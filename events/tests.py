import threading
import time
from datetime import date
from unittest import mock

from django.db import connection
from django.test import TransactionTestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Event, Reservation


def make_event(**overrides):
    fields = {
        'title': 'PyCon',
        'venue': 'Main Hall',
        'date': date(2026, 12, 1),
        'total_seats': 10,
        'available_seats': 10,
        'status': 'upcoming',
    }
    fields.update(overrides)
    return Event.objects.create(**fields)


def reservation_payload(event, seats=1, name='Ada'):
    return {
        'event': event.pk,
        'attendee_name': name,
        'attendee_email': f'{name.lower()}@example.com',
        'seats_reserved': seats,
    }


class EventApiTests(APITestCase):
    def test_list_filters_by_status_and_venue(self):
        make_event(title='A', venue='Main Hall')
        make_event(title='B', venue='Side Room', status='cancelled')

        response = self.client.get('/api/events/', {'status': 'cancelled'})
        self.assertEqual([e['title'] for e in response.json()], ['B'])

        response = self.client.get('/api/events/', {'venue': 'main'})
        self.assertEqual([e['title'] for e in response.json()], ['A'])

    def test_create_rejects_available_above_total(self):
        response = self.client.post('/api/events/', {
            'title': 'X', 'venue': 'Y', 'date': '2026-12-01',
            'total_seats': 5, 'available_seats': 6,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('available_seats', response.json())

    def test_reservations_count_only_counts_confirmed(self):
        event = make_event()
        Reservation.objects.create(event=event, attendee_name='A', attendee_email='a@x.com', seats_reserved=1)
        Reservation.objects.create(
            event=event, attendee_name='B', attendee_email='b@x.com', seats_reserved=1, status='cancelled'
        )
        response = self.client.get(f'/api/events/{event.pk}/')
        self.assertEqual(response.json()['reservations_count'], 1)


class ReservationApiTests(APITestCase):
    def test_reserve_decrements_available_seats(self):
        event = make_event(available_seats=10)
        response = self.client.post('/api/reservations/', reservation_payload(event, seats=3))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['status'], 'confirmed')
        event.refresh_from_db()
        self.assertEqual(event.available_seats, 7)

    def test_reserve_more_than_available_is_rejected(self):
        event = make_event(available_seats=2)
        response = self.client.post('/api/reservations/', reservation_payload(event, seats=3))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        event.refresh_from_db()
        self.assertEqual(event.available_seats, 2)
        self.assertFalse(Reservation.objects.exists())

    def test_reserve_zero_seats_is_rejected(self):
        event = make_event()
        response = self.client.post('/api/reservations/', reservation_payload(event, seats=0))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reserve_for_inactive_event_is_rejected(self):
        for event_status in ('completed', 'cancelled'):
            event = make_event(status=event_status)
            response = self.client.post('/api/reservations/', reservation_payload(event))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, event_status)
        self.assertFalse(Reservation.objects.exists())

    def test_cancel_restores_seats_once(self):
        event = make_event(available_seats=10)
        reservation_id = self.client.post(
            '/api/reservations/', reservation_payload(event, seats=4)
        ).json()['id']

        response = self.client.post(f'/api/reservations/{reservation_id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'cancelled')
        event.refresh_from_db()
        self.assertEqual(event.available_seats, 10)

        response = self.client.post(f'/api/reservations/{reservation_id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        event.refresh_from_db()
        self.assertEqual(event.available_seats, 10)

    def test_list_filters_by_event_id(self):
        first, second = make_event(), make_event(title='Other')
        self.client.post('/api/reservations/', reservation_payload(first, name='Ada'))
        self.client.post('/api/reservations/', reservation_payload(second, name='Bob'))

        response = self.client.get('/api/reservations/', {'event_id': first.pk})
        self.assertEqual([r['attendee_name'] for r in response.json()], ['Ada'])


class ConcurrentReservationTests(TransactionTestCase):
    """Real threads and real commits, so row locking is exercised end to end."""

    def _run_concurrently(self, requests):
        barrier = threading.Barrier(len(requests))
        results = [None] * len(requests)

        def worker(index, path):
            try:
                barrier.wait()
                results[index] = APIClient().post(path, requests[index][1]).status_code
            except Exception as exc:  # surface DB errors (e.g. "database is locked") as failures
                results[index] = repr(exc)
            finally:
                connection.close()

        threads = [threading.Thread(target=worker, args=(i, path)) for i, (path, _) in enumerate(requests)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)
        return results

    def _slow_event_save(self):
        # Widen the read-then-write window so an unlocked implementation would overbook.
        original_save = Event.save

        def slow_save(instance, *args, **kwargs):
            time.sleep(0.3)
            return original_save(instance, *args, **kwargs)

        return mock.patch.object(Event, 'save', slow_save)

    def test_two_simultaneous_bookings_cannot_share_the_last_seats(self):
        event = make_event(total_seats=3, available_seats=3)
        payloads = [reservation_payload(event, seats=2, name=n) for n in ('Ada', 'Bob')]

        with self._slow_event_save():
            results = self._run_concurrently([('/api/reservations/', p) for p in payloads])

        self.assertCountEqual(results, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
        event.refresh_from_db()
        self.assertEqual(event.available_seats, 1)
        self.assertEqual(Reservation.objects.filter(event=event, status='confirmed').count(), 1)

    def test_simultaneous_cancels_refund_seats_once(self):
        event = make_event(total_seats=5, available_seats=1)
        reservation = Reservation.objects.create(
            event=event, attendee_name='Ada', attendee_email='ada@example.com', seats_reserved=4
        )
        path = f'/api/reservations/{reservation.pk}/cancel/'

        with self._slow_event_save():
            results = self._run_concurrently([(path, {}), (path, {})])

        self.assertCountEqual(results, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
        event.refresh_from_db()
        self.assertEqual(event.available_seats, 5)
