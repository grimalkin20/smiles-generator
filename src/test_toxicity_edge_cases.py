
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

        for section in walk_sections(data.get("Record", {}).get("Section", [])):
            heading = section.get("TOCHeading")

            if heading not in TARGET_HEADINGS:
                continue

            records.extend(normalize_toxicity_section(cid, section))

        print(f"\n{'=' * 65}")
        print(f"{name} | CID {cid}")
        print(f"{'=' * 65}")

        print("\n--- Endpoint recognized, but no numeric value extracted ---")
        unmatched = [
            r for r in records
            if r["endpoint"] and r["value"] is None
        ]

        if not unmatched:
            print("None")
        for r in unmatched:
            print(f"Heading: {r['heading']}")
            print(f"Reference: {r['reference_number']}")
            print(f"Text: {r['raw_text']!r}\n")

        print("--- Records without extracted original text ---")
        empty = [r for r in records if not r["raw_text"]]

        if not empty:
            print("None")
        for r in empty:
            print(
                f"Heading: {r['heading']} | "
                f"Reference: {r['reference_number']} | "
                f"Type: {r['record_type']} | "
                f"External pointer: {r['external_table_name']!r}"
            )

        print("\n--- Human toxicity records ---")
        human = [
            r for r in records
            if r["heading"] == "Human Toxicity Values"
        ]

        if not human:
            print("None")
        for r in human:
            print(f"Type: {r['record_type']}")
            print(f"Endpoint: {r['endpoint']}")
            print(f"Value: {r['value']}")
            print(f"Text: {r['raw_text']!r}\n")


if __name__ == "__main__":
    main()

