from resolver.pubchem_experimental import (
    get_experimental_data,
    filter_property_records,
    get_available_properties,
)


def print_records(
    title: str,
    records: list[dict]
):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    if not records:
        print("No records found.")
        return

    for index, record in enumerate(
        records,
        start=1
    ):

        print(f"\nRecord {index}")
        print("-" * 50)

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

        print("Values:")

        if record["values"]:

            for value in record["values"]:
                print(f"  - {value}")

        else:

            print(
                "  - No value reported"
            )

        print("References:")

        if record["references"]:

            for reference in record[
                "references"
            ]:
                print(
                    f"  - {reference}"
                )

        else:

            print(
                "  - No reference reported"
            )


def main():

    # Change this CID when testing another compound.
    cid = 3672

    print("=" * 70)
    print(
        "       PUBCHEM EXPERIMENTAL DATA PARSER TEST"
    )
    print("=" * 70)

    print(f"\nCID: {cid}")

    # --------------------------------------------------
    # 1. ONE API REQUEST
    # --------------------------------------------------

    print(
        "\n[1] Retrieving experimental data..."
    )
    print("-" * 50)

    try:

        records = get_experimental_data(
            cid
        )

    except Exception as error:

        print("✗ Request failed")
        print(error)

        return

    if not records:

        print(
            "⚠ No Experimental Properties "
            "were available for this CID."
        )

        return

    print(
        f"✓ Retrieved {len(records)} "
        f"experimental records"
    )

    # --------------------------------------------------
    # 2. AVAILABLE PROPERTY HEADINGS
    # --------------------------------------------------

    print(
        "\n[2] Available property headings"
    )
    print("-" * 50)

    headings = get_available_properties(
        records
    )

    for heading in headings:

        print(
            f"  - {heading}"
        )

    # --------------------------------------------------
    # 3. TEST SELECTED PROPERTIES
    # --------------------------------------------------

    properties_to_test = [
        "Melting Point",
        "Solubility",
        "Density",
        "Vapor Pressure",
        "Flash Point",
        "Dissociation Constants",
    ]

    for property_name in (
        properties_to_test
    ):

        property_records = (
            filter_property_records(
                records,
                property_name
            )
        )

        print_records(
            property_name,
            property_records
        )

    # --------------------------------------------------
    # 4. SUMMARY
    # --------------------------------------------------

    print("\n" + "=" * 70)
    print(
        "       EXPERIMENTAL PARSER TEST COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()