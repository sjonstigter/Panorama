variable "rulebase" {
  type = string
}

variable "position_keyword" {
  type = string
}

variable "group_tag" {
  type = string
}

variable "service_map" {
  type = map(string)
}

variable "rules" {
  type = list(object({
    name                  = string
    device_group          = string
    source_zones          = list(string)
    source_addresses      = list(string)
    source_users          = optional(list(string), ["any"])
    destination_zones     = list(string)
    destination_addresses = list(string)
    applications          = list(string)
    services              = list(string)
    categories            = optional(list(string), ["any"])
    tags                  = optional(list(string))
    action                = string
    description           = optional(string)
    disabled              = optional(bool)
  }))
}
