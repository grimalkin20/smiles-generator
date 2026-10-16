
from chemistry.toxicity_normalizer import normalize_toxicity_record


def make_record(text):
    return {
        "ReferenceNumber": 1,
        "Value": {"StringWithMarkup": [{"String": text}]},
    }


def test_estimated_ld50_range():
    text = (
        "The estimated LD50 for humans is between "
        "150 and 200 mg/kg."
    )

    result = normalize_toxicity_record(
        2519, "Toxicity Summary", make_record(text)
    )

    mentions = result["reported_dose_mentions"]
    assert any(
        m["context"] == "estimated_ld50"
        and m["value"] == 150
        and m["range_end"] == 200
        and m["unit"] == "mg/kg"
        for m in mentions
    )


def test_fatal_dose_mention():
    text = (
        "Case reports indicate that doses as low as "
        "57 mg/kg have resulted in fatalities."
    )

    result = normalize_toxicity_record(
        2519, "Toxicity Summary", make_record(text)
    )

    assert any(
        m["context"] == "reported_fatal_dose"
        and m["value"] == 57
        and m["unit"] == "mg/kg"
        for m in result["reported_dose_mentions"]
    )


def test_toxic_dose():
    text = (
        "A toxic dose is estimated to be around 1.2 g."
    )

    result = normalize_toxicity_record(
        2519, "Toxicity Summary", make_record(text)
    )

    assert any(
        m["context"] == "toxic_dose"
        and m["value"] == 1.2
        and m["unit"] == "g"
        for m in result["reported_dose_mentions"]
    )


def test_life_threatening_range():
    text = (
        "The life-threatening dose ranges from 10 to 14 g."
    )

    result = normalize_toxicity_record(
        2519, "Toxicity Summary", make_record(text)
    )

    assert any(
        m["context"] == "life_threatening_dose"
        and m["value"] == 10
        and m["range_end"] == 14
        and m["unit"] == "g"
        for m in result["reported_dose_mentions"]
    )


def test_original_text_is_preserved():
    text = (
        "In adults, iv doses of 57 mg/kg and oral doses "
        "of 18-50 g have been fatal."
    )

    result = normalize_toxicity_record(
        2519, "Human Toxicity Values", make_record(text)
    )

    assert result["raw_text"] == text
    assert result["value"] is None
    assert result["reported_dose_mentions"]

    
def test_adult_fatal_doses_include_oral_range():
    from chemistry.toxicity_normalizer import _extract_reported_dose_mentions

    text = (
        "In adults, iv doses of 57 mg/kg and oral doses of "
        "18-50 g have been fatal."
    )

    mentions = _extract_reported_dose_mentions(text)

    assert any(
        m["context"] == "reported_fatal_dose"
        and m["value"] == 57.0
        and m["unit"] == "mg/kg"
        for m in mentions
    )

    assert any(
        m["context"] == "reported_fatal_dose"
        and m["value"] == 18.0
        and m["range_end"] == 50.0
        and m["unit"] == "g"
        for m in mentions
    )

def test_child_fatal_ingestion_dose():
    from chemistry.toxicity_normalizer import _extract_reported_dose_mentions

    text = (
        "In one 5-year-old patient, death occurred following "
        "oral ingestion of approximately 3 g of caffeine."
    )

    mentions = _extract_reported_dose_mentions(text)

    assert any(
        mention["context"] == "reported_fatal_dose"
        and mention["value"] == 3.0
        and mention["unit"] == "g"
        for mention in mentions
    )



if __name__ == "__main__":
    tests = [
        test_estimated_ld50_range,
        test_fatal_dose_mention,
        test_toxic_dose,
        test_life_threatening_range,
        test_original_text_is_preserved,
        test_adult_fatal_doses_include_oral_range,
        test_child_fatal_ingestion_dose,
    ]

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")

    print(f"\nAll {len(tests)} narrative tests passed.")
