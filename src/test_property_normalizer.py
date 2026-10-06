from resolver.pubchem_experimental import (
    get_experimental_data
)

from chemistry.experimental_parser import (
    normalize_experimental_records
)

from chemistry.property_normalizer import (
    normalize_property_records
)


def print_property(
    records,
    property_name
):
    print()
    print("=" * 80)
    print(property_name)
    print("=" * 80)

    found = False

    for record in records:

        if (
            record.get("property", "").lower()
            != property_name.lower()
        ):
            continue

        found = True

        print()
        print("Name:", record.get("name"))
        print(
            "Reference:",
            record.get("reference_number")
        )

        for observation in record.get(
            "observations",
            []
        ):

            print(
                "  Raw:",
                observation.get("raw_value")
            )

            print(
                "  Solvent:",
                observation.get("solvent")
            )

            print(
                "  Value:",
                observation.get("value")
            )

            print(
                "  Min:",
                observation.get("min_value")
            )

            print(
                "  Max:",
                observation.get("max_value")
            )

            print(
                "  Unit:",
                observation.get("unit")
            )

            print(
                "  Temperature:",
                observation.get("temperature")
            )

            print(
                "  Temperature Unit:",
                observation.get(
                    "temperature_unit"
                )
            )

            print(
                "  Qualitative:",
                observation.get("qualitative")
            )

            print(
                "  Interpretation:",
                observation.get(
                    "interpretation_type"
                )
            )

            print(
                "  Mass:",
                observation.get(
                    "mass"
                )
            )

            print(
                "  Mass Unit:",
                observation.get(
                    "mass_unit"
                )
            )

            print(
                "  Volume:",
                observation.get(
                    "volume"
                )
            )

            print(
                "  Volume Unit:",
                observation.get(
                    "volume_unit"
                )
            )

    if not found:
        print("No records found.")


def run_test(cid: int):

    print()
    print("#" * 80)
    print(f"CID: {cid}")
    print("#" * 80)

    print(
        f"Retrieving experimental data..."
    )

    raw_records = get_experimental_data(
        cid
    )

    print(
        f"Raw records: {len(raw_records)}"
    )

    normalized_records = (
        normalize_experimental_records(
            raw_records
        )
    )

    property_records = (
        normalize_property_records(
            normalized_records
        )
    )

    print(
        f"Normalized records: "
        f"{len(property_records)}"
    )

    print_property(
        property_records,
        "Solubility"
    )


def main():

    # Ibuprofen
    run_test(3672)

    # Salicylic acid
    run_test(338)

    # Caffeine
    run_test(2519)


if __name__ == "__main__":
    main()