import re
from typing import Any


# ============================================================
# GENERAL HELPERS
# ============================================================

def _normalize_property_name(
    property_name: str | None
) -> str:

    if not property_name:
        return ""

    return property_name.strip().lower()


def _copy_common_fields(
    record: dict[str, Any]
) -> dict[str, Any]:

    return {
        "property": record.get("property"),
        "name": record.get("name"),
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
    }

# ============================================================
# SOLVENT CLEANING HELPER
# ============================================================

def _clean_solvent(
    solvent: str | None
) -> str | None:

    if not solvent:
        return None

    solvent = solvent.strip()

    # Remove trailing temperature conditions.
    solvent = re.sub(
        r"\s+at\s+-?\d+(?:\.\d+)?\s*"
        r"(?:°|º|˚)?\s*(?:C|F|K)\b",
        "",
        solvent,
        flags=re.IGNORECASE
    )

    # Normalize "boiling water" etc.
    solvent = re.sub(
        r"^\s*boiling\s+",
        "",
        solvent,
        flags=re.IGNORECASE
    )

    return solvent.strip()


# ============================================================
# TEMPERATURE
# ============================================================

def _extract_temperature(
    text: str
) -> tuple[float | None, str | None]:

    pattern = re.compile(
        r"(?:@|at|around|approximately|approx\.?|\()\s*"
        r"(-?\d+(?:\.\d+)?)\s*"
        r"(?:°|º|˚)?\s*"
        r"(C|F|K)\b",
        re.IGNORECASE
    )

    match = pattern.search(text)

    if not match:
        return None, None

    temperature = float(
        match.group(1)
    )

    unit = match.group(2).upper()

    if unit == "C":
        unit = "°C"
    elif unit == "F":
        unit = "°F"

    return temperature, unit


# ============================================================
# NUMBER PARSING
# ============================================================

def _parse_number(
    text: str
) -> float | None:
    """
    Parse:

        21
        2,240
        2.16X10+4
        4.74X10-5
        2.16 x 10^4
    """

    cleaned = (
        text
        .strip()
        .replace(",", "")
    )

    scientific = re.fullmatch(
        r"([+-]?\d+(?:\.\d+)?)"
        r"\s*[xX×]\s*10"
        r"(?:\^)?"
        r"\s*([+-]?\d+)",
        cleaned
    )

    if scientific:

        base = float(
            scientific.group(1)
        )

        exponent = int(
            scientific.group(2)
        )

        return base * (
            10 ** exponent
        )

    try:
        return float(
            cleaned
        )

    except ValueError:
        return None


# ============================================================
# UNIT NORMALIZATION
# ============================================================

def _normalize_unit(
    unit: str | None
) -> str | None:

    if not unit:
        return None

    cleaned = (
        unit
        .strip()
        .lower()
    )

    cleaned = re.sub(
        r"\s+",
        "",
        cleaned
    )

    aliases = {
        "mg/l": "mg/L",
        "mg/ml": "mg/mL",
        "g/l": "g/L",
        "g/ml": "g/mL",
        "g/100ml": "g/100mL",
        "g/cm3": "g/cm³",
        "g/cm³": "g/cm³",
        "mmhg": "mmHg",
    }

    return aliases.get(
        cleaned,
        cleaned
    )


# ============================================================
# SOLVENTS
# ============================================================

COMMON_SOLVENTS = [
    "carbon tetrachloride",
    "oil of turpentine",
    "absolute ethanol",
    "diethyl ether",
    "tetrahydrofuran",
    "petroleum ether",
    "benzene",
    "propanol",
    "ethanol",
    "methanol",
    "acetone",
    "chloroform",
    "ether",
    "hexane",
    "toluene",
    "acetonitrile",
    "pyridine",
    "pyrrole",
    "alcohol",
    "water",
]


def _extract_solvent(
    text: str
) -> str | None:

    lowered = text.lower()

    # --------------------------------------------------------
    # Explicit "in <solvent>"
    # --------------------------------------------------------

    for solvent in sorted(
        COMMON_SOLVENTS,
        key=len,
        reverse=True
    ):

        if re.search(
            rf"\bin\s+{re.escape(solvent)}\b",
            lowered
        ):
            return solvent

    # --------------------------------------------------------
    # Solvent immediately before a number
    #
    # benzene 0.775
    # ethanol 34.87
    # --------------------------------------------------------

    for solvent in sorted(
        COMMON_SOLVENTS,
        key=len,
        reverse=True
    ):

        if re.search(
            rf"\b{re.escape(solvent)}\b"
            rf"\s+(?=[+-]?\d)",
            lowered
        ):
            return solvent

    return None


# ============================================================
# CONTEXT DETECTION
# ============================================================

def _detect_solubility_context(
    text: str
) -> dict[str, Any]:
    """
    Detect context applying to the whole statement.

    Examples:

        Solubility (weight percent): ...

        Solubility in water, g/100ml at 20 °C: ...

    The context is inherited by individual observations.
    """

    lowered = text.lower()

    context = {
        "unit": None,
        "interpretation_type": None,
        "solvent": None,
        "temperature": None,
        "temperature_unit": None,
    }

    # --------------------------------------------------------
    # Weight percent
    # --------------------------------------------------------

    if (
        "weight percent" in lowered
        or "weight%" in lowered
    ):

        context["unit"] = "%"
        context["interpretation_type"] = (
            "weight_percent"
        )

    # --------------------------------------------------------
    # g/100 mL
    # --------------------------------------------------------

    if re.search(
        r"g\s*/\s*100\s*mL",
        text,
        re.IGNORECASE
    ):

        context["unit"] = "g/100mL"
        context["interpretation_type"] = (
            "quantitative"
        )

    # --------------------------------------------------------
    # Parent solvent
    #
    # Only inherit an explicit solvent when the statement
    # is actually describing measurements in that solvent.
    # --------------------------------------------------------

    if re.search(
        r"\bin\s+water\s*,",
        text,
        re.IGNORECASE
    ):
        context["solvent"] = "water"

    elif re.search(
        r"\bin\s+"
        r"(?:carbon tetrachloride|benzene|"
        r"propanol|ethanol|methanol|acetone|"
        r"chloroform|ether|toluene)\s*,",
        text,
        re.IGNORECASE
    ):
        context["solvent"] = _clean_solvent(
            _extract_solvent(text)
        )
    else:
        context["solvent"] = None

    # --------------------------------------------------------
    # Temperature in parent context
    # --------------------------------------------------------

    temperature, temperature_unit = (
        _extract_temperature(
            text
        )
    )

    context["temperature"] = temperature
    context["temperature_unit"] = (
        temperature_unit
    )

    return context


# ============================================================
# QUANTITY WITH EXPLICIT UNIT
# ============================================================

def _extract_explicit_quantity(
    text: str
) -> dict[str, Any] | None:

    unit_pattern = (
        r"(mg\s*/\s*L|"
        r"mg\s*/\s*mL|"
        r"g\s*/\s*L|"
        r"g\s*/\s*mL|"
        r"g\s*/\s*100\s*mL)"
    )

    # --------------------------------------------------------
    # Scientific notation
    # --------------------------------------------------------

    scientific = re.search(
        rf"([+-]?\d+(?:\.\d+)?"
        rf"\s*[xX×]\s*10"
        rf"(?:\^)?\s*[+-]?\d+)"
        rf"\s*{unit_pattern}",
        text,
        re.IGNORECASE
    )

    if scientific:

        return {
            "value": _parse_number(
                scientific.group(1)
            ),
            "min_value": None,
            "max_value": None,
            "unit": _normalize_unit(
                scientific.group(2)
            ),
        }

    # --------------------------------------------------------
    # Number BEFORE unit in source wording:
    #
    # g/100ml: 0.2
    # g/100ml 0.2
    # --------------------------------------------------------

    standard_before_unit = re.search(
        rf"{unit_pattern}"
        rf"\s*(?::|=)\s*"
        rf"([+-]?\d+(?:,\d{{3}})*(?:\.\d+)?)"
        r"(?![\d.])",
        text,
        re.IGNORECASE
    )

    if standard_before_unit:

        return {
            "value": _parse_number(
                standard_before_unit.group(2)
            ),
            "min_value": None,
            "max_value": None,
            "unit": _normalize_unit(
                standard_before_unit.group(1)
            ),
        }

    # --------------------------------------------------------
    # Standard number AFTER unit
    #
    # 0.2 g/100ml
    # 21 mg/L
    # --------------------------------------------------------

    standard_after_unit = re.search(
        rf"(?<![\d.])"
        rf"([+-]?\d+(?:,\d{{3}})*(?:\.\d+)?)"
        rf"\s*{unit_pattern}",
        text,
        re.IGNORECASE
    )

    if standard_after_unit:

        return {
            "value": _parse_number(
                standard_after_unit.group(1)
            ),
            "min_value": None,
            "max_value": None,
            "unit": _normalize_unit(
                standard_after_unit.group(2)
            ),
        }


    return None


# ============================================================
# RANGE
# ============================================================

def _extract_range(
    text: str
) -> dict[str, Any] | None:

    unit_pattern = (
        r"(mg\s*/\s*L|"
        r"mg\s*/\s*mL|"
        r"g\s*/\s*L|"
        r"g\s*/\s*mL|"
        r"g\s*/\s*100\s*mL)"
    )

    match = re.search(
        rf"(?<![\d.])"
        rf"(\d+(?:,\d{{3}})*(?:\.\d+)?)"
        rf"\s*(?:-|–|—|to)\s*"
        rf"(\d+(?:,\d{{3}})*(?:\.\d+)?)"
        rf"\s*"
        rf"{unit_pattern}",
        text,
        re.IGNORECASE
    )

    if not match:
        return None

    return {
        "value": None,
        "min_value": _parse_number(
            match.group(1)
        ),
        "max_value": _parse_number(
            match.group(2)
        ),
        "unit": _normalize_unit(
            match.group(3)
        ),
    }


# ============================================================
# DISSOLUTION RATIO
# ============================================================

def _extract_dissolution_ratio(
    text: str
) -> dict[str, Any] | None:

    match = re.search(
        r"(?<![\d.])"
        r"([+-]?\d+(?:,\d{3})*(?:\.\d+)?)"
        r"\s*(?:g|gm|gram|grams)"
        r"\s+dissolves\s+in\s+"
        r"([+-]?\d+(?:,\d{3})*(?:\.\d+)?)"
        r"\s*mL\s+"
        r"([A-Za-z][A-Za-z\s\-]*)",
        text,
        re.IGNORECASE
    )

    if not match:
        return None

    solvent = match.group(3).strip()

    solvent = re.split(
        r",|;",
        solvent
    )[0].strip()

    return {
        "mass": _parse_number(
            match.group(1)
        ),
        "mass_unit": "g",
        "volume": _parse_number(
            match.group(2)
        ),
        "volume_unit": "mL",
        "solvent": solvent,
    }


# ============================================================
# INDIVIDUAL SOLUBILITY OBSERVATION
# ============================================================

def _parse_solubility_observation(
    text: str,
    context: dict[str, Any] | None = None
) -> dict[str, Any]:

    if context is None:
        context = {}

    raw_text = text.strip()

    # --------------------------------------------------------
    # Temperature
    # --------------------------------------------------------

    temperature, temperature_unit = (
        _extract_temperature(
            raw_text
        )
    )

    if temperature is None:
        temperature = context.get(
            "temperature"
        )

    if temperature_unit is None:
        temperature_unit = context.get(
            "temperature_unit"
        )

    # --------------------------------------------------------
    # Solvent
    # --------------------------------------------------------

    solvent = _clean_solvent(
        _extract_solvent(
        raw_text
    ))

    if solvent is None:
        solvent = context.get(
            "solvent"
        )

    # --------------------------------------------------------
    # Range FIRST
    #
    # This is important.
    #
    # "10 to 50 mg/mL"
    #
    # must not become value=50.
    # --------------------------------------------------------

    range_value = _extract_range(
        raw_text
    )

    if range_value:

        return {
            "raw_value": raw_text,
            "solvent": solvent,
            "value": None,
            "min_value": range_value[
                "min_value"
            ],
            "max_value": range_value[
                "max_value"
            ],
            "unit": range_value[
                "unit"
            ],
            "temperature": temperature,
            "temperature_unit": temperature_unit,
            "qualitative": None,
            "interpretation_type": (
                "quantitative_range"
            ),
        }

    # --------------------------------------------------------
    # Explicit quantity
    # --------------------------------------------------------

    quantity = _extract_explicit_quantity(
        raw_text
    )

    if quantity:

        return {
            "raw_value": raw_text,
            "solvent": solvent,
            "value": quantity["value"],
            "min_value": None,
            "max_value": None,
            "unit": quantity["unit"],
            "temperature": temperature,
            "temperature_unit": temperature_unit,
            "qualitative": None,
            "interpretation_type": (
                "quantitative"
            ),
        }

    # --------------------------------------------------------
    # Dissolution ratio
    # --------------------------------------------------------

    ratio = _extract_dissolution_ratio(
        raw_text
    )

    if ratio:

        return {
            "raw_value": raw_text,
            "solvent": ratio["solvent"],
            "value": None,
            "min_value": None,
            "max_value": None,
            "unit": None,
            "temperature": temperature,
            "temperature_unit": temperature_unit,
            "qualitative": None,
            "interpretation_type": (
                "solvent_volume_required"
            ),
            "mass": ratio["mass"],
            "mass_unit": ratio["mass_unit"],
            "volume": ratio["volume"],
            "volume_unit": ratio["volume_unit"],
        }

    # --------------------------------------------------------
    # Inherited quantitative context
    #
    # Example:
    #
    # weight percent:
    # benzene 0.775
    # --------------------------------------------------------

    inherited_unit = context.get(
        "unit"
    )

    if inherited_unit:

        number_match = re.search(
            r"(?<![\d.])"
            r"([+-]?\d+(?:,\d{3})*(?:\.\d+)?)"
            r"(?![\d.])",
            raw_text
        )

        if number_match:

            value = _parse_number(
                number_match.group(1)
            )

            interpretation = context.get(
                "interpretation_type"
            )

            if interpretation is None:
                interpretation = (
                    "quantitative"
                )

            return {
                "raw_value": raw_text,
                "solvent": solvent,
                "value": value,
                "min_value": None,
                "max_value": None,
                "unit": inherited_unit,
                "temperature": temperature,
                "temperature_unit": temperature_unit,
                "qualitative": None,
                "interpretation_type": interpretation,
            }

    # --------------------------------------------------------
    # Qualitative
    # --------------------------------------------------------

    return {
        "raw_value": raw_text,
        "solvent": solvent,
        "value": None,
        "min_value": None,
        "max_value": None,
        "unit": None,
        "temperature": temperature,
        "temperature_unit": temperature_unit,
        "qualitative": raw_text,
        "interpretation_type": "qualitative",
    }


# ============================================================
# MULTI-OBSERVATION DISSOLUTION STATEMENTS
# ============================================================

def _split_dissolution_statement(
    text: str
) -> list[str]:

    """
    Convert:

        1 gm dissolves in 46 mL water,
        5.5 mL water at 80 °C,
        1.5 mL boiling water,
        66 mL alcohol,
        ...

    into independent observation fragments.

    The leading mass is inherited by every fragment.
    """

    match = re.match(
        r"\s*"
        r"([+-]?\d+(?:,\d{3})*(?:\.\d+)?)"
        r"\s*(g|gm|gram|grams)"
        r"\s+dissolves\s+in\s+"
        r"(.+)",
        text,
        re.IGNORECASE
    )

    if not match:
        return []

    mass = _parse_number(
        match.group(1)
    )

    mass_unit = match.group(2)

    remainder = match.group(3)

    parts = [
        part.strip()
        for part in re.split(
            r",",
            remainder
        )
        if part.strip()
    ]

    observations = []

    for part in parts:

        volume_match = re.match(
            r"([+-]?\d+(?:,\d{3})*(?:\.\d+)?)"
            r"\s*mL\s+"
            r"(.+)",
            part,
            re.IGNORECASE
        )

        if not volume_match:
            continue

        volume = _parse_number(
            volume_match.group(1)
        )

        description = (
            volume_match
            .group(2)
            .strip()
        )

        observations.append(
            {
                "mass": mass,
                "mass_unit": mass_unit,
                "volume": volume,
                "volume_unit": "mL",
                "description": description,
            }
        )

    return observations


# ============================================================
# SOLUBILITY
# ============================================================

def normalize_solubility(
    record: dict[str, Any]
) -> dict[str, Any]:

    result = _copy_common_fields(
        record
    )

    result["property_type"] = (
        "solubility"
    )

    result["observations"] = []

    for value in record.get(
        "values",
        []
    ):

        raw_value = value.get(
            "raw_value",
            ""
        )

        if not raw_value:

            result["observations"].append(
                {
                    "raw_value": "",
                    "solvent": None,
                    "value": None,
                    "min_value": None,
                    "max_value": None,
                    "unit": None,
                    "temperature": None,
                    "temperature_unit": None,
                    "qualitative": None,
                    "interpretation_type": "unknown",
                }
            )

            continue

        # ----------------------------------------------------
        # Detect parent context BEFORE splitting.
        # ----------------------------------------------------

        context = _detect_solubility_context(
            raw_value
        )

        # ----------------------------------------------------
        # Special dissolution-ratio statement.
        # ----------------------------------------------------

        dissolution_parts = (
            _split_dissolution_statement(
                raw_value
            )
        )

        if dissolution_parts:

            for part in dissolution_parts:

                temperature, temperature_unit = (
                    _extract_temperature(
                        part["description"]
                    )
                )

                solvent = _extract_solvent(
                    part["description"]
                )

                solvent = _clean_solvent(
                    solvent
                )

                if solvent is None:

                    solvent = part[
                        "description"
                    ]

                result["observations"].append(
                    {
                        "raw_value": (
                            part["description"]
                        ),
                        "solvent": solvent,
                        "value": None,
                        "min_value": None,
                        "max_value": None,
                        "unit": None,
                        "temperature": temperature,
                        "temperature_unit": (
                            temperature_unit
                        ),
                        "qualitative": None,
                        "interpretation_type": (
                            "solvent_volume_required"
                        ),
                        "mass": part["mass"],
                        "mass_unit": part[
                            "mass_unit"
                        ],
                        "volume": part[
                            "volume"
                        ],
                        "volume_unit": part[
                            "volume_unit"
                        ],
                    }
                )

            continue

        # ----------------------------------------------------
        # Semicolon-separated observations.
        # ----------------------------------------------------

        parts = [
            part.strip()
            for part in raw_value.split(";")
            if part.strip()
        ]

        for part in parts:

            observation = (
                _parse_solubility_observation(
                    part,
                    context=context
                )
            )

            result["observations"].append(
                observation
            )

    return result


# ============================================================
# MELTING POINT
# ============================================================

def normalize_melting_point(
    record: dict[str, Any]
) -> dict[str, Any]:

    result = _copy_common_fields(
        record
    )

    result["property_type"] = (
        "melting_point"
    )

    result["observations"] = []

    for value in record.get(
        "values",
        []
    ):

        result["observations"].append(
            {
                "raw_value": value.get(
                    "raw_value"
                ),
                "value": value.get(
                    "value"
                ),
                "min_value": value.get(
                    "min_value"
                ),
                "max_value": value.get(
                    "max_value"
                ),
                "unit": value.get(
                    "unit"
                ),
                "qualitative": value.get(
                    "qualitative"
                ),
            }
        )

    return result


# ============================================================
# BOILING POINT
# ============================================================

def normalize_boiling_point(
    record: dict[str, Any]
) -> dict[str, Any]:

    result = _copy_common_fields(
        record
    )

    result["property_type"] = (
        "boiling_point"
    )

    result["observations"] = []

    for value in record.get(
        "values",
        []
    ):

        result["observations"].append(
            {
                "raw_value": value.get(
                    "raw_value"
                ),
                "value": value.get(
                    "value"
                ),
                "min_value": value.get(
                    "min_value"
                ),
                "max_value": value.get(
                    "max_value"
                ),
                "unit": value.get(
                    "unit"
                ),
                "qualitative": value.get(
                    "qualitative"
                ),
            }
        )

    return result


# ============================================================
# DISPATCHER
# ============================================================

PROPERTY_NORMALIZERS = {
    "melting point": normalize_melting_point,
    "boiling point": normalize_boiling_point,
    "solubility": normalize_solubility,
}


def normalize_property_record(
    record: dict[str, Any]
) -> dict[str, Any]:

    property_name = (
        _normalize_property_name(
            record.get("property")
        )
    )

    normalizer = PROPERTY_NORMALIZERS.get(
        property_name
    )

    if normalizer is None:
        return record

    return normalizer(
        record
    )


def normalize_property_records(
    records: list[dict[str, Any]]
) -> list[dict[str, Any]]:

    return [
        normalize_property_record(
            record
        )
        for record in records
    ]

