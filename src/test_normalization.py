from resolver.pubchem_experimental import (
    get_experimental_data,
)

from chemistry.experimental_parser import (
    normalize_experimental_records,
)


def print_normalized_record(record):
    print()
    print("-" * 70)

    print(
        f"Property          : "
        f"{record['property']}"
    )

    print(
        f"Name              : "
        f"{record['name']}"
    )

    print(
        f"Reference Number  : "
        f"{record['reference_number']}"
    )

    for index, value in enumerate(
        record["values"],
        start=1
    ):

        print(
            f"\nValue {index}"
        )

        print(
            f"  Raw Value       : "
            f"{value['raw_value']}"
        )

        print(
            f"  Value           : "
            f"{value['value']}"
        )

        print(
            f"  Minimum         : "
            f"{value['min_value']}"
        )

        print(
            f"  Maximum         : "
            f"{value['max_value']}"
        )

        print(
            f"  Unit            : "
            f"{value['unit']}"
        )

        print(
            f"  Temperature     : "
            f"{value['temperature']}"
        )

        print(
            f"  Temperature Unit: "
            f"{value['temperature_unit']}"
        )

        print(
            f"  Qualitative     : "
            f"{value['qualitative']}"
        )

    print(
        "\nReferences:"
    )

    references = record.get(
        "references",
        []
    )

    if references:

        for reference in references:

            print(
                f"  - {reference}"
            )

    else:

        print(
            "  - No reference reported"
        )


def main():

    # --------------------------------------------------------
    # Use Ibuprofen first because it contains many useful
    # normalization cases.
    # --------------------------------------------------------

    cid = 3672

    print("=" * 70)

    print(
        "       PUBCHEM EXPERIMENTAL NORMALIZATION TEST"
    )

    print("=" * 70)

    print(
        f"\nCID: {cid}"
    )

    # --------------------------------------------------------
    # Retrieve raw experimental records
    # --------------------------------------------------------

    print(
        "\n[1] Retrieving experimental data..."
    )

    print(
        "-" * 50
    )

    records = get_experimental_data(
        cid
    )

    print(
        f"✓ Retrieved {len(records)} "
        f"experimental records"
    )

    if not records:

        print(
            "\nNo experimental records available."
        )

        return

    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    print(
        "\n[2] Normalizing experimental records..."
    )

    print(
        "-" * 50
    )

    normalized_records = (
        normalize_experimental_records(
            records
        )
    )

    print(
        f"✓ Normalized "
        f"{len(normalized_records)} records"
    )

    # --------------------------------------------------------
    # Display selected properties
    # --------------------------------------------------------

    selected_properties = [
        "Melting Point",
        "Solubility",
        "Vapor Pressure",
        "Dissociation Constants",
    ]

    for property_name in selected_properties:

        print(
            "\n"
            + "=" * 70
        )

        print(
            property_name
        )

        print(
            "=" * 70
        )

        matching_records = [
            record
            for record in normalized_records
            if record.get(
                "property"
            ) == property_name
        ]

        if not matching_records:

            print(
                "No records found."
            )

            continue

        for record in matching_records:

            print_normalized_record(
                record
            )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "       NORMALIZATION TEST COMPLETE"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()

    