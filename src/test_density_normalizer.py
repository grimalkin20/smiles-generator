
from resolver.pubchem_experimental import get_experimental_data
from chemistry.experimental_parser import normalize_experimental_records
from chemistry.property_normalizer import normalize_property_records


def run_test(cid: int) -> None:
    print("\n" + "=" * 80)
    print(f"Density normalization test | PubChem CID: {cid}")
    print("=" * 80)

    raw_records = get_experimental_data(cid)
    generic_records = normalize_experimental_records(raw_records)
    normalized_records = normalize_property_records(generic_records)

    density_records = [
        record
        for record in normalized_records
        if record.get("property", "").strip().lower() == "density"
    ]

    print(f"Density records found: {len(density_records)}")

    for record in density_records:
        print(f"\nName: {record.get('name')}")
        print(f"Reference: {record.get('reference_number')}")

        for observation in record.get("observations", []):
            print(f"  Raw: {observation.get('raw_value')}")
            print(f"  Value: {observation.get('value')}")
            print(f"  Unit: {observation.get('unit')}")
            print(
                "  Temperature:",
                observation.get("temperature"),
                observation.get("temperature_unit"),
            )
            print(
                "  Reference temperature:",
                observation.get("reference_temperature"),
                observation.get("reference_temperature_unit"),
            )
            print(
                "  Interpretation:",
                observation.get("interpretation"),
            )


def main() -> None:
    # Ibuprofen
    run_test(3672)

    # Salicylic acid
    run_test(338)

    # Caffeine
    run_test(2519)


if __name__ == "__main__":
    main()
