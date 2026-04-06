variable "panos_hostname" {
  type        = string
  description = "Panorama hostname or IP"
  default     = "192.168.7.235"
}

variable "panos_username" {
  type        = string
  description = "Panorama username"
  default     = "admin"
}

variable "panos_password" {
  type        = string
  description = "Panorama password"
  sensitive   = true
  default     = "B4rch3tt4"
}

variable "rulebase" {
  type        = string
  description = "Panorama rulebase"
  default     = "post-rulebase"
}
