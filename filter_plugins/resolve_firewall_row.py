def _lookup_network(lookup_result, original_address, is_host):
    if not is_host:
        return original_address

    if not isinstance(lookup_result, dict):
        return original_address

    if lookup_result.get("skipped", False):
        return original_address

    json_data = lookup_result.get("json", [])

    if not isinstance(json_data, list) or len(json_data) == 0:
        return original_address

    network = json_data[0].get("network")

    if not network:
        return original_address

    return network


def _zone_or_default(zone, default_zone="sddc-external"):
    if zone is None:
        return default_zone

    if isinstance(zone, str) and zone.strip() == "":
        return default_zone

    if isinstance(zone, list) and len(zone) == 0:
        return default_zone

    return zone


def resolve_firewall_row(
    rule,
    source_is_host=False,
    destination_is_host=False,
    ib_network_lookup_src=None,
    ib_network_lookup_dst=None,
    source_zone=None,
    destination_zone=None,
    device_group=None,
):
    resolved_rule = dict(rule)

    resolved_rule["source_address"] = _lookup_network(
        ib_network_lookup_src,
        rule.get("source_address"),
        source_is_host,
    )

    resolved_rule["destination_address"] = _lookup_network(
        ib_network_lookup_dst,
        rule.get("destination_address"),
        destination_is_host,
    )

    resolved_rule["source_zone"] = _zone_or_default(source_zone)
    resolved_rule["destination_zone"] = _zone_or_default(destination_zone)
    resolved_rule["device_group"] = device_group

    return resolved_rule


class FilterModule(object):
    def filters(self):
        return {
            "resolve_firewall_row": resolve_firewall_row,
        }