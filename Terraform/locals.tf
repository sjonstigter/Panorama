locals {
  policy_files = fileset("${path.module}/policies", "*.yaml")

  policies = {
    for f in local.policy_files :
    trimsuffix(basename(f), ".yaml") => yamldecode(file("${path.module}/policies/${f}"))
  }

  services_config = yamldecode(file("${path.module}/services.yaml"))
  services = {
    for svc in local.services_config.services : svc.name => svc
  }

  address_objects_config = yamldecode(file("${path.module}/address_objects.yaml"))
  address_objects = {
    for obj in local.address_objects_config.address_objects : obj.name => obj
  }
}
