output "resource_group_name" {
  value = module.resource_group.name
}

output "web_app_name" {
  value = module.linux_web_app.name
}

output "web_app_url" {
  value = "https://${module.linux_web_app.default_hostname}"
}
