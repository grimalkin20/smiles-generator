
from chemistry.bioactivity_normalizer import (
    normalize_bioactivity_record,
    normalize_bioactivity_records,
)


def main() -> None:
    cases = [
        {
            "name": "IC50 numeric value",
            "record": {
                "AID": "101",
                "CID": "3672",
                "Activity Name": "IC50",
                "Activity Value [uM]": "0.5",
                "Activity Outcome": "Active",
            },
            "expected_value": 0.5,
            "expected_qualifier": "=",
            "expected_type": "IC50",
            "expected_unit": "uM",
        },
        {
            "name": "EC50 less-than value",
            "record": {
                "AID": "102",
                "CID": "338",
                "activity_name": "EC50",
                "activity_value_raw": "< 0.05",
                "activity_unit": "nM",
            },
            "expected_value": 0.05,
            "expected_qualifier": "<",
            "expected_type": "EC50",
            "expected_unit": "nM",
        },
        {
            "name": "Ki greater-than value",
            "record": {
                "AID": "103",
                "CID": "2519",
                "activity_name": "Ki",
                "activity_value_raw": "> 10",
                "activity_unit": "uM",
            },
            "expected_value": 10.0,
            "expected_qualifier": ">",
            "expected_type": "Ki",
            "expected_unit": "uM",
        },
        {
            "name": "Missing measurement",
            "record": {
                "AID": "104",
                "CID": "3672",
                "Activity Outcome": "Inactive",
                "Activity Value [uM]": "",
                "Activity Name": "",
            },
            "expected_value": None,
            "expected_qualifier": None,
            "expected_type": None,
            "expected_unit": None,
        },
    ]

    for case in cases:
        result = normalize_bioactivity_record(case["record"])

        assert result["activity_value"] == case["expected_value"], case["name"]
        assert result["activity_qualifier"] == case["expected_qualifier"], case["name"]
        assert result["activity_type"] == case["expected_type"], case["name"]
        assert result["activity_unit"] == case["expected_unit"], case["name"]

        print(f"PASS: {case['name']}")

    collection = normalize_bioactivity_records(
        [case["record"] for case in cases]
    )
    assert len(collection) == len(cases)

    # The original source fields must remain available.
    assert collection[0]["source_record"]["AID"] == "101"

    print(f"\nAll {len(cases)} test cases passed.")


if __name__ == "__main__":
    main()


