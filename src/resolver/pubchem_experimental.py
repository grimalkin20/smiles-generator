import json
import subprocess
import time
from typing import Any


PUBCHEM_BASE_URL = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view"
)

USER_AGENT = "SMILES-Generator/1.0"


# ============================================================
# LOW-LEVEL REQUEST
# ============================================================

def _pubchem_view_request(
    url: str,
    retries: int = 3
) -> dict[str, Any]:
    """
    Request data from PubChem PUG-View using curl.exe.

    Includes retry handling for temporary HTTP errors
    such as 503 Service Unavailable.
    """

    last_error = None

    for attempt in range(1, retries + 1):

        result = subprocess.run(
            [
                "curl.exe",
                "-A",
                USER_AGENT,
                "--fail",
                "--silent",
                "--show-error",
                url,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode == 0:

            if not result.stdout.strip():
                raise RuntimeError(
                    "PubChem PUG-View returned "
                    "an empty response."
                )

            try:

                return json.loads(
                    result.stdout
                )

            except json.JSONDecodeError as error:

                raise RuntimeError(
                    "PubChem PUG-View returned "
                    "invalid JSON."
                ) from error

        error_message = (
            result.stderr.strip()
        )

        last_error = error_message

        # Retry temporary server failures.
        if "503" in error_message:

            if attempt < retries:

                wait_seconds = attempt * 3

                print(
                    f"PubChem temporarily unavailable "
                    f"(503). Retrying in "
                    f"{wait_seconds} seconds..."
                )

                time.sleep(
                    wait_seconds
                )

                continue

        # Do not retry permanent errors such as 404.
        break

    raise RuntimeError(
        "PubChem PUG-View request failed:\n"
        f"{last_error}"
    )


# ============================================================
# EXPERIMENTAL PROPERTIES
# ============================================================

def get_experimental_properties(
    cid: int
) -> dict[str, Any]:
    """
    Retrieve the Experimental Properties section
    from PubChem PUG-View.

    Returns an empty structure when PubChem does not
    provide this heading for the requested CID.
    """

    url = (
        f"{PUBCHEM_BASE_URL}/data/compound/"
        f"{cid}/JSON"
        "?heading=Experimental+Properties"
    )

    try:

        return _pubchem_view_request(
            url
        )

    except RuntimeError as error:

        error_text = str(error)

        # Some compounds do not have an
        # Experimental Properties section.
        if "404" in error_text:

            return {
                "Record": {
                    "Section": []
                }
            }

        raise


# ============================================================
# VALUE EXTRACTION
# ============================================================

def _extract_text(
    value: dict[str, Any]
) -> list[str]:
    """
    Extract human-readable values from
    PubChem's StringWithMarkup structure.
    """

    strings = []

    string_with_markup = value.get(
        "StringWithMarkup",
        []
    )

    if not isinstance(
        string_with_markup,
        list
    ):
        return strings

    for item in string_with_markup:

        if not isinstance(
            item,
            dict
        ):
            continue

        text = item.get(
            "String"
        )

        if text is not None:

            strings.append(
                str(text)
            )

    return strings


# ============================================================
# REFERENCE EXTRACTION
# ============================================================

def _extract_reference_text(
    information: dict[str, Any]
) -> list[str]:
    """
    Extract references associated with
    an experimental record.
    """

    references = []

    direct_references = information.get(
        "Reference",
        []
    )

    if isinstance(
        direct_references,
        list
    ):

        for reference in direct_references:

            if isinstance(
                reference,
                str
            ):

                if reference not in references:

                    references.append(
                        reference
                    )

    extended_references = information.get(
        "ExtendedReference",
        []
    )

    if isinstance(
        extended_references,
        list
    ):

        for reference in extended_references:

            if not isinstance(
                reference,
                dict
            ):
                continue

            citation = reference.get(
                "Citation"
            )

            if (
                citation
                and citation not in references
            ):

                references.append(
                    citation
                )

    return references


# ============================================================
# INFORMATION PARSER
# ============================================================

def _parse_information(
    heading: str,
    information: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Convert PubChem Information objects into
    our internal experimental-record format.

    IMPORTANT:
    Values remain as original text.

    We do NOT guess units, temperatures,
    ranges, or numerical values here.
    """

    records = []

    for item in information:

        if not isinstance(
            item,
            dict
        ):
            continue

        value_text = []

        value = item.get(
            "Value"
        )

        if isinstance(
            value,
            dict
        ):

            value_text = _extract_text(
                value
            )

        references = (
            _extract_reference_text(
                item
            )
        )

        name = item.get(
            "Name"
        )

        # Convert empty strings to None.
        if isinstance(
            name,
            str
        ):

            name = name.strip()

            if not name:
                name = None

        record = {
            "property": heading,

            "name": name,

            "values": value_text,

            "reference_number": item.get(
                "ReferenceNumber"
            ),

            "references": references,

            "description": item.get(
                "Description"
            ),
        }

        records.append(
            record
        )

    return records


# ============================================================
# RECURSIVE SECTION WALKER
# ============================================================

def _walk_sections(
    sections: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Recursively walk PubChem's nested
    Section structure.
    """

    results = []

    for section in sections:

        if not isinstance(
            section,
            dict
        ):
            continue

        heading = section.get(
            "TOCHeading"
        )

        information = section.get(
            "Information",
            []
        )

        if (
            heading
            and isinstance(
                information,
                list
            )
        ):

            results.extend(
                _parse_information(
                    heading,
                    information
                )
            )

        nested_sections = section.get(
            "Section",
            []
        )

        if isinstance(
            nested_sections,
            list
        ):

            results.extend(
                _walk_sections(
                    nested_sections
                )
            )

    return results


# ============================================================
# PARSE RAW RESPONSE
# ============================================================

def parse_experimental_properties(
    data: dict[str, Any]
) -> list[dict[str, Any]]:
    """
    Parse a raw PubChem PUG-View response.
    """

    if not isinstance(
        data,
        dict
    ):
        return []

    record = data.get(
        "Record",
        {}
    )

    if not isinstance(
        record,
        dict
    ):
        return []

    sections = record.get(
        "Section",
        []
    )

    if not isinstance(
        sections,
        list
    ):
        return []

    return _walk_sections(
        sections
    )


# ============================================================
# COMPLETE EXPERIMENTAL DATA
# ============================================================

def get_experimental_data(
    cid: int
) -> list[dict[str, Any]]:
    """
    Retrieve and parse all experimental data
    for a PubChem CID.
    """

    raw_data = (
        get_experimental_properties(
            cid
        )
    )

    return parse_experimental_properties(
        raw_data
    )


# ============================================================
# FILTER EXISTING RECORDS
# ============================================================

def filter_property_records(
    records: list[dict[str, Any]],
    property_name: str
) -> list[dict[str, Any]]:
    """
    Filter an already retrieved list of records.

    This function DOES NOT make another API request.
    """

    target = (
        property_name
        .strip()
        .lower()
    )

    return [
        record
        for record in records
        if record.get(
            "property",
            ""
        ).strip().lower()
        == target
    ]


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def get_property_records(
    cid: int,
    property_name: str
) -> list[dict[str, Any]]:
    """
    Retrieve records for one property.

    This function makes exactly one PubChem
    request.
    """

    records = get_experimental_data(
        cid
    )

    return filter_property_records(
        records,
        property_name
    )


# ============================================================
# AVAILABLE PROPERTY HEADINGS
# ============================================================

def get_available_properties(
    records: list[dict[str, Any]]
) -> list[str]:
    """
    Return unique experimental property headings.
    """

    headings = {
        record["property"]
        for record in records
        if record.get("property")
    }

    return sorted(
        headings
    )