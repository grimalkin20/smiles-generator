
"""Normalize PubChem toxicity records without discarding source information."""

from __future__ import annotations

import re
from typing import Any


ENDPOINT_PATTERN = re.compile(
    r"\b(LD\s*50|LC\s*50|EC\s*50|IC\s*50|NOAEL|LOAEL|"
    r"NOEL|LOEL|LD\s*LO|LC\s*LO)\b",
    re.IGNORECASE,
)

NUMBER_PATTERN = re.compile(
    r"(?P<qualifier>>=|<=|>|<|≥|≤|=)?\s*"
    r"(?P<value>\d+(?:,\d{3})*(?:\.\d+)?|\.\d+)"
    r"(?:\s*(?P<range_separator>[-–])\s*"
    r"(?P<range_end>\d+(?:,\d{3})*(?:\.\d+)?|\.\d+))?"
    r"\s*(?P<unit>mg\s*/\s*kg|g\s*/\s*kg|"
    r"µg\s*/\s*kg|μg\s*/\s*kg|ug\s*/\s*kg|"
    r"mg\s*/\s*m(?:3|³)|g\s*/\s*m(?:3|³)|"
    r"ppm|ppb|mg\s*/\s*l|mg\s*/\s*L|"
    r"g\s*/\s*l|g\s*/\s*L|mg\s*/\s*mL|"
    r"g\s*/\s*mL|mg\s*/\s*cm(?:3|³)|"
    r"mg\s*/\s*day|g\s*/\s*day|"
    r"mg|g|µg|μg|ug|mL|ml|L|l)?\b",
    re.IGNORECASE,
)

ROUTE_PATTERN = re.compile(
    r"\b(oral|gavage|intravenous|i\.v\.|iv|"
    r"intraperitoneal|i\.p\.|ip|intramuscular|"
    r"subcutaneous|inhalation|dermal|topical|"
    r"skin|injection)\b",
    re.IGNORECASE,
)

SPECIES_PATTERN = re.compile(
    r"\b(mouse|mice|rat|rats|rabbit|rabbits|"
    r"dog|dogs|monkey|monkeys|mammal|mammals|"
    r"human|humans|guinea pig|guinea pigs|"
    r"hamster|hamsters)\b",
    re.IGNORECASE,
)


def _get_text(value: Any) -> str:
    """Extract text from PubChem's StringWithMarkup field."""
    if not isinstance(value, dict):
        return ""

    items = value.get("StringWithMarkup", [])
    if not isinstance(items, list):
        return ""

    parts = []
    for item in items:
        if isinstance(item, dict):
            text = item.get("String")
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())

    return " ".join(parts)


def _get_citations(info: dict[str, Any]) -> list[str]:
    """Collect available citation strings without inventing references."""
    citations: list[str] = []

    references = info.get("Reference", [])
    if isinstance(references, str):
        references = [references]

    if isinstance(references, list):
        citations.extend(
            item for item in references if isinstance(item, str) and item.strip()
        )

    extended = info.get("ExtendedReference", [])
    if isinstance(extended, dict):
        extended = [extended]

    if isinstance(extended, list):
        for item in extended:
            if not isinstance(item, dict):
                continue

            citation = item.get("Citation")
            if isinstance(citation, str) and citation.strip():
                citations.append(citation)

    # Preserve order while avoiding duplicate citation strings.
    return list(dict.fromkeys(citations))


def _classify_record(heading: str, raw_text: str, value: Any) -> str:
    """Classify records while keeping narrative and pointers distinct."""
    if isinstance(value, dict) and value.get("ExternalTableName"):
        return "external_table_pointer"

    if heading.strip().lower() == "toxicity summary":
        return "narrative_summary"

    if ENDPOINT_PATTERN.search(raw_text):
        return "toxicity_observation"

    if heading.strip().lower() in {
        "human toxicity values",
        "non-human toxicity values",
        "toxicity data",
        "lethal dose",
        "lethal concentration",
        "effect level",
    }:
        return "toxicity_text_unparsed"

    return "other"


def _extract_endpoint(raw_text: str) -> str | None:
    match = ENDPOINT_PATTERN.search(raw_text)
    if not match:
        return None

    endpoint = re.sub(r"\s+", "", match.group(1)).upper()
    return endpoint


def _extract_measurement(raw_text: str) -> dict[str, Any]:
    """Extract a conservative numeric measurement from toxicity text."""
    result: dict[str, Any] = {
        "qualifier": None,
        "value": None,
        "range_end": None,
        "unit": None,
        "species": None,
        "route": None,
        "measurement_status": "not_parsed",
    }

    endpoint_match = ENDPOINT_PATTERN.search(raw_text)
    if not endpoint_match:
        return result

    # Prefer a numeric value after the endpoint label. This avoids accidentally
    # extracting unrelated numbers that occur earlier in a sentence.
    search_text = raw_text[endpoint_match.end():]
    number_match = NUMBER_PATTERN.search(search_text)

    if not number_match:
        return result

    qualifier = number_match.group("qualifier")
    value_text = number_match.group("value")
    range_end_text = number_match.group("range_end")
    unit = number_match.group("unit")

    result["qualifier"] = qualifier
    result["value"] = float(value_text.replace(",", ""))

    if range_end_text is not None:
        result["range_end"] = float(range_end_text.replace(",", ""))
        result["measurement_status"] = "range_parsed"
    else:
        result["measurement_status"] = (
            "value_and_unit_parsed" if unit else "value_parsed_unit_missing"
        )

    if unit:
        result["unit"] = re.sub(r"\s+", "", unit).replace("³", "3")

    species_match = SPECIES_PATTERN.search(raw_text)
    if species_match:
        result["species"] = species_match.group(1).lower()

    route_match = ROUTE_PATTERN.search(raw_text)
    if route_match:
        route = route_match.group(1).lower()
        route_map = {
            "i.v.": "intravenous",
            "iv": "intravenous",
            "i.p.": "intraperitoneal",
            "ip": "intraperitoneal",
            "skin": "dermal",
        }
        result["route"] = route_map.get(route, route)

    return result


def _extract_reported_dose_mentions(raw_text: str) -> list[dict[str, Any]]:
    """Extract contextual dose mentions without treating them as validated endpoints."""
    number = r"\d+(?:,\d{3})*(?:\.\d+)?"
    unit = r"(?:mg\s*/\s*kg|g\s*/\s*kg|mg\s*/\s*day|g\s*/\s*day|mg|g|µg|μg|ug)"

    patterns = [
        (
            "estimated_ld50",
            re.compile(
                rf"estimated\s+LD\s*50\b[^.]*?"
                rf"\bbetween\s+(?P<start>{number})\s*"
                rf"(?:to|and|[-–])\s*(?P<end>{number})\s*"
                rf"(?P<unit>{unit})",
                re.IGNORECASE,
            ),
        ),
        (
            "reported_fatal_dose",
            re.compile(
                rf"\b(?:iv|i\.v\.|intravenous|oral)\s+doses?\s+of\s+"
                rf"(?P<start>{number})"
                rf"(?:\s*(?:to|and|[-–])\s*(?P<end>{number}))?"
                rf"\s*(?P<unit>{unit})",
                re.IGNORECASE,
            ),
        ),
        (
            "reported_fatal_dose",
            re.compile(
                rf"\bdoses?\s+as\s+low\s+as\s+"
                rf"(?P<start>{number})\s*(?P<unit>{unit})"
                rf"[^.]*?\bfatal",
                re.IGNORECASE,
            ),
        ),
        (
            "reported_fatal_dose",
            re.compile(
                rf"\b(?:death occurred following|fatalities? following)\b"
                rf"[^.]*?\b(?:ingestion of|dose of)\s*"
                rf"(?:approximately|about|around)?\s*"
                rf"(?P<start>{number})\s*(?P<unit>{unit})",
                re.IGNORECASE,
            ),
        ),
        (
            "toxic_dose",
            re.compile(
                rf"\btoxic\s+dose\b[^.]*?"
                rf"\b(?:around|approximately|about|of)\s+"
                rf"(?P<start>{number})\s*(?P<unit>{unit})",
                re.IGNORECASE,
            ),
        ),
        (
            "life_threatening_dose",
            re.compile(
                rf"\blife[- ]threatening\s+dose\b[^.]*?"
                rf"\b(?:range\s+from|from|of)\s+"
                rf"(?P<start>{number})\s*(?:to|and|[-–])\s*"
                rf"(?P<end>{number})\s*(?P<unit>{unit})",
                re.IGNORECASE,
            ),
        ),
    ]

    mentions: list[dict[str, Any]] = []

    for context, pattern in patterns:
        for match in pattern.finditer(raw_text):
            if context == "reported_fatal_dose":
                context_window = raw_text[
                    max(0, match.start() - 100):
                    min(len(raw_text), match.end() + 100)
                ]
                if not re.search(
                    r"\bfatal\b|\bfatalities\b|\bdeath occurred\b",
                    context_window,
                    re.IGNORECASE,
                ):
                    continue

            start = float(match.group("start").replace(",", ""))
            end_text = match.groupdict().get("end")
            end = float(end_text.replace(",", "")) if end_text else None

            normalized_unit = re.sub(
                r"\s+", "", match.group("unit")
            )

            # Retain a short source excerpt so each extraction is auditable.
            excerpt_start = max(0, match.start() - 80)
            excerpt_end = min(len(raw_text), match.end() + 80)

            mentions.append({
                "context": context,
                "value": start,
                "range_end": end,
                "unit": normalized_unit,
                "source_excerpt": raw_text[excerpt_start:excerpt_end],
            })

    # Remove duplicate extractions while preserving discovery order.
    unique_mentions = []
    seen = set()

    for mention in mentions:
        key = (
            mention["context"],
            mention["value"],
            mention["range_end"],
            mention["unit"],
        )
        if key not in seen:
            seen.add(key)
            unique_mentions.append(mention)

    return unique_mentions


def normalize_toxicity_record(
    cid: int,
    heading: str,
    info: dict[str, Any],
) -> dict[str, Any]:
    """Normalize one PubChem toxicity Information entry."""
    if not isinstance(info, dict):
        raise TypeError("info must be a dictionary")

    value = info.get("Value")
    raw_text = _get_text(value)

    record_type = _classify_record(heading, raw_text, value)
    endpoint = _extract_endpoint(raw_text)

    measurement = {
        "qualifier": None,
        "value": None,
        "range_end": None,
        "unit": None,
        "species": None,
        "route": None,
        "measurement_status": "not_applicable",
    }

    if record_type == "toxicity_observation":
        measurement = _extract_measurement(raw_text)

    external_table = None
    if isinstance(value, dict):
        external_table = value.get("ExternalTableName")

    return {
        "cid": cid,
        "heading": heading,
        "reference_number": info.get("ReferenceNumber"),
        "name": info.get("Name"),
        "description": info.get("Description"),
        "record_type": record_type,
        "endpoint": endpoint,
        "raw_text": raw_text,
        "qualifier": measurement["qualifier"],
        "value": measurement["value"],
        "range_end": measurement["range_end"],
        "unit": measurement["unit"],
        "species": measurement["species"],
        "route": measurement["route"],
        "measurement_status": measurement["measurement_status"],
        "citations": _get_citations(info),
        "external_table_name": external_table,
        "reported_dose_mentions": (
            _extract_reported_dose_mentions(raw_text)
            if record_type in {
                "narrative_summary",
                "toxicity_text_unparsed",
            }
            else []
        ),
    }


def normalize_toxicity_section(
    cid: int,
    section: dict[str, Any],
) -> list[dict[str, Any]]:
    """Normalize all Information entries in one PubChem section."""
    heading = section.get("TOCHeading", "Unknown")
    information = section.get("Information", [])

    if isinstance(information, dict):
        information = [information]

    if not isinstance(information, list):
        return []

    return [
        normalize_toxicity_record(cid, heading, info)
        for info in information
        if isinstance(info, dict)
    ]


