# API testing examples

This guide shows what to enter in the JSON request body for each Swagger operation and what response to expect.

## Start the API

```powershell
python manage.py runserver
```

Open Swagger UI at `http://127.0.0.1:8000/api/docs/`, select **Try it out**, enter the JSON body shown below, and select **Execute**. The examples use event ID `1` and reservation ID `1`.

## Event API

### Create event: `POST /api/events/`

Request body:

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

Expected response: `201 Created`

```json
{
  "id": 1,
  "title": "PyCon India 2026",
  "venue": "Bangalore Convention Centre",
  "date": "2026-09-20",
  "total_seats": 500,
  "available_seats": 500,
  "status": "upcoming",
  "created_at": "2026-08-19T10:00:00Z",
  "reservations_count": 0
}
```

### List events: `GET /api/events/`

Request body: none.

Expected response: `200 OK`

```json
[
  {
    "id": 1,
    "title": "PyCon India 2026",
    "venue": "Bangalore Convention Centre",
    "date": "2026-09-20",
    "total_seats": 500,
    "available_seats": 500,
    "status": "upcoming",
    "created_at": "2026-08-19T10:00:00Z",
    "reservations_count": 0
  }
]
```

### Get one event: `GET /api/events/{id}/`

Example URL: `/api/events/1/`

Request body: none.

Expected response: `200 OK`, one event object in the same shape as the create response.

### Filter events: `GET /api/events/?status=upcoming`

Request body: none. Add the query parameter in the Swagger request URL.

Example URL: `/api/events/?status=upcoming`

Expected response: `200 OK`, an array containing only upcoming events.

### Filter events: `GET /api/events/?venue=mumbai`

Request body: none. The venue filter is case-insensitive.

Example URL: `/api/events/?venue=mumbai`

Expected response: `200 OK`, an array containing events whose venue contains `mumbai`.

### Replace an event: `PUT /api/events/{id}/`

Example URL: `/api/events/1/`

Request body: send all writable event fields.

```json
{
  "title": "PyCon India 2026",
  "venue": "Mumbai Convention Centre",
  "date": "2026-09-20",
  "total_seats": 500,
  "available_seats": 500,
  "status": "upcoming"
}
```

Expected response: `200 OK`, the updated event object.

### Partially update an event: `PATCH /api/events/{id}/`

Example URL: `/api/events/1/`

Request body: send only the field to change.

```json
{
  "venue": "Mumbai Convention Centre"
}
```

Expected response: `200 OK`, the updated event object.

### Delete an event: `DELETE /api/events/{id}/`

Example URL: `/api/events/1/`

Request body: none.

Expected response: `204 No Content`.

## Reservation API

### Create reservation: `POST /api/reservations/`

Create the event first, then use its returned ID in the `event` field.

Request body:

```json
{
  "event": 1,
  "attendee_name": "Priya Sharma",
  "attendee_email": "priya@example.com",
  "seats_reserved": 2
}
```

Expected response: `201 Created`. The event's `available_seats` decreases by `2`.

```json
{
  "id": 1,
  "event": 1,
  "attendee_name": "Priya Sharma",
  "attendee_email": "priya@example.com",
  "seats_reserved": 2,
  "status": "confirmed",
  "created_at": "2026-08-19T10:05:00Z"
}
```

### List reservations: `GET /api/reservations/`

Request body: none.

Expected response: `200 OK`, an array of reservation objects.

### Get one reservation: `GET /api/reservations/{id}/`

Example URL: `/api/reservations/1/`

Request body: none.

Expected response: `200 OK`, one reservation object.

### Filter reservations: `GET /api/reservations/?event_id=1`

Request body: none. Add the query parameter in the Swagger request URL.

Example URL: `/api/reservations/?event_id=1`

Expected response: `200 OK`, an array containing reservations for event `1`.

### Replace a reservation: `PUT /api/reservations/{id}/`

Example URL: `/api/reservations/1/`

Request body: send the writable reservation fields. `status` and `created_at` are read-only.

```json
{
  "event": 1,
  "attendee_name": "Priya S. Sharma",
  "attendee_email": "priya@example.com",
  "seats_reserved": 2
}
```

Expected response: `200 OK`, the updated reservation object.

### Partially update a reservation: `PATCH /api/reservations/{id}/`

Example URL: `/api/reservations/1/`

Request body:

```json
{
  "attendee_name": "Priya S. Sharma"
}
```

Expected response: `200 OK`, the updated reservation object.

### Delete a reservation: `DELETE /api/reservations/{id}/`

Example URL: `/api/reservations/1/`

Request body: none.

Expected response: `204 No Content`.

### Cancel reservation: `POST /api/reservations/{id}/cancel/`

Example URL: `/api/reservations/1/cancel/`

Request body: none.

Expected response: `200 OK`. The reservation becomes cancelled and its seats are returned to the event.

```json
{
  "id": 1,
  "event": 1,
  "attendee_name": "Priya S. Sharma",
  "attendee_email": "priya@example.com",
  "seats_reserved": 2,
  "status": "cancelled",
  "created_at": "2026-08-19T10:05:00Z"
}
```

Calling the cancel endpoint again returns `400 Bad Request`:

```json
{
  "error": "Already cancelled."
}
```

## Common validation examples

### Not enough seats: `POST /api/reservations/`

Request body:

```json
{
  "event": 1,
  "attendee_name": "Alex Kumar",
  "attendee_email": "alex@example.com",
  "seats_reserved": 9999
}
```

Expected response: `400 Bad Request`.

```json
{
  "non_field_errors": [
    "Only 0 seat(s) available."
  ]
}
```

### Invalid event capacity: `POST /api/events/`

Request body:

```json
{
  "title": "Invalid Event",
  "venue": "Hall A",
  "date": "2026-09-20",
  "total_seats": 10,
  "available_seats": 20,
  "status": "upcoming"
}
```

Expected response: `400 Bad Request` because `available_seats` cannot exceed `total_seats`.
