
import json
import os

from resolver.pubchem_bioactivity import parse_assay_summary
from chemistry.bioactivity_normalizer import normalize_bioactivity_records


def test_compound(cid: int) -> None:
    path = os.path.join(
        os.environ["TEMP"],
        f"pubchem_assays_{cid}.json",
    )

    print("\n" + "=" * 65)
    print(f"Biological activity integration test | CID {cid}")
    print("=" * 65)

    if not os.path.exists(path):
        print(f"SKIP: Saved response not found: {path}")
        return

    with open(path, encoding="utf-8") as file:
        payload = json.load(file)

    retrieved = parse_assay_summary(payload, cid=cid)
    normalized = normalize_bioactivity_records(
        retrieved["records"]
    )

    assert len(normalized) == retrieved["record_count"]

    numeric_count = sum(
        item["activity_value"] is not None
        for item in normalized
    )

    target_count = sum(
        item["target_accession"] is not None
        or item["target_gene_id"] is not None
        for item in normalized
    )

    missing_count = sum(
        item["activity_value"] is None
        for item in normalized
    )

    for item in normalized:
        assert item["compound_cid"] == str(cid)
        assert item["assay_id"] is not None
        assert isinstance(item["source_record"], dict)

    print("Retrieved records:", retrieved["record_count"])
    print("Normalized records:", len(normalized))
    print("Numeric activity values:", numeric_count)
    print("Missing activity values:", missing_count)
    print("Records with target identifiers:", target_count)

    print("\nFirst normalized record:")
    if normalized:
        sample = normalized[0]
        for key in (
            "assay_id",
            "compound_cid",
            "activity_type",
            "activity_value",
            "activity_qualifier",
            "activity_unit",
            "activity_outcome",
            "target_accession",
            "target_gene_id",
        ):
            print(f"  {key}: {sample.get(key)}")

    print("\nPASS")


def main() -> None:
    for cid in (3672, 338, 2519):
        test_compound(cid)


if __name__ == "__main__":
    main()


