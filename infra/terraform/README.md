# EventHub Azure Infrastructure

This Terraform stack provisions the basic Azure hosting layer used by EventHub:

- Resource group
- Linux App Service plan
- Python Linux Web App

The Web App runs `manage.py migrate` before starting Gunicorn. Terraform state is local by default; use an Azure Storage backend before sharing state across operators.

## GitHub secrets

Configure these secrets on the `dev` GitHub environment before running the workflow:

- `AZURE_SUBSCRIPTION_ID`
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_WEBAPP_NAME`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`

The deploy workflow additionally needs `AZURE_PUBLISH_PROFILE`.

## Provisioning

1. Run `Provision Azure App Service` with `terraform_action=plan`.
2. Review the Terraform plan in the Actions log.
3. Run it again with `terraform_action=apply`.
4. Run `Build, Check, and Deploy EventHub` after the Web App exists.

For local use, copy `terraform.tfvars.example` to `terraform.tfvars`, fill in the values, then run:

```powershell
terraform init
terraform plan
terraform apply
```
