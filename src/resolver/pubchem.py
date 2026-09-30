import json
import re
import subprocess
from urllib.parse import quote

from models.compound import Compound


PUBCHEM_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
USER_AGENT = "SMILES-Generator/1.0"


# ============================================================
# LOW-LEVEL PUBCHEM REQUEST
# ============================================================

def _pubchem_request(url):
    """
    Send a request to PubChem using curl.exe.
    """

    result = subprocess.run(
        ["curl.exe", "-A", USER_AGENT, url],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"PubChem request failed:\n{result.stderr}"
        )

    if not result.stdout.strip():
        raise RuntimeError(
            "PubChem returned an empty response."
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
            "Unknown PubChem error."
        )
        raise LookupError(message)

    return data


# ============================================================
# BASIC COMPOUND LOOKUP
# ============================================================

def get_compound_from_pubchem(compound_name):
    """
    Search PubChem by compound name.
    """

    compound_name = compound_name.strip()

    if not compound_name:
        raise ValueError(
            "Compound name cannot be empty."
        )

    encoded_name = quote(
        compound_name,
        safe=""
    )

    url = (
        f"{PUBCHEM_BASE_URL}/compound/name/"
        f"{encoded_name}/property/"
        "Title,"
        "SMILES,"
        "ConnectivitySMILES,"
        "InChI,"
        "InChIKey/"
        "JSON"
    )

    data = _pubchem_request(url)

    if "PropertyTable" not in data:
        raise RuntimeError(
            "Unexpected response received from PubChem."
        )

    return data


# ============================================================
# EXTRACT BASIC COMPOUND INFORMATION
# ============================================================

def extract_compound_info(data):
    """
    Convert PubChem response into Compound object.
    """

    properties = data["PropertyTable"]["Properties"]

    if not properties:
        raise LookupError(
            "No compound information found."
        )

    compound = properties[0]

    return Compound(
        cid=compound.get("CID"),
        name=compound.get("Title"),

        smiles=(
            compound.get("SMILES")
            or compound.get("ConnectivitySMILES")
        ),

        inchi=compound.get("InChI"),
        inchikey=compound.get("InChIKey"),

        canonical_smiles=compound.get(
            "ConnectivitySMILES"
        ),

        isomeric_smiles=compound.get(
            "SMILES"
        )
    )


# ============================================================
# PUBCHEM MOLECULAR PROPERTIES
# ============================================================

def get_pubchem_properties(cid):
    """
    Retrieve scientific molecular properties from PubChem.
    """

    if not cid:
        raise ValueError(
            "PubChem CID is required."
        )

    properties = [
        "MolecularFormula",
        "MolecularWeight",
        "ExactMass",
        "MonoisotopicMass",
        "HeavyAtomCount",
        "Charge",
        "HBondDonorCount",
        "HBondAcceptorCount",
        "RotatableBondCount",
        "TPSA",
        "XLogP",
        "Complexity",
        "IUPACName"
    ]

    property_string = ",".join(properties)

    url = (
        f"{PUBCHEM_BASE_URL}/compound/cid/"
        f"{cid}/property/"
        f"{property_string}/JSON"
    )

    data = _pubchem_request(url)

    try:
        return data[
            "PropertyTable"
        ][
            "Properties"
        ][0]

    except (KeyError, IndexError, TypeError):
        raise RuntimeError(
            "PubChem returned no molecular properties."
        )


# ============================================================
# PUBCHEM SYNONYMS
# ============================================================

def get_pubchem_synonyms(cid):
    """
    Retrieve synonyms associated with a PubChem CID.
    """

    if not cid:
        raise ValueError(
            "PubChem CID is required."
        )

    url = (
        f"{PUBCHEM_BASE_URL}/compound/cid/"
        f"{cid}/synonyms/JSON"
    )

    data = _pubchem_request(url)

    try:
        return data[
            "InformationList"
        ][
            "Information"
        ][0][
            "Synonym"
        ]

    except (KeyError, IndexError, TypeError):
        return []


# ============================================================
# CAS NUMBER EXTRACTION
# ============================================================

def extract_cas_numbers(synonyms):
    """
    Extract CAS Registry Numbers from PubChem synonyms.
    """

    cas_pattern = re.compile(
        r"^\d{2,7}-\d{2}-\d$"
    )

    cas_numbers = []

    for synonym in synonyms:
        synonym = synonym.strip()

        if cas_pattern.match(synonym):
            cas_numbers.append(synonym)

    return list(
        dict.fromkeys(cas_numbers)
    )


def get_pubchem_cas(cid):
    """
    Retrieve CAS numbers from PubChem.
    """

    synonyms = get_pubchem_synonyms(cid)

    return extract_cas_numbers(
        synonyms
    )


# ============================================================
# PUBCHEM IUPAC NAME
# ============================================================

def get_pubchem_iupac_name(cid):
    """
    Retrieve IUPAC name for a PubChem CID.
    """

    if not cid:
        raise ValueError(
            "PubChem CID is required."
        )

    url = (
        f"{PUBCHEM_BASE_URL}/compound/cid/"
        f"{cid}/property/IUPACName/JSON"
    )

    data = _pubchem_request(url)

    try:
        return data[
            "PropertyTable"
        ][
            "Properties"
        ][0].get(
            "IUPACName"
        )

    except (KeyError, IndexError, TypeError):
        return None


# ============================================================
# PUBCHEM 3D RECORD
# ============================================================

def get_pubchem_3d(cid):
    """
    Retrieve PubChem 3D record.
    """

    if not cid:
        raise ValueError(
            "PubChem CID is required."
        )

    url = (
        f"{PUBCHEM_BASE_URL}/compound/cid/"
        f"{cid}/record/JSON"
        "?record_type=3d"
    )

    return _pubchem_request(url)


# ============================================================
# PUBCHEM CROSS-REFERENCES
# ============================================================

def get_pubchem_cross_references(cid):
    """
    Retrieve PubChem cross-reference information.
    """

    if not cid:
        raise ValueError(
            "PubChem CID is required."
        )

    url = (
        f"{PUBCHEM_BASE_URL}/compound/cid/"
        f"{cid}/xrefs/JSON"
    )

    return _pubchem_request(url)


# ============================================================
# COMPLETE PUBCHEM SCIENTIFIC DATA
# ============================================================

def get_complete_pubchem_data(cid):
    """
    Retrieve the main scientific data currently supported.
    """

    properties = get_pubchem_properties(cid)

    synonyms = get_pubchem_synonyms(cid)

    cas_numbers = extract_cas_numbers(
        synonyms
    )

    iupac_name = properties.get(
        "IUPACName"
    )

    if not iupac_name:
        iupac_name = get_pubchem_iupac_name(
            cid
        )

    return {
        "properties": properties,
        "synonyms": synonyms,
        "cas_numbers": cas_numbers,
        "iupac_name": iupac_name
    }