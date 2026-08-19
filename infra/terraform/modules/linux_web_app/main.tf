resource "azurerm_linux_web_app" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  service_plan_id     = var.service_plan_id
  https_only          = true

  site_config {
    always_on              = true
    minimum_tls_version    = "1.2"
    ftps_state             = "Disabled"
    app_command_line       = "python manage.py migrate --noinput && gunicorn --bind=0.0.0.0 --timeout 600 eventhub.wsgi"

    application_stack {
      python_version = var.python_version
    }
  }

  app_settings = {
    SCM_DO_BUILD_DURING_DEPLOYMENT = "1"
    DJANGO_SECRET_KEY              = var.django_secret_key
    DJANGO_ALLOWED_HOSTS           = var.allowed_hosts
    DJANGO_DEBUG                   = "False"
  }
}

output "name" {
  value = azurerm_linux_web_app.this.name
}

output "default_hostname" {
  value = azurerm_linux_web_app.this.default_hostname
}
