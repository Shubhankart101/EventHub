# EventHub

EventHub is a Django REST Framework ticketing API for browsing events, reserving seats, and cancelling reservations. It includes Swagger-based endpoint testing, transaction-safe seat updates, manual GitHub Actions pipelines, modular Azure infrastructure, and a GitHub Pages pipeline tracker.

<p align="center"><a href="eventhub/urls.py">API routes and Swagger entrypoints</a></p>
<p align="center"><a href=".github/workflows/terraform.yml">Reusable Terraform template</a></p>
<p align="center"><a href=".github/workflows/publish-status-board.yml">Publish pipeline status board</a></p>

## The EventHub lifecycle

### 1. Validate application changes

<p><strong><a href=".github/workflows/pull-request-tests.yml">Pull Request Tests</a></strong> install dependencies, compile Python, run Django checks, verify migrations, and execute the test command.</p>
<p><img src="docs/assets/office.gif" width="560" alt="Pipeline checks in progress"></p>

### 2. Test the API interactively

<p><strong><a href="docs/api.md">API Reference</a></strong> documents Event and Reservation routes, while Swagger UI at <code>/api/docs/</code> lets you execute requests from the browser.</p>
<p><img src="docs/assets/devtrack-code-loop.gif" width="560" alt="API development workflow"></p>

### 3. Provision hosting

<p><strong><a href=".github/workflows/azure-deploy.yml">Provision Azure App Service</a></strong> runs the modular Terraform plan or apply workflow.</p>
<p><img src="docs/assets/eyebrow-raise-dwight.gif" width="560" alt="Review infrastructure plan carefully"></p>

### 4. Build and deploy

<p><strong><a href=".github/workflows/app-deploy.yml">Build, Check, and Deploy EventHub</a></strong> validates the source and deploys it to Azure Linux Web App.</p>
<p><img src="docs/assets/great-job.gif" width="560" alt="Successful application deployment"></p>

### 5. Track pipeline runs

<p><strong><a href=".github/workflows/publish-status-board.yml">Publish Pipeline Status Board</a></strong> publishes the latest GitHub Actions snapshot to GitHub Pages.</p>
<p><img src="docs/assets/pipeline-success.gif" width="560" alt="Successful pipeline status"></p>

## Contents

| Section | Description |
| --- | --- |
| [Quick start](#quick-start) | Install dependencies, run checks, and start the API |
| [Interactive API docs](#interactive-api-docs) | Test endpoints through Swagger UI |
| [Project structure](#project-structure) | Understand the Django application and operational directories |
| [Application pipelines](#application-pipelines) | Understand validation and deployment workflows |
| [Documentation](#documentation) | Find setup, API, architecture, deployment, and troubleshooting guides |

## Quick start

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3 -m pip install -r requirements.txt
py -3 manage.py migrate
py -3 manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`.

Run the same checks used by CI:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py spectacular --validate
python manage.py test
```

The repository currently has no committed test module, so the test command reports zero discovered tests.

## Project structure

The core application follows the requested Django layout:

```text
eventhub/
├── manage.py
├── eventhub/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
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

CI/CD workflows, detailed guides, Terraform modules, and the pipeline tracker live in `.github/`, `docs/`, `infra/`, and `pipeline-tracker/`.

## Interactive API docs

Open `http://127.0.0.1:8000/api/docs/`, select **Try it out**, provide request data, and choose **Execute**. The raw OpenAPI document is available at `http://127.0.0.1:8000/api/schema/`.

## Endpoints

### Event Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/events/` | List all events |
| POST | `/api/events/` | Create event |
| GET | `/api/events/{id}/` | Get single event |
| PUT | `/api/events/{id}/` | Update event |
| PATCH | `/api/events/{id}/` | Partially update event |
| DELETE | `/api/events/{id}/` | Delete event |
| GET | `/api/events/?status=upcoming` | Filter by status |
| GET | `/api/events/?venue=mumbai` | Filter by venue |

![Event endpoints](https://space-mycohort-web.sgp1.digitaloceanspaces.com/2026/04/01/EFKYJBEXSNXBL4RT.png)

### Reservation Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/reservations/` | List all reservations |
| POST | `/api/reservations/` | Create reservation |
| GET | `/api/reservations/{id}/` | Get single reservation |
| PUT | `/api/reservations/{id}/` | Update reservation |
| PATCH | `/api/reservations/{id}/` | Partially update reservation |
| GET | `/api/reservations/?event_id=1` | Filter by event |
| POST | `/api/reservations/{id}/cancel/` | Cancel reservation |

![Reservation endpoints](https://space-mycohort-web.sgp1.digitaloceanspaces.com/2026/04/01/ME9ZKJ2Q7W6OH1RF.png)

Filter events with `?status=upcoming` and/or `?venue=hall`. Filter reservations with `?event_id=1`.

Seat deductions and refunds run inside database transactions with row locking to prevent overbooking and double refunds.

## Application pipelines

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| [Pull Request Tests](.github/workflows/pull-request-tests.yml) | Pull requests and pushes to `main`, excluding Markdown-only changes | Runs compilation, Django checks, migration checks, and the test command |
| [Build, Check, and Deploy EventHub](.github/workflows/app-deploy.yml) | Manual | Validates and deploys the Django package to Azure Web App |
| [Provision Azure App Service](.github/workflows/azure-deploy.yml) | Manual | Plans or applies Azure hosting infrastructure |
| [Publish Pipeline Status Board](.github/workflows/publish-status-board.yml) | Manual | Publishes recent Actions runs to GitHub Pages |

The current repository does not include a committed test module, so the test command currently discovers zero tests. Add focused API tests before treating a green run as full behavioral coverage.

## Documentation

| Topic | File |
| --- | --- |
| Local setup and troubleshooting | [docs/setup.md](docs/setup.md) |
| API reference, Swagger, and curl examples | [docs/api.md](docs/api.md) |
| Request/response JSON examples | [docs/api-testing-examples.md](docs/api-testing-examples.md) |
| Data model and request flow | [docs/architecture.md](docs/architecture.md) |
| Deployment, pipelines, and secrets | [docs/deployment.md](docs/deployment.md) |
| Pipeline troubleshooting and mitigation | [Troubleshooting](#troubleshooting) |
| Pipeline status board | [docs/status-board.md](docs/status-board.md) |

## CI/CD and Hosting

The repository includes manual GitHub Actions workflows for pull request checks, Azure App Service provisioning, application deployment, and publishing the pipeline status board. See [infra/terraform/README.md](infra/terraform/README.md) for Azure setup and [docs/status-board.md](docs/status-board.md) for the tracker.

The hosting workflow provisions a Linux Azure Web App and starts Django with Gunicorn after applying migrations. Configure the required GitHub environment secrets before running an `apply` or deployment workflow.

## Troubleshooting

This section covers the common failure modes for EventHub changes and pipeline runs.

<img src="docs/assets/office.gif" width="560" alt="Pipeline troubleshooting">

### Quick decision table

| Change set | Automatic behavior | Manual workflow |
| --- | --- | --- |
| Python, Django, API, or migration code | Pull request and main push validation runs | `app-deploy.yml` for a full build and deployment |
| Only Markdown documentation | Path-filtered validation is skipped | Run a workflow manually if validation is needed |
| Code plus Markdown | Validation runs because code changed | Use the normal application workflow sequence |
| Terraform infrastructure | No automatic infrastructure apply | `azure-deploy.yml` with `plan` or `apply` |
| Pipeline tracker or workflow files | Workflow behavior may need a manual run | `publish-status-board.yml` or the affected workflow |

### Workflow does not start

<img src="docs/assets/pipeline-queued.gif" width="560" alt="Pipeline queued">

Check that the pull request targets `main`, the workflow is enabled, and the change is not Markdown-only. A commit containing both code and Markdown still runs the code workflow.

### Dependency, Django, or schema checks fail

Reproduce locally:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py spectacular --validate
```

Review imports, settings, URL routes, migrations, and OpenAPI serializer annotations.

<img src="docs/assets/bounce-dwight.gif" width="560" alt="Pipeline work in progress">

### Reservation behavior is rejected

Verify that the event exists, has `upcoming` or `ongoing` status, and has enough `available_seats`. A cancelled reservation cannot be cancelled twice.

### Terraform plan fails

<img src="docs/assets/eyebrow-raise-dwight.gif" width="560" alt="Review Terraform plan">

Run from `infra/terraform`:

```powershell
terraform fmt -recursive
terraform init
terraform validate
terraform plan
```

Confirm the Azure secrets exist in the selected GitHub environment and review the plan before applying it.

### App deployment fails

Check `AZURE_WEBAPP_NAME` and `AZURE_PUBLISH_PROFILE`, confirm the publish profile belongs to the same Web App, and inspect Azure deployment logs. The startup command runs migrations before Gunicorn.

<img src="docs/assets/tired-office.gif" width="560" alt="Inspect runtime logs when deployment fails">

### Pipeline board is stale or empty

The publisher is manual-only. Run `Publish Pipeline Status Board` again and confirm GitHub Pages uses **GitHub Actions** as its source. The workflow requests Pages enablement automatically; if `configure-pages` still reports `Get Pages site failed`, a repository administrator must enable Pages once under **Settings → Pages**. The workflow must generate `status-data.json` and copy `pipeline-tracker/index.html` plus `docs/assets/` into the Pages artifact.

<img src="docs/assets/pipeline-running.gif" width="560" alt="Pipeline status is still running">

## Tests

```powershell
py -3 manage.py test
```
