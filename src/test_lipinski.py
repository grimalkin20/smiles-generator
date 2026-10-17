
from chemistry.rdkit_utils import (
    calculate_lipinski,
    calculate_lipinski_details,
)


def valid_properties():
    """Return a baseline molecule-like descriptor set."""
    return {
        "molecular_weight": 180.159,
        "logp": 1.3101,
        "h_bond_donors": 1,
        "h_bond_acceptors": 3,
    }


def test_all_rules_pass():
    result = calculate_lipinski_details(valid_properties())

    assert result["complete"] is True
    assert result["violation_count"] == 0
    assert result["lipinski_pass"] is True
    assert all(
        rule["passed"] is True
        for rule in result["rules"].values()
    )


def test_one_violation():
    properties = valid_properties()
    properties["molecular_weight"] = 501

    result = calculate_lipinski_details(properties)

    assert result["violation_count"] == 1
    assert result["rules"]["molecular_weight"]["passed"] is False
    assert result["lipinski_pass"] is True


def test_two_violations():
    properties = valid_properties()
    properties["molecular_weight"] = 501
    properties["logp"] = 5.1

    result = calculate_lipinski_details(properties)

    assert result["violation_count"] == 2
    assert result["lipinski_pass"] is False
    assert calculate_lipinski(properties) is False


def test_threshold_values_pass():
    properties = {
        "molecular_weight": 500,
        "logp": 5,
        "h_bond_donors": 5,
        "h_bond_acceptors": 10,
    }

    result = calculate_lipinski_details(properties)

    assert result["violation_count"] == 0
    assert result["lipinski_pass"] is True


def test_missing_property_is_not_a_pass():
    properties = valid_properties()
    del properties["logp"]

    result = calculate_lipinski_details(properties)

    assert result["complete"] is False
    assert result["evaluated_rule_count"] == 3
    assert result["violation_count"] is None
    assert result["lipinski_pass"] is None
    assert result["rules"]["logp"]["passed"] is None


def test_invalid_numeric_value_is_not_a_pass():
    properties = valid_properties()
    properties["logp"] = float("nan")

    result = calculate_lipinski_details(properties)

    assert result["complete"] is False
    assert result["lipinski_pass"] is None


def test_boolean_is_not_accepted_as_a_numeric_value():
    properties = valid_properties()
    properties["molecular_weight"] = True

    result = calculate_lipinski_details(properties)

    assert result["complete"] is False
    assert result["lipinski_pass"] is None


def main():
    tests = [
        test_all_rules_pass,
        test_one_violation,
        test_two_violations,
        test_threshold_values_pass,
        test_missing_property_is_not_a_pass,
        test_invalid_numeric_value_is_not_a_pass,
        test_boolean_is_not_accepted_as_a_numeric_value,
    ]

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")

    print(f"\nAll {len(tests)} Lipinski tests passed.")


if __name__ == "__main__":
    main()

