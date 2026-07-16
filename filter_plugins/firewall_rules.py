from collections import Counter

def combine_firewall_rules(rules, combine_mode="port"):
    combined = {}

#    for rule in rules:
#        if str(rule.get("rule_match", "")).strip().lower() == "rule matched":
#            continue

    for rule in rules:
        source_task = str(rule.get("source_task", "")).strip().lower()
        destination_task = str(rule.get("destination_task", "")).strip().lower()
        rule_match = str(rule.get("rule_match", "")).strip().lower()

        if (
            rule_match == "rule matched"
            or (
                "sddc" not in source_task
                and "sddc" not in destination_task
            )
        ):
            continue

#    for rule in rules:
        key_parts = [
            rule.get("source_zone"),
            rule.get("destination_zone"),
            rule.get("service_protocol", "").lower(),
            rule.get("action", "").lower(),
            rule.get("persistent"),
            rule.get("source_task"),
            rule.get("destination_task"),
            rule.get("device_group"),
        ]

        if combine_mode == "port":
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
                "az_source_zone": rule.get("az_source_zone"),
                "az_destination_zone": rule.get("az_destination_zone"),
                "service_protocol": rule.get("service_protocol", "").lower(),
                "group_id": rule.get("group_id"),
                "action": rule.get("action", "").lower(),
                "persistent": rule.get("persistent"),
                "source_task": rule.get("source_task"),
                "destination_task": rule.get("destination_task"),
                "device_group": rule.get("device_group"),
                "rule_match": rule.get("rule_match"),
                "rule_match_name": rule.get("rule_match_name"),
                "applications": [],
                "service_destination_ports": [],
                "rows": [],
                "sources": [],
                "destinations": [],
                "source_cis": [],
                "destination_cis": [],
                "common_cis": [],
            }

        combined[key]["applications"].append(rule.get("application"))
        combined[key]["service_destination_ports"].append(str(rule.get("services")))
        combined[key]["rows"].append(rule.get("row"))

        combined[key]["source_cis"].append(rule.get("source_ci"))
        combined[key]["destination_cis"].append(rule.get("destination_ci"))

        combined[key]["common_cis"].append(rule.get("source_ci"))
        combined[key]["common_cis"].append(rule.get("destination_ci"))

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


def _most_common_value(values):
    filtered_values = [value for value in values if value is not None]

    if not filtered_values:
        return None

    return Counter(filtered_values).most_common(1)[0][0]


def _normalize_rule(rule):
    rule["applications"] = _unique_list(rule["applications"])
    rule["service_destination_ports"] = _unique_list(rule["service_destination_ports"])
    rule["rows"] = _unique_list(rule["rows"])
    rule["common_source_ci"] = _most_common_value(rule["source_cis"])
    rule["common_destination_ci"] = _most_common_value(rule["destination_cis"])
    rule["common_ci"] = _most_common_value(rule["common_cis"])
    rule["sources"] = _unique_dicts(rule["sources"])
    rule["destinations"] = _unique_dicts(rule["destinations"])
    return rule


class FilterModule(object):
    def filters(self):
        return {
            "combine_firewall_rules": combine_firewall_rules
        }