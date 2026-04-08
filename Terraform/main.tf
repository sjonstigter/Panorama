resource "panos_panorama_service_object" "services" {
  for_each = local.services

  name             = each.value.name
  protocol         = each.value.protocol
  description      = try(each.value.description, null)
  destination_port = each.value.destination_port

  lifecycle {
    create_before_destroy = true
  }
}

locals {
  service_map = merge(
    {
      "any" = "any"
    },
    {
      for name, svc in panos_panorama_service_object.services : name => svc.name
    }
  )
}

resource "panos_address_object" "address_objects" {
  for_each = local.address_objects

  name        = each.value.name
  type        = try(each.value.type, "ip-netmask")
  value       = each.value.value
  description = try(each.value.description, null)

  lifecycle {
    create_before_destroy = true
  }
}

module "policy_apps" {
  for_each = local.policies

  source = "./modules/policy_app"

  rulebase         = var.rulebase
  position_keyword = try(each.value.position_keyword, "bottom")
  group_tag        = each.value.group_tag

  rules       = each.value.rules
  service_map = local.service_map
}
