import re
from typing import Any


# ============================================================
# Regular expressions
# ============================================================

NUMBER_PATTERN = r"\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"


# Numerical range:
#
#   75-77.5
#   75 – 77
#   75 to 77
#
# IMPORTANT:
# The numbers are intentionally unsigned here.
# A '-' between them is treated as a range separator.
RANGE_PATTERN = re.compile(
    rf"({NUMBER_PATTERN})\s*"
    r"(?:-|–|—|to)\s*"
    rf"({NUMBER_PATTERN})",
    re.IGNORECASE,
)


SINGLE_NUMBER_PATTERN = re.compile(
    rf"(?<![\d.])"
    rf"(-?{NUMBER_PATTERN})"
    rf"(?![\d.])"
)


# Temperature explicitly associated with a condition.
#
# Examples:
#   @ 25 °C
#   at 25 °C
#   at 20 °C
#   /25 °C/
#
# We intentionally do NOT simply search for any °C value,
# because "76 °C" may itself be the melting point.
CONDITION_TEMPERATURE_PATTERN = re.compile(
    rf"(?:@|at|around|approximately|approx\.?|/)\s*"
    rf"(-?{NUMBER_PATTERN})\s*"
    r"(?:°|º|˚)?\s*"
    r"(C|F|K)\b",
    re.IGNORECASE,
)


# Temperature appearing inside parentheses as a condition.
#
# Example:
#   (25 °C)
#
# This is useful for strings such as:
#   "21 mg/L (25 °C)"
PAREN_TEMPERATURE_PATTERN = re.compile(
    rf"\(\s*"
    rf"(-?{NUMBER_PATTERN})\s*"
    r"(?:°|º|˚)?\s*"
    r"(C|F|K)\s*"
    r"\)",
    re.IGNORECASE,
)


# ============================================================
# Unit aliases
# ============================================================

UNIT_ALIASES = {
    "°c": "°C",
    "ºc": "°C",
    "˚c": "°C",
    "c": "°C",

    "°f": "°F",
    "ºf": "°F",
    "˚f": "°F",
    "f": "°F",

    "k": "K",

    "mg/l": "mg/L",
    "mg/liter": "mg/L",
    "mg/litre": "mg/L",

    "mg/ml": "mg/mL",
    "g/ml": "g/mL",

    "g/cm3": "g/cm³",
    "g/cm³": "g/cm³",

    "mm hg": "mmHg",
    "mmhg": "mmHg",

    "pa": "Pa",
    "kpa": "kPa",
    "mpa": "MPa",

    "atm": "atm",
}


def normalize_unit(
    unit: str | None
) -> str | None:
    """
    Normalize common scientific units.
    """

    if not unit:
        return None

    cleaned = unit.strip()

    key = cleaned.lower()

    return UNIT_ALIASES.get(
        key,
        cleaned
    )


# ============================================================
# Number conversion
# ============================================================

def _to_float(
    value: str
) -> float:
    """
    Convert numeric text into float.
    """

    return float(
        value.replace(",", "").strip()
    )


# ============================================================
# Scientific notation
# ============================================================

def normalize_scientific_notation(
    text: str
) -> str:
    """
    Normalize PubChem-style scientific notation.

    Examples:

        4.74X10-5
        -> 4.74e-5

        2.16X10+4
        -> 2.16e+4

        9.0 x 10-7
        -> 9.0e-7
    """

    pattern = re.compile(
        rf"({NUMBER_PATTERN})"
        r"\s*[xX×]\s*10\s*"
        r"([+-]?\s*\d+)"
    )

    def replacement(match):

        base = match.group(1)

        exponent = (
            match.group(2)
            .replace(" ", "")
        )

        return (
            f"{base}e{exponent}"
        )

    return pattern.sub(
        replacement,
        text
    )


# ============================================================
# Temperature extraction
# ============================================================

def extract_temperature(
    text: str
) -> dict[str, Any]:
    """
    Extract an experimental/measurement temperature.

    IMPORTANT:
    A temperature is extracted only when it appears
    to be a condition.

    Examples:

        '21 mg/L @ 25 °C'
            -> 25 °C

        '0.021 mg/mL at 25 °C'
            -> 25 °C

        '76 °C'
            -> no separate temperature

    This prevents the actual property value from being
    incorrectly interpreted as the temperature.
    """

    # --------------------------------------------------------
    # First look for explicit condition markers.
    # --------------------------------------------------------

    match = CONDITION_TEMPERATURE_PATTERN.search(
        text
    )

    if match:

        return {
            "temperature": _to_float(
                match.group(1)
            ),
            "temperature_unit": normalize_unit(
                match.group(2)
            ),
        }

    # --------------------------------------------------------
    # Then look for parenthesized conditions.
    # --------------------------------------------------------

    match = PAREN_TEMPERATURE_PATTERN.search(
        text
    )

    if match:

        return {
            "temperature": _to_float(
                match.group(1)
            ),
            "temperature_unit": normalize_unit(
                match.group(2)
            ),
        }

    return {
        "temperature": None,
        "temperature_unit": None,
    }


# ============================================================
# Range parsing
# ============================================================

def parse_range(
    text: str
) -> tuple[float, float] | None:
    """
    Detect a numerical range.

    Examples:

        '75-77.5 °C'
            -> (75.0, 77.5)

        '75–77 °C'
            -> (75.0, 77.0)

        '235 to 237 °C'
            -> (235.0, 237.0)
    """

    match = RANGE_PATTERN.search(
        text
    )

    if not match:
        return None

    minimum = _to_float(
        match.group(1)
    )

    maximum = _to_float(
        match.group(2)
    )

    return (
        minimum,
        maximum
    )


# ============================================================
# Unit extraction
# ============================================================

def extract_unit(
    text: str,
    property_name: str | None = None
) -> str | None:
    """
    Extract common scientific units.

    This function is intentionally conservative.
    """

    patterns = [
        (r"mg\s*/\s*mL", "mg/mL"),
        (r"mg\s*/\s*L", "mg/L"),
        (r"g\s*/\s*mL", "g/mL"),
        (r"g\s*/\s*cm(?:3|³)", "g/cm³"),

        (r"mm\s*Hg", "mmHg"),

        (r"kPa", "kPa"),
        (r"MPa", "MPa"),
        (r"Pa", "Pa"),

        (r"atm\b", "atm"),

        (r"°\s*C", "°C"),
        (r"º\s*C", "°C"),
        (r"˚\s*C", "°C"),

        (r"°\s*F", "°F"),
        (r"º\s*F", "°F"),
        (r"˚\s*F", "°F"),

        (r"\bK\b", "K"),
    ]

    for pattern, normalized in patterns:

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):
            return normalized

    # PubChem sometimes reports units inside brackets.
    bracket_match = re.search(
        r"\[([^\]]+)\]",
        text
    )

    if bracket_match:

        return normalize_unit(
            bracket_match.group(1)
        )

    return None


# ============================================================
# Numeric value extraction
# ============================================================

def _extract_numeric_portion(
    text: str
) -> str:
    """
    Extract the first useful numerical value.

    Handles:
        76
        4.74e-5
        -5.2
    """

    match = SINGLE_NUMBER_PATTERN.search(
        text
    )

    if not match:
        return ""

    return match.group(1)


# ============================================================
# Qualitative detection
# ============================================================

def is_qualitative(
    text: str
) -> bool:
    """
    Determine whether a value is qualitative.

    Examples:

        'Readily soluble in water'
        'VERY SOLUBLE IN ALCOHOL'

    are qualitative.

    Numerical values are not.
    """

    if not text:
        return False

    if not re.search(
        NUMBER_PATTERN,
        text
    ):
        return True

    return False


# ============================================================
# Generic value normalization
# ============================================================

def normalize_value(
    raw_value: str,
    property_name: str | None = None,
    record_name: str | None = None
) -> dict[str, Any]:
    """
    Normalize one raw PubChem experimental value.

    The raw value is ALWAYS preserved.
    """

    if raw_value is None:
        raw_value = ""

    raw_value = str(
        raw_value
    ).strip()

    result = {
        "raw_value": raw_value,
        "value": None,
        "min_value": None,
        "max_value": None,
        "unit": None,
        "temperature": None,
        "temperature_unit": None,
        "qualitative": None,
    }

    if not raw_value:
        return result

    # --------------------------------------------------------
    # Normalize scientific notation first.
    # --------------------------------------------------------

    normalized_text = (
        normalize_scientific_notation(
            raw_value
        )
    )

    # --------------------------------------------------------
    # Extract actual experimental temperature.
    # --------------------------------------------------------

    temperature_data = (
        extract_temperature(
            raw_value
        )
    )

    result.update(
        temperature_data
    )

    # --------------------------------------------------------
    # Extract unit.
    # --------------------------------------------------------

    result["unit"] = extract_unit(
        raw_value,
        property_name
    )

    # --------------------------------------------------------
    # Check for numerical range.
    # --------------------------------------------------------

    numeric_range = parse_range(
        normalized_text
    )

    if numeric_range:

        result["min_value"] = (
            numeric_range[0]
        )

        result["max_value"] = (
            numeric_range[1]
        )

        return result

    # --------------------------------------------------------
    # Check for a single numerical value.
    # --------------------------------------------------------

    numeric_text = (
        _extract_numeric_portion(
            normalized_text
        )
    )

    if numeric_text:

        try:

            result["value"] = (
                _to_float(
                    numeric_text
                )
            )

            return result

        except ValueError:
            pass

    # --------------------------------------------------------
    # Qualitative value.
    # --------------------------------------------------------

    result["qualitative"] = raw_value

    return result


# ============================================================
# Experimental record normalization
# ============================================================

def normalize_experimental_record(
    record: dict[str, Any]
) -> dict[str, Any]:
    """
    Normalize one PubChem experimental record.
    """

    property_name = record.get(
        "property"
    )

    name = record.get(
        "name"
    )

    values = record.get(
        "values",
        []
    )

    normalized_values = []

    for raw_value in values:

        normalized_values.append(
            normalize_value(
                raw_value,
                property_name=property_name,
                record_name=name,
            )
        )

    return {
        "property": property_name,
        "name": name,
        "reference_number": record.get(
            "reference_number"
        ),
        "references": record.get(
            "references",
            []
        ),
        "description": record.get(
            "description"
        ),
        "values": normalized_values,
    }


# ============================================================
# Normalize all records
# ============================================================

def normalize_experimental_records(
    records: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Normalize an entire collection of
    PubChem experimental records.
    """

    return [
        normalize_experimental_record(
            record
        )
        for record in records
    ]

