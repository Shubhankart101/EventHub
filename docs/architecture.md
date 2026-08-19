# Architecture

<img src="assets/atg-studiocapa.gif" width="560" alt="EventHub architecture review">

## Project structure

The core Django application follows this structure:

```text
eventhub/
├── manage.py
├── eventhub/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py              # Required by Gunicorn/Azure hosting
├── events/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── middleware.py
│   └── migrations/
├── db.sqlite3
└── requirements.txt
```

The repository also contains operational documentation and hosting files outside this core application tree:

```text
├── .github/workflows/     # CI, deployment, Terraform, and Pages workflows
├── docs/                  # Setup, API, architecture, and troubleshooting guides
├── infra/terraform/       # Modular Azure App Service infrastructure
└── pipeline-tracker/      # Static GitHub Actions run viewer
```

## Request flow

1. `eventhub/urls.py` mounts the API under `/api/` and exposes Swagger UI and the OpenAPI schema.
2. `events/urls.py` registers `EventViewSet` and `ReservationViewSet` with `DefaultRouter`.
3. ViewSets select and filter model querysets from request query parameters.
4. DRF serializers validate incoming data and shape responses.
5. Reservation creation locks the event row, verifies current availability, deducts seats, and creates the reservation inside one transaction.
6. Reservation cancellation locks both records, restores seats, and marks the reservation cancelled inside one transaction.
7. `RequestLoggingMiddleware` records method, path, HTTP status, and request duration.

## Data model

`Event` has many `Reservation` records through the `reservations` related name. Deleting an event cascades to its reservations.

- `Event`: title, venue, date, total seats, available seats, status, creation time
- `Reservation`: event, attendee name, attendee email, seats reserved, status, creation time

Events are ordered by date. Reservations are ordered newest first.

## Seat consistency

The reservation serializer uses `transaction.atomic()` and `select_for_update()` so concurrent requests do not both spend the same available seats. Cancellation uses the same transaction and row-locking approach to prevent a reservation from refunding its seats twice.

<img src="assets/eyebrow-raise-dwight.gif" width="560" alt="Review seat consistency carefully">

## Validation rules

- `available_seats` cannot exceed `total_seats`.
- Reservations require at least one seat.
- Reservations are allowed only for `upcoming` and `ongoing` events.
- Requested seats cannot exceed current availability.
- A cancelled reservation cannot be cancelled again.
- `reservations_count` includes confirmed reservations only.

## Runtime configuration

Development defaults are defined in `eventhub/settings.py`. Hosted deployments provide `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, and `DJANGO_ALLOWED_HOSTS` through Azure App Service settings.
