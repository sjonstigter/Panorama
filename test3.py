#!/usr/bin/env python3

# sudo apt install python3-pandas python3-openpyxl

import argparse
import json
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert firewall Excel change form rows to JSON."
    )

    parser.add_argument(
        "file_path",
        help="Path to the Excel file, for example ORD-64699-Z0S1FirewallChangeForm_Publish16.xlsx"
    )

    return parser.parse_args()


def multiline_to_list(value):
    """
    Convert multiline Excel cell values to a clean Python list.

    Example:
      "443\\n554-560\\n605"

    Becomes:
      ["443", "554-560", "605"]
    """
    if pd.isna(value):
        return []

    return [
        item.strip()
        for item in str(value).splitlines()
        if item.strip()
    ]


def protocol_ports_to_services(protocol, ports):
    """
    Convert protocol + ports to normalized service names.

    Examples:
      TCP + ["80"]       -> ["tcp-80"]
      UDP + ["53"]       -> ["udp-53"]
      TCP/UDP + ["80"]   -> ["tcp-80", "udp-80"]
    """
    protocol = str(protocol or "").strip().lower()
    ports = multiline_to_list(ports)

    services = []

    for port in ports:
        if protocol == "tcp/udp":
            services.append(f"tcp-{port}")
            services.append(f"udp-{port}")
        elif protocol in ["tcp", "udp"]:
            services.append(f"{protocol}-{port}")
        else:
            services.append(port)

    return services


def main():
    args = parse_args()

    file_path = args.file_path

    # Sheets to read (0-based index -> Excel sheet 4 and 5)
    sheets = [3, 4]

    dfs = []

    for sheet in sheets:
        df = pd.read_excel(
            file_path,
            sheet_name=sheet,
            usecols="B:V",
            skiprows=11,
            nrows=17
        )

        # Normalize empty/whitespace cells to NaN
        df = df.replace(r"^\s*$", pd.NA, regex=True)

        # Remove rows where "Row" is not numeric, for example "vb"
        df = df[pd.to_numeric(df["Row"], errors="coerce").notna()]

        # Remove empty rows
        df = df[
            df[
                [
                    "Description",
                    "Source IP adress(es)",
                    "Destination IP adress(es)"
                ]
            ].notna().any(axis=1)
        ]

        # Rename Excel header names to usable internal names
        df = df.rename(columns={
            "Row": "row",
            "Description": "description",
            "Src. Appl. CI nr": "source_ci",
            "Source IP adress(es)": "source_address",
            "DNS name or EPG": "source_name",
            "Network Zone": "source_zone",
            "Group ID / MS AD": "group_id",
            "Dest. Appl. CI Nr": "destination_ci",
            "Destination IP adress(es)": "destination_address",
            "DNS name or EPG.1": "destination_name",
            "Network Zone.1": "destination_zone",
            "Network application/service": "application",
            "Protocol": "service_protocol",
            "Port(s)": "service_destination_port",
            "Action": "action",
            "Persistent Rule": "persistent",
            "Leverancier": "supplier",
            "Regel omschrijving": "rule_description2",
            "Source Task for": "source_task",
            "Destination Task for": "destination_task"
        })

        # Drop empty "Unnamed" columns
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        # Fix integer-like floats, for example 443.0 -> 443
        for col in df.select_dtypes(include=["float"]):
            if (df[col].dropna() % 1 == 0).all():
                df[col] = df[col].astype("Int64")

        dfs.append(df)

    # Combine both sheets
    df = pd.concat(dfs, ignore_index=True)

    # Normalize action values
    df["action"] = df["action"].replace({
        "Permit": "allow",
        "Deny": "deny"
    })

    # Normalize persistent values
    df["persistent"] = df["persistent"].replace({
        "Yes": True,
        "No": False
    })

    # Create normalized services field from protocol + ports
    #
    # Examples:
    #   service_protocol = TCP
    #   service_destination_port = 80
    #   services = ["tcp-80"]
    #
    #   service_protocol = TCP/UDP
    #   service_destination_port = 80
    #   services = ["tcp-80", "udp-80"]
    df["services"] = df.apply(
        lambda row: protocol_ports_to_services(
            row["service_protocol"],
            row["service_destination_port"]
        ),
        axis=1
    )

    # Remove original raw port column from final JSON
    df = df.drop(columns=["service_destination_port"])

    # Convert pandas NaN → Python None, so JSON shows null
    df = df.astype(object).where(pd.notna(df), None)

    # Wrap records in top-level firewall_rules key
    output_data = {
        "firewall_rules": df.to_dict(orient="records")
    }

    # Convert to JSON
    json_data = json.dumps(
        output_data,
        ensure_ascii=False,
        indent=2
    )

    print(json_data)


if __name__ == "__main__":
    main()