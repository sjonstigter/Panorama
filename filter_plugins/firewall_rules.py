def combine_firewall_rules(rules, combine_mode="none"):
    combined = {}

    for rule in rules:
        key_parts = [
            rule.get("description"),
            rule.get("source_zone"),
            rule.get("destination_zone"),
            rule.get("service_protocol", "").lower(),
            rule.get("group_id"),
            rule.get("action", "").lower(),
            rule.get("device_group"),
        ]

        if combine_mode == "none":
            key_parts.extend([
                rule.get("source_address"),
                rule.get("source_name"),
                rule.get("source_ci"),
                rule.get("destination_address"),
                rule.get("destination_name"),
                rule.get("destination_ci"),
            ])

        elif combine_mode == "destination-port":
            key_parts.extend([
                rule.get("source_address"),
                rule.get("source_name"),
                rule.get("source_ci"),
            ])

        elif combine_mode == "source-port":
            key_parts.extend([
                rule.get("destination_address"),
                rule.get("destination_name"),
                rule.get("destination_ci"),
            ])

        key = "|".join(str(x or "") for x in key_parts)

        if key not in combined:
            combined[key] = {
                "description": rule.get("description"),
                "source_zone": rule.get("source_zone"),
                "destination_zone": rule.get("destination_zone"),
                "service_protocol": rule.get("service_protocol", "").lower(),
                "group_id": rule.get("group_id"),
                "action": rule.get("action", "").lower(),
                "device_group": rule.get("device_group"),
                "applications": [],
                "service_destination_ports": [],
                "rows": [],
                "sources": [],
                "destinations": [],
            }

        combined[key]["applications"].append(rule.get("application"))
        combined[key]["service_destination_ports"].append(str(rule.get("service_destination_port")))
        combined[key]["rows"].append(rule.get("row"))

        combined[key]["sources"].append({
            "address": rule.get("source_address"),
            "name": rule.get("source_name"),
            "ci": rule.get("source_ci"),
        })

        combined[key]["destinations"].append({
            "address": rule.get("destination_address"),
            "name": rule.get("destination_name"),
            "ci": rule.get("destination_ci"),
        })

    return [_normalize_rule(rule) for rule in combined.values()]


def _unique_list(values):
    result = []
    for value in values:
        if value not in result and value is not None:
            result.append(value)
    return sorted(result)


def _unique_dicts(values):
    result = []
    for value in values:
        if value.get("address") and value not in result:
            result.append(value)
    return result


def _normalize_rule(rule):
    rule["applications"] = _unique_list(rule["applications"])
    rule["service_destination_ports"] = _unique_list(rule["service_destination_ports"])
    rule["rows"] = _unique_list(rule["rows"])
    rule["sources"] = _unique_dicts(rule["sources"])
    rule["destinations"] = _unique_dicts(rule["destinations"])
    return rule


class FilterModule(object):
    def filters(self):
        return {
            "combine_firewall_rules": combine_firewall_rules
        }