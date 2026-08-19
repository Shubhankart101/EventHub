module "resource_group" {
  source   = "./modules/resource_group"
  name     = var.resource_group_name
  location = var.location
}

module "service_plan" {
  source              = "./modules/service_plan"
  name                = var.app_service_plan_name
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name
  sku_name            = var.app_service_plan_sku
}

module "linux_web_app" {
  source              = "./modules/linux_web_app"
  name                = var.app_name
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name
  service_plan_id     = module.service_plan.id
  python_version      = var.python_version
  django_secret_key   = var.django_secret_key
  allowed_hosts       = var.allowed_hosts
}
