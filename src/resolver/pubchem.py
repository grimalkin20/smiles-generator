import subprocess
import json
from urllib.parse import quote


def get_compound_from_pubchem(compound_name):
    """
    Search PubChem by chemical name.

    Returns:
        Dictionary containing PubChem response.

    Raises:
        ValueError: If the compound name is empty.
        LookupError: If PubChem cannot find the compound.
        RuntimeError: If the PubChem request fails.
    """

    compound_name = compound_name.strip()

    if not compound_name:
        raise ValueError("Compound name cannot be empty.")

    # Safely encode the user's chemical name for use in a URL.
    encoded_name = quote(compound_name, safe="")

    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
        f"compound/name/{encoded_name}/property/"
        "Title,CanonicalSMILES,IsomericSMILES,InChI,InChIKey/JSON"
    )

    result = subprocess.run(
        [
            "curl.exe",
            "-A",
            "SMILES-Generator/1.0",
            url
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"curl failed:\n{result.stderr}"
        )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            "PubChem returned invalid JSON."
        )

    if "Fault" in data:
        message = data["Fault"].get(
            "Message",
            "Compound could not be found."
        )

        raise LookupError(message)

    if "PropertyTable" not in data:
        raise RuntimeError(
            "Unexpected response received from PubChem."
        )

    return data


def extract_compound_info(data):
    """
    Extract useful chemical information from PubChem response.
    """

    properties = data["PropertyTable"]["Properties"]

    if not properties:
        raise LookupError(
            "No compound information found."
        )

    compound = properties[0]

    return {
        "cid": compound.get("CID"),
        "name": compound.get("Title"),
        "smiles": compound.get("SMILES"),
        "inchi": compound.get("InChI"),
        "inchikey": compound.get("InChIKey")
    }