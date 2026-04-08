locals {
  rules_by_device_group = {
    for dg in distinct([for r in var.rules : r.device_group]) :
    dg => [for r in var.rules : r if r.device_group == dg]
  }
}

resource "panos_security_rule_group" "this" {
  for_each = local.rules_by_device_group

  device_group     = each.key
  rulebase         = var.rulebase
  position_keyword = var.position_keyword

  dynamic "rule" {
    for_each = each.value

    content {
      name                  = rule.value.name
      source_zones          = rule.value.source_zones
      source_addresses      = rule.value.source_addresses
      source_users          = try(rule.value.source_users, ["any"])
      destination_zones     = rule.value.destination_zones
      destination_addresses = rule.value.destination_addresses
      applications          = rule.value.applications
      services = [
        for svc in rule.value.services : lookup(var.service_map, svc, svc)
      ]
      categories = try(rule.value.categories, ["any"])
      tags       = try(rule.value.tags, null)
      group_tag  = var.group_tag
      action     = rule.value.action
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}
