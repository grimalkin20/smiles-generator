
"""Integration test for real PubChem toxicity JSON responses."""

import json
import os
from collections import Counter
from pathlib import Path

from chemistry.toxicity_normalizer import normalize_toxicity_section


CIDS = {
    3672: "Ibuprofen",
    338: "Salicylic acid",
    2519: "Caffeine",
}

TARGET_HEADINGS = {
    "Toxicity Data",
    "Human Toxicity Values",
    "Non-Human Toxicity Values",
    "Lethal Dose",
    "Lethal Concentration",
    "Effect Level",
    "Toxicity Summary",
}


def walk_sections(sections):
    """Yield all sections, including nested sections."""
    for section in sections or []:
        if not isinstance(section, dict):
            continue

        yield section

        children = section.get("Section", [])
        if isinstance(children, dict):
            children = [children]

        yield from walk_sections(children)


def main():
    temp_dir = Path(os.environ["TEMP"])
    all_records = []
    errors = []

    for cid, compound_name in CIDS.items():
        path = temp_dir / f"pubchem_toxicity_{cid}.json"

        print(f"\n{'=' * 55}")
        print(f"{compound_name} | CID {cid}")
        print(f"{'=' * 55}")

        if not path.exists():
            errors.append(f"Missing input file: {path}")
            print(f"ERROR: File not found: {path}")
            continue

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"Could not read {path}: {exc}")
            print(f"ERROR: {exc}")
            continue

        record = data.get("Record", {})
        sections = record.get("Section", [])

        compound_records = []

        for section in walk_sections(sections):
            heading = section.get("TOCHeading")

            if heading not in TARGET_HEADINGS:
                continue

            try:
                normalized = normalize_toxicity_section(cid, section)
                compound_records.extend(normalized)
            except Exception as exc:
                errors.append(
                    f"CID {cid}, heading {heading}: "
                    f"{type(exc).__name__}: {exc}"
                )

        all_records.extend(compound_records)

        types = Counter(r["record_type"] for r in compound_records)
        endpoints = Counter(
            r["endpoint"]
            for r in compound_records
            if r["endpoint"]
        )

        print(f"Normalized records: {len(compound_records)}")
        print(f"Record types: {dict(types)}")
        print(f"Recognized endpoints: {dict(endpoints)}")

        parsed = [
            r for r in compound_records
            if r["value"] is not None
        ]
        print(f"Records with extracted numeric values: {len(parsed)}")

        for item in parsed[:5]:
            print(
                f"  {item['heading']}: "
                f"{item['endpoint']} {item['qualifier'] or ''} "
                f"{item['value']} {item['unit'] or '[unit missing]'}; "
                f"species={item['species'] or '[unknown]'}; "
                f"route={item['route'] or '[unknown]'}"
            )

    print(f"\n{'=' * 55}")
    print("INTEGRATION TEST SUMMARY")
    print(f"{'=' * 55}")
    print(f"Total normalized records: {len(all_records)}")
    print(
        "Records with original text: "
        f"{sum(bool(r['raw_text']) for r in all_records)}"
    )
    print(
        "Records with citations: "
        f"{sum(bool(r['citations']) for r in all_records)}"
    )
    print(
        "External pointers: "
        f"{sum(r['record_type'] == 'external_table_pointer' for r in all_records)}"
    )
    print(f"Errors: {len(errors)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    if not all_records:
        raise SystemExit("FAIL: No records were normalized.")

    print("\nPASS: Real PubChem responses processed without exceptions.")


if __name__ == "__main__":
    main()


