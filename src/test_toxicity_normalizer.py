
from chemistry.toxicity_normalizer import normalize_toxicity_record


def make_record(text, reference=1):
    return {
        "ReferenceNumber": reference,
        "Value": {"StringWithMarkup": [{"String": text}]},
        "Reference": ["Example source"],
    }


def test_ld50():
    result = normalize_toxicity_record(
        3672,
        "Non-Human Toxicity Values",
        make_record("LD50 Rat oral 636 mg/kg"),
    )

    assert result["endpoint"] == "LD50"
    assert result["value"] == 636
    assert result["unit"] == "mg/kg"
    assert result["species"] == "rat"
    assert result["route"] == "oral"
    assert result["record_type"] == "toxicity_observation"
    assert result["citations"] == ["Example source"]


def test_lc50_with_comparison():
    result = normalize_toxicity_record(
        338,
        "Toxicity Data",
        make_record("LC50 (mammals) > 300mg/m3"),
    )

    assert result["endpoint"] == "LC50"
    assert result["qualifier"] == ">"
    assert result["value"] == 300
    assert result["unit"] == "mg/m3"
    assert result["species"] == "mammals"


def test_mouse_oral_ld50():
    result = normalize_toxicity_record(
        2519,
        "Toxicity Data",
        make_record("LD50: 127 mg/kg (Oral, Mouse)"),
    )

    assert result["endpoint"] == "LD50"
    assert result["value"] == 127
    assert result["unit"] == "mg/kg"
    assert result["species"] == "mouse"
    assert result["route"] == "oral"


def test_narrative_summary_is_preserved():
    text = "This is a narrative summary without a measured endpoint."

    result = normalize_toxicity_record(
        3672,
        "Toxicity Summary",
        make_record(text),
    )

    assert result["record_type"] == "narrative_summary"
    assert result["raw_text"] == text
    assert result["value"] is None


def test_external_pointer_is_not_a_measurement():
    result = normalize_toxicity_record(
        338,
        "Lethal Dose",
        {
            "ReferenceNumber": 47,
            "Value": {
                "ExternalTableName": "collection=toxvaldb&kind=^LD$"
            },
        },
    )

    assert result["record_type"] == "external_table_pointer"
    assert result["external_table_name"] == (
        "collection=toxvaldb&kind=^LD$"
    )
    assert result["value"] is None


def test_human_narrative_does_not_get_a_numeric_measurement():
    text = (
        "In adults, iv doses of 57 mg/kg and oral doses of "
        "18-50 g have been fatal."
    )

    result = normalize_toxicity_record(
        2519,
        "Human Toxicity Values",
        make_record(text),
    )

    assert result["raw_text"] == text
    assert result["record_type"] == "toxicity_text_unparsed"
    assert result["value"] is None


if __name__ == "__main__":
    tests = [
        test_ld50,
        test_lc50_with_comparison,
        test_mouse_oral_ld50,
        test_narrative_summary_is_preserved,
        test_external_pointer_is_not_a_measurement,
        test_human_narrative_does_not_get_a_numeric_measurement,
    ]

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")

    print(f"\nAll {len(tests)} tests passed.")


