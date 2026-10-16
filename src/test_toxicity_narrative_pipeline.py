
import json
import os
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

    for cid, name in CIDS.items():
        path = temp_dir / f"pubchem_toxicity_{cid}.json"

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        records = []

        for section in walk_sections(
            data.get("Record", {}).get("Section", [])
        ):
            if section.get("TOCHeading") not in TARGET_HEADINGS:
                continue

            records.extend(normalize_toxicity_section(cid, section))

        print(f"\n{'=' * 65}")
        print(f"{name} | CID {cid}")
        print(f"{'=' * 65}")

        records_with_mentions = [
            record for record in records
            if record.get("reported_dose_mentions")
        ]

        print(
            "Records with reported dose mentions: "
            f"{len(records_with_mentions)}"
        )

        for record in records_with_mentions:
            print(f"\nHeading: {record['heading']}")
            print(f"Reference: {record['reference_number']}")
            print(f"Record type: {record['record_type']}")
            print(f"Original text: {record['raw_text'][:500]}")

            for mention in record["reported_dose_mentions"]:
                print(f"  Context: {mention['context']}")
                print(f"  Value: {mention['value']}")
                print(f"  Range end: {mention['range_end']}")
                print(f"  Unit: {mention['unit']}")
                print(f"  Excerpt: {mention['source_excerpt']}")

        human_records = [
            record for record in records
            if record["heading"] == "Human Toxicity Values"
        ]

        print("\nHuman toxicity records:")
        for record in human_records:
            print(f"  Reference: {record['reference_number']}")
            print(f"  Original text: {record['raw_text']}")
            print(
                "  Dose mentions: "
                f"{len(record.get('reported_dose_mentions', []))}"
            )


if __name__ == "__main__":
    main()

