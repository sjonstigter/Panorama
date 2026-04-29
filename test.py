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


def main():
    args = parse_args()

    file_path = args.file_path

    # Sheets to read (0-based index → Excel sheet 4 and 5)
    sheets = [3, 4]

    dfs = []

    for sheet in sheets:
        df = pd.read_excel(
            file_path,
            sheet_name=sheet,
            usecols="B:R",
            skiprows=11,
            nrows=17
        )

        # Normalize empty/whitespace cells to NaN
        df = df.replace(r"^\s*$", pd.NA, regex=True)

        # Remove rows where "Row" is not numeric (e.g. "vb")
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

        # Rename our header names to something actually usable
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
            "Persistent Rule": "persistent"
        })

        # Drop empty "Unnamed" columns
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        # Fix integer-like floats, for example 55776.0 -> 55776
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