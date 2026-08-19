# Deployment

<img src="assets/hell-yeah-yeah.gif" width="560" alt="Deployment ready to run">

EventHub uses manual GitHub Actions workflows and modular Terraform to host the Django API on Azure Linux App Service. The pipeline status board is published separately through GitHub Pages.

## Application pipelines

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| [Pull Request Tests](../.github/workflows/pull-request-tests.yml) | Pull requests to `main` and pushes to `main`, excluding Markdown-only changes | Installs dependencies, compiles Python, runs Django checks, verifies migrations, and runs the test command |
| [Build, Check, and Deploy EventHub](../.github/workflows/app-deploy.yml) | Manual | Repeats application validation and deploys the package to Azure Web App |
| [Publish Pipeline Status Board](../.github/workflows/publish-status-board.yml) | Manual | Captures recent Actions runs and publishes the tracker to GitHub Pages |

The current repository does not include a committed test module, so the application workflows currently execute Django's test command with zero discovered tests. Add tests before treating a green run as full behavioral coverage.

## Infrastructure pipeline

| Workflow | Purpose |
| --- | --- |
| [Provision Azure App Service](../.github/workflows/azure-deploy.yml) | Manually runs Terraform `plan` or `apply` for the Azure resource group, Linux App Service plan, and Web App |
| [Terraform Template](../.github/workflows/terraform.yml) | Reusable workflow used by the Azure infrastructure entrypoint |

## Recommended order

1. Configure the GitHub `dev` environment secrets.
2. Run **Provision Azure App Service** with `terraform_action=plan`.
3. Review the Terraform plan.
4. Run the same workflow with `terraform_action=apply`.
5. Run **Build, Check, and Deploy EventHub** and provide the Azure Web App name if it is not stored as a secret.
6. Run **Publish Pipeline Status Board** after enabling GitHub Pages with **GitHub Actions** as its source.

<img src="assets/crazy-dance-funny-dance.gif" width="560" alt="Deployment complete">

## Required secrets

| Secret | Purpose |
| --- | --- |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription used by Terraform |
| `AZURE_TENANT_ID` | Microsoft Entra tenant used by Terraform |
| `AZURE_CLIENT_ID` | Service principal client ID |
| `AZURE_CLIENT_SECRET` | Service principal client secret |
| `AZURE_WEBAPP_NAME` | Globally unique Azure Web App name |
| `AZURE_PUBLISH_PROFILE` | Azure Web App publish profile for application deployment |
| `DJANGO_SECRET_KEY` | Production Django secret key |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated Azure and custom hostnames |

## Terraform structure

```text
infra/terraform/                 # Terraform root
├── modules/resource_group/      # Azure resource group
├── modules/service_plan/        # Linux App Service plan
├── modules/linux_web_app/       # Python Web App and settings
├── main.tf
├── variables.tf
├── outputs.tf
└── terraform.tfvars.example
```

See [infra/terraform/README.md](../infra/terraform/README.md) for local Terraform commands and secret setup.

## App runtime

Azure App Service runs:

```text
python manage.py migrate --noinput && gunicorn --bind=0.0.0.0 --timeout 600 eventhub.wsgi
```

The deployment package includes `requirements.txt`; Azure build automation installs the Python dependencies. HTTPS-only access is enabled by Terraform.

<img src="assets/tired-office.gif" width="560" alt="Inspect runtime logs when deployment fails">

## Branch protection

Configure `main` to require pull requests and the `Pull Request Tests / test` status check. The workflow cannot enforce branch protection by itself.

## Pipeline GIF gallery

<img src="assets/the-office-the-office-memes.gif" width="560" alt="Pipeline reaction">

<img src="assets/pond-naravit-ppnaravit.gif" width="560" alt="Unexpected pipeline result">

<img src="assets/thats-what-she-said-what-she-said.gif" width="560" alt="Pipeline review reaction">

<img src="assets/the-office-the-office-memes.gif" width="560" alt="Pipeline team reaction">

<img src="assets/pipeline-queued.gif" width="560" alt="Pipeline queued">

<img src="assets/pipeline-running.gif" width="560" alt="Pipeline running">

<img src="assets/pipeline-success.gif" width="560" alt="Pipeline passed">
