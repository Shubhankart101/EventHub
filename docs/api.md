# API reference

Base URL: `http://127.0.0.1:8000/api/`

Interactive documentation is available at [`/api/docs/`](http://127.0.0.1:8000/api/docs/). The machine-readable schema is available at [`/api/schema/`](http://127.0.0.1:8000/api/schema/).

## Event endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/events/` | List all events |
| POST | `/api/events/` | Create an event |
| GET | `/api/events/{id}/` | Retrieve one event |
| PUT | `/api/events/{id}/` | Replace an event |
| PATCH | `/api/events/{id}/` | Partially update an event |
| DELETE | `/api/events/{id}/` | Delete an event |
| GET | `/api/events/?status=upcoming` | Filter events by status |
| GET | `/api/events/?venue=mumbai` | Filter events by venue, case-insensitive |

![Event endpoints](https://space-mycohort-web.sgp1.digitaloceanspaces.com/2026/04/01/EFKYJBEXSNXBL4RT.png)

### Event request body

```json
{
  "title": "PyCon India 2026",
  "venue": "Bangalore Convention Centre",
  "date": "2026-09-20",
  "total_seats": 500,
  "available_seats": 500,
  "status": "upcoming"
}
```

Supported statuses are `upcoming`, `ongoing`, `completed`, and `cancelled`.

The response includes `reservations_count`, which counts confirmed reservations only. `created_at` and `reservations_count` are read-only.

## Reservation endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/reservations/` | List all reservations |
| POST | `/api/reservations/` | Create a reservation |
| GET | `/api/reservations/{id}/` | Retrieve one reservation |
| PUT | `/api/reservations/{id}/` | Replace a reservation |
| PATCH | `/api/reservations/{id}/` | Partially update a reservation |
| DELETE | `/api/reservations/{id}/` | Delete a reservation |
| GET | `/api/reservations/?event_id=1` | Filter reservations by event |
| POST | `/api/reservations/{id}/cancel/` | Cancel a confirmed reservation and restore its seats |

![Reservation endpoints](https://space-mycohort-web.sgp1.digitaloceanspaces.com/2026/04/01/ME9ZKJ2Q7W6OH1RF.png)

### Reservation request body

```json
{
  "event": 1,
  "attendee_name": "Priya Sharma",
  "attendee_email": "priya@example.com",
  "seats_reserved": 2
}
```

Supported reservation statuses are `confirmed` and `cancelled`. The API sets the status on creation and exposes `created_at` as read-only.

## Validation and responses

- `201 Created` indicates a successful event or reservation creation.
- `400 Bad Request` indicates invalid fields, an unavailable event, insufficient seats, or an already cancelled reservation.
- `404 Not Found` indicates that the event or reservation ID does not exist.
- `204 No Content` is returned by successful DELETE operations.

Reservations require at least one seat, an `upcoming` or `ongoing` event, and enough available seats. Events reject `available_seats` values greater than `total_seats`.

## Example curl requests

```bash
# List upcoming events at a venue
curl "http://127.0.0.1:8000/api/events/?status=upcoming&venue=mumbai"

# Create an event
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{"title":"PyCon India 2026","venue":"Bangalore Convention Centre","date":"2026-09-20","total_seats":500,"available_seats":500,"status":"upcoming"}'

# Reserve seats
curl -X POST http://127.0.0.1:8000/api/reservations/ \
  -H "Content-Type: application/json" \
  -d '{"event":1,"attendee_name":"Priya Sharma","attendee_email":"priya@example.com","seats_reserved":2}'

# Cancel a reservation
curl -X POST http://127.0.0.1:8000/api/reservations/1/cancel/
```

## Pipeline verification

After changing an endpoint, run `python manage.py check`, inspect the OpenAPI schema, and use the [pipeline status board](status-board.md) to review the related GitHub Actions run.
