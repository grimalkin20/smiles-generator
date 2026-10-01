import json
import subprocess


PUBCHEM_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view"
USER_AGENT = "SMILES-Generator/1.0"


def get_experimental_properties(cid):
    """
    Retrieve the complete Experimental Properties
    section from PubChem PUG-View.
    """

    url = (
        f"{PUBCHEM_BASE_URL}/data/compound/"
        f"{cid}/JSON"
        "?heading=Experimental+Properties"
    )

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
        return json.loads(result.stdout)

    except json.JSONDecodeError:
        print("Raw PubChem response:")
        print(result.stdout)

        raise RuntimeError(
            "PubChem returned invalid JSON."
        )


def main():

    cid = 2244
    compound_name = "Aspirin"

    print("=" * 70)
    print("          PUBCHEM EXPERIMENTAL DATA TEST")
    print("=" * 70)

    print(f"\nCompound : {compound_name}")
    print(f"CID      : {cid}")

    print("\n[1] Retrieving Experimental Properties...")
    print("-" * 50)

    try:

        data = get_experimental_properties(cid)

        print("✓ Experimental data retrieved")

    except Exception as error:

        print("✗ Request failed")
        print(error)

        return

    print("\n[2] Inspecting response structure")
    print("-" * 50)

    print(
        f"Top-level keys: {list(data.keys())}"
    )

    if "Record" in data:

        record = data["Record"]

        print(
            f"Record keys: {list(record.keys())}"
        )

    print("\n[3] Raw JSON structure")
    print("-" * 50)

    print(
        json.dumps(
            data,
            indent=2
        )
    )

    print("\n" + "=" * 70)
    print("       EXPERIMENTAL DATA TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
