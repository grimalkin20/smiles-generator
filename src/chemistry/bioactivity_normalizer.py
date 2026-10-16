
"""Normalize PubChem biological activity observations."""

import re
from typing import Any


NUMBER_PATTERN = (
    r"(?:\d+(?:\.\d*)?|\.\d+)"
    r"(?:[eE][+-]?\d+)?"
)

MEASUREMENT_PATTERN = re.compile(
    rf"^\s*(?P<qualifier><=|>=|<|>|=)?\s*"
    rf"(?P<value>{NUMBER_PATTERN})\s*$"
)


def _optional_text(value: Any) -> str | None:
    """Convert non-empty values to strings; preserve missing values."""
    if value is None:
        return None

    text = str(value).strip()
    return text or None


def _normalize_activity_type(value: Any) -> str | None:
    """Recognize common activity types without guessing from values."""
    text = _optional_text(value)

    if text is None:
        return None

    normalized = re.sub(r"[\s_-]+", "", text).lower()

    known_types = {
        "ic50": "IC50",
        "ec50": "EC50",
        "ki": "Ki",
        "kd": "Kd",
        "gi50": "GI50",
        "ac50": "AC50",
        "lc50": "LC50",
        "ld50": "LD50",
        "inhibition": "inhibition",
        "percentinhibition": "inhibition_percentage",
        "%inhibition": "inhibition_percentage",
    }

    return known_types.get(normalized, text)


def _parse_measurement(
    raw_value: Any,
) -> tuple[float | None, str | None]:
    """Parse a numeric value and comparison qualifier."""
    if raw_value is None:
        return None, None

    if isinstance(raw_value, bool):
        return None, None

    if isinstance(raw_value, (int, float)):
        return float(raw_value), "="

    text = str(raw_value).strip()

    if not text:
        return None, None

    match = MEASUREMENT_PATTERN.fullmatch(text)

    if not match:
        return None, None

    try:
        value = float(match.group("value"))
    except ValueError:
        return None, None

    return value, match.group("qualifier") or "="


def normalize_bioactivity_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    """Normalize one assay-summary record while retaining source data."""

    # Accept either our retrieval module's aliases or original PubChem columns.
    raw_value = record.get("activity_value_raw")

    if raw_value is None:
        raw_value = record.get("Activity Value [uM]")

    if raw_value is None:
        raw_value = record.get("activity_value")

    activity_value, qualifier = _parse_measurement(raw_value)

    raw_unit = _optional_text(record.get("activity_unit"))

    if raw_unit is None and _optional_text(
        record.get("Activity Value [uM]")
    ) is not None:
        raw_unit = "uM"

    raw_activity_type = (
        record.get("Activity Name")
        or record.get("activity_name")
    )

    activity_type = _normalize_activity_type(raw_activity_type)

    outcome = (
        record.get("Activity Outcome")
        or record.get("activity_outcome")
    )

    assay_id = record.get("AID") or record.get("assay_id")
    cid = record.get("CID") or record.get("compound_cid")
    sid = record.get("SID") or record.get("substance_sid")

    target_accession = (
        record.get("Target Accession")
        or record.get("target_accession")
    )

    target_gene_id = (
        record.get("Target GeneID")
        or record.get("target_gene_id")
    )

    assay_name = record.get("Assay Name") or record.get("assay_name")
    assay_type = record.get("Assay Type") or record.get("assay_type")
    pubmed_id = record.get("PubMed ID") or record.get("pubmed_id")

    return {
        "source": "PubChem",
        "compound_cid": _optional_text(cid),
        "assay_id": _optional_text(assay_id),
        "substance_sid": _optional_text(sid),
        "activity_type": activity_type,
        "activity_type_raw": _optional_text(raw_activity_type),
        "activity_value": activity_value,
        "activity_qualifier": qualifier,
        "activity_unit": raw_unit,
        "activity_value_raw": (
            str(raw_value).strip()
            if raw_value is not None
            else None
        ),
        "activity_outcome": _optional_text(outcome),
        "target_accession": _optional_text(target_accession),
        "target_gene_id": _optional_text(target_gene_id),
        "assay_name": _optional_text(assay_name),
        "assay_type": _optional_text(assay_type),
        "pubmed_id": _optional_text(pubmed_id),
        "source_record": dict(record),
    }


def normalize_bioactivity_records(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Normalize a collection of biological activity records."""
    return [
        normalize_bioactivity_record(record)
        for record in records
        if isinstance(record, dict)
    ]


