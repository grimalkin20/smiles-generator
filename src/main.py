from resolver.pubchem import (
    get_compound_from_pubchem,
    extract_compound_info
)

from chemistry.rdkit_utils import (
    validate_smiles,
    canonicalize_smiles
)

from database.sqlite_db import (
    initialize_database,
    get_compound_by_name,
    save_compound
)


def display_compound(compound):
    """
    Display compound information in the terminal.
    """

    print()
    print("========================================")
    print("           COMPOUND RESULT")
    print("========================================")
    print()

    print("CID        :", compound.cid)
    print("Name       :", compound.name)
    print("SMILES     :", compound.smiles)
    print("Canonical  :", compound.canonical_smiles)
    print("InChIKey   :", compound.inchikey)

    print()

    print(
        "RDKit validation:",
        validate_smiles(compound.smiles)
    )

    print()


def search_compound(compound_name):
    """
    Search for a compound locally first.
    If it is not found, search PubChem.

    Returns:
        Compound object if successful.
        None if the compound cannot be found.
    """

    # --------------------------------------------------
    # STEP 1: Check local database
    # --------------------------------------------------

    print("Checking local database...")

    compound = get_compound_by_name(compound_name)

    if compound:

        print("✓ Compound found in local database.")

        return compound

    # --------------------------------------------------
    # STEP 2: Search PubChem
    # --------------------------------------------------

    print("Compound not found locally.")
    print("Searching PubChem...")
    print()

    try:

        data = get_compound_from_pubchem(
            compound_name
        )

        compound = extract_compound_info(data)

    except LookupError:

        print("✗ Compound not found.")
        print()
        print(
            "Please check the chemical name "
            "and try again."
        )

        return None

    except ValueError as error:

        print(f"✗ {error}")

        return None

    except RuntimeError as error:

        print(
            "✗ Unable to retrieve compound information."
        )

        print()
        print(error)

        return None

    # --------------------------------------------------
    # STEP 3: Validate SMILES using RDKit
    # --------------------------------------------------

    print("Validating SMILES with RDKit...")

    is_valid = validate_smiles(
        compound.smiles
    )

    if not is_valid:

        print(
            "✗ PubChem returned an invalid SMILES."
        )

        return None

    print("✓ SMILES validated.")

    # --------------------------------------------------
    # STEP 4: Generate canonical SMILES
    # --------------------------------------------------

    compound.canonical_smiles = (
        canonicalize_smiles(
            compound.smiles
        )
    )

    # --------------------------------------------------
    # STEP 5: Save compound locally
    # --------------------------------------------------

    save_compound(
        compound,
        compound_name
    )

    print("✓ Compound saved to local database.")

    return compound


def main():
    """
    Main application entry point.
    """

    # --------------------------------------------------
    # Initialize database
    # --------------------------------------------------

    initialize_database()

    print()
    print("========================================")
    print("        CHEMINFORMATICS TOOL")
    print("        NAME → SMILES RESOLVER")
    print("========================================")
    print()

    # --------------------------------------------------
    # Get user input
    # --------------------------------------------------

    compound_name = input(
        "Enter compound name: "
    ).strip()

    print()

    # --------------------------------------------------
    # Validate input
    # --------------------------------------------------

    if not compound_name:

        print("✗ Compound name cannot be empty.")

        return

    # --------------------------------------------------
    # Search compound
    # --------------------------------------------------

    compound = search_compound(
        compound_name
    )

    # --------------------------------------------------
    # Display result
    # --------------------------------------------------

    if compound:

        display_compound(
            compound
        )


# ------------------------------------------------------
# PROGRAM ENTRY POINT
# ------------------------------------------------------

if __name__ == "__main__":
    main()
