
"""Retrieve and parse PubChem compound assay summaries."""

import json
import re
import subprocess
import time
from typing import Any
from urllib.error import URLError


BASE_URL = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
    "compound/cid/{cid}/assaysummary/JSON"
)


def _parse_activity_value(raw_value: Any) -> float | None:
    """Parse a simple numeric activity value without guessing units."""
    if raw_value is None:
        return None

    text = str(raw_value).strip()

    if not text:
        return None

    try:
        return float(text)
    except ValueError:
        return None


def parse_assay_summary(
    payload: dict[str, Any],
    cid: int | None = None,
) -> dict[str, Any]:
    """Convert PubChem's Table/Columns/Row response to dictionaries."""

    table = payload.get("Table", {})
    columns = table.get("Columns", {}).get("Column", [])
    rows = table.get("Row", [])

    if not isinstance(columns, list) or not isinstance(rows, list):
        raise ValueError("Unexpected PubChem assay-summary schema.")

    records = []

    for row in rows:
        cells = row.get("Cell", [])

        if not isinstance(cells, list):
            continue

        # Map each cell to its original column label.
        record = {
            str(columns[index]): value
            for index, value in enumerate(cells)
            if index < len(columns)
        }

        raw_activity = record.get("Activity Value [uM]")

        record["activity_value_raw"] = raw_activity
        record["activity_value"] = _parse_activity_value(raw_activity)
        record["activity_unit"] = (
            "uM"
            if raw_activity is not None
            and str(raw_activity).strip()
            else None
        )

        # Preserve empty source fields; provide convenient normalized aliases.
        record["assay_id"] = record.get("AID") or None
        record["compound_cid"] = record.get("CID") or None
        record["substance_sid"] = record.get("SID") or None
        record["activity_outcome"] = (
            record.get("Activity Outcome") or None
        )
        record["target_accession"] = (
            record.get("Target Accession") or None
        )
        record["target_gene_id"] = (
            record.get("Target GeneID") or None
        )
        record["activity_name"] = (
            record.get("Activity Name") or None
        )
        record["assay_name"] = record.get("Assay Name") or None
        record["assay_type"] = record.get("Assay Type") or None
        record["pubmed_id"] = record.get("PubMed ID") or None

        records.append(record)

    return {
        "cid": cid,
        "source": "PubChem PUG REST assay summary",
        "record_count": len(records),
        "records": records,
    }


def get_bioactivity_summary(
    cid: int,
    retries: int = 3,
    timeout: int = 90,
) -> dict[str, Any]:
    """Fetch and parse a compound's PubChem assay summary."""

    if not isinstance(cid, int) or isinstance(cid, bool) or cid <= 0:
        raise ValueError("CID must be a positive integer.")

    if retries < 1:
        raise ValueError("retries must be at least 1.")

    url = BASE_URL.format(cid=cid)
    last_error = None

    for attempt in range(retries):
        try:
            response = subprocess.run(
                [
                    "curl.exe",
                    "-sS",
                    "--max-time",
                    str(timeout),
                    "-w",
                    "\n%{http_code}",
                    url,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                timeout=timeout + 10,
            )

            if response.returncode != 0:
                last_error = RuntimeError(
                    response.stderr.strip()
                    or f"curl exited with code {response.returncode}"
                )
            else:
                body, _, status_text = response.stdout.rpartition("\n")

                try:
                    status = int(status_text.strip())
                except ValueError:
                    status = 0

                if status == 200:
                    payload = json.loads(body)
                    return parse_assay_summary(payload, cid=cid)

                last_error = RuntimeError(
                    f"PubChem returned HTTP {status} for CID {cid}."
                )

                # Retry only transient server/rate-limit responses.
                if status not in (429, 500, 502, 503, 504):
                    raise last_error

        except (subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            last_error = exc
        except FileNotFoundError as exc:
            raise RuntimeError(
                "curl.exe was not found. Verify curl is available in PATH."
            ) from exc

        if attempt < retries - 1:
            time.sleep(2 ** attempt)

    raise RuntimeError(
        f"Could not retrieve assay summary for CID {cid} "
        f"after {retries} attempts: {last_error}"
    ) from last_error
