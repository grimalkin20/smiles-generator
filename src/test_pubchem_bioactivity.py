
import json
import os

from resolver.pubchem_bioactivity import parse_assay_summary


def test_saved_assay_summary(cid: int) -> None:
    path = os.path.join(
        os.environ["TEMP"],
        f"pubchem_assays_{cid}.json",
    )

    print("\n" + "=" * 70)
    print(f"Testing PubChem assay summary | CID {cid}")
    print("=" * 70)

    if not os.path.exists(path):
        print(f"SKIP: JSON file not found: {path}")
        return

    with open(path, encoding="utf-8") as file:
        payload = json.load(file)

    result = parse_assay_summary(payload, cid=cid)
    records = result["records"]

    print("Records parsed:", result["record_count"])
    assert result["record_count"] > 0

    for record in records[:3]:
        print("\nAssay ID:", record["assay_id"])
        print("Outcome:", record["activity_outcome"])
        print("Activity value:", record["activity_value"])
        print("Activity unit:", record["activity_unit"])
        print("Target accession:", record["target_accession"])
        print("Target gene ID:", record["target_gene_id"])
        print("Assay name:", record["assay_name"])

    # Confirm fields are preserved and blanks aren't fabricated.
    first = records[0]
    assert first["assay_id"] is not None
    assert first["compound_cid"] == str(cid)
    assert "Activity Value [uM]" in first

    print("\nPASS")


def main() -> None:
    for cid in (3672, 338, 2519):
        test_saved_assay_summary(cid)


if __name__ == "__main__":
    main()
