variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
  sensitive   = true
}

variable "tenant_id" {
  description = "Azure tenant ID"
  type        = string
  sensitive   = true
}

variable "resource_group_name" {
  description = "Azure resource group name"
  type        = string
  default     = "rg-eventhub"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "app_service_plan_name" {
  description = "Linux App Service plan name"
  type        = string
  default     = "plan-eventhub"
}

variable "app_service_plan_sku" {
  description = "App Service plan SKU"
  type        = string
  default     = "B1"
}

variable "app_name" {
  description = "Globally unique Azure Web App name"
  type        = string
}

variable "python_version" {
  description = "Python runtime version"
  type        = string
  default     = "3.12"
}

variable "django_secret_key" {
  description = "Django secret key stored as an App Service setting"
  type        = string
  sensitive   = true
}

variable "allowed_hosts" {
  description = "Comma-separated Django allowed hosts"
  type        = string
  default     = "*"
}
