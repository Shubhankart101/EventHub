# Pipeline troubleshooting guide

This guide explains what should run for each kind of EventHub change and how to recover when a workflow fails. Workflow paths are relative to the repository root.

## Quick decision table

| Change set | Automatic behavior | Manual workflow |
| --- | --- | --- |
| Python, Django, API, or migration code | Pull request and main push validation runs | `app-deploy.yml` for a full build and deployment |
| Only Markdown documentation | Path-filtered validation is skipped | Run a workflow manually if validation is needed |
| Code plus Markdown | Validation runs because code changed | Use the normal application workflow sequence |
| Terraform infrastructure | No automatic infrastructure apply | `azure-deploy.yml` with `plan` or `apply` |
| Pipeline tracker or workflow files | Workflow behavior may need a manual run | `publish-status-board.yml` or the affected workflow |

## Code changes

### Workflow does not start

Check that the pull request targets `main`, the workflow is enabled, and the change is not Markdown-only. A commit containing both code and Markdown still runs the code workflow.

### Dependency installation fails

Reproduce locally:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Check package compatibility and retry after transient package-index failures.

### Django check or migration check fails

Run:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
```

Review imports, settings, URL routes, and whether a model change requires a committed migration.

### Swagger schema validation fails

Run:

```powershell
python manage.py spectacular --validate
```

Confirm `drf_spectacular` is installed, `DEFAULT_SCHEMA_CLASS` is configured, and computed serializer fields have schema annotations when required.

### Reservation behavior is rejected

Verify the event exists, has `upcoming` or `ongoing` status, and has enough `available_seats`. A cancelled reservation cannot be cancelled twice.

## Azure deployment

### Terraform authentication fails

Confirm the selected GitHub environment contains `AZURE_SUBSCRIPTION_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET`. Check that the service principal has permission to create or update the target resource group and App Service resources.

### Terraform plan fails

Install Terraform 1.8.5 locally and run from `infra/terraform`:

```powershell
terraform fmt -recursive
terraform init
terraform validate
terraform plan
```

Review module paths, provider initialization, variable values, and Azure naming constraints.

### Terraform proposes unexpected replacement

Stop before applying. Compare the plan with the intended change, inspect Azure for drift, and confirm that resource names and locations have not changed accidentally.

### App deployment fails

Check `AZURE_WEBAPP_NAME` and `AZURE_PUBLISH_PROFILE`, confirm the publish profile belongs to the same Web App, and inspect the Azure deployment log. The app startup command runs migrations before Gunicorn.

### App starts but returns a host or secret error

Set `DJANGO_ALLOWED_HOSTS` to the Web App hostname and set a strong `DJANGO_SECRET_KEY`. Keep `DJANGO_DEBUG` set to `False` in hosted environments.

## GitHub Pages status board

### Publisher fails at `configure-pages`

Open repository **Settings → Pages**, select **GitHub Actions** as the source, save, and rerun [publish-status-board.yml](../.github/workflows/publish-status-board.yml).

### Board shows no runs

Run the publisher once so it creates `status-data.json` in the published artifact. The board uses the authenticated snapshot generated during the workflow and does not expose a personal access token in browser code.

### Board is stale

The publisher is manual-only. Run it again after workflow or tracker changes. Open the GitHub Actions run link shown by the publisher if the artifact upload or Pages deployment failed.

## Local verification checklist

```powershell
python -m compileall -q eventhub events manage.py
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py spectacular --validate
python manage.py test
```

Start the API and verify:

- `http://127.0.0.1:8000/api/docs/`
- `http://127.0.0.1:8000/api/schema/`
- `http://127.0.0.1:8000/api/events/`
- `http://127.0.0.1:8000/api/reservations/`
