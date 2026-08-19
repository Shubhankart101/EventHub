variable "name" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "service_plan_id" {
  type = string
}

variable "python_version" {
  type = string
}

variable "django_secret_key" {
  type      = string
  sensitive = true
}

variable "allowed_hosts" {
  type = string
}
