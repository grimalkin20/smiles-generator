from resolver.pubchem import (
    get_compound_from_pubchem,
    extract_compound_info
)

from chemistry.rdkit_utils import (
    validate_smiles,
    canonicalize_smiles,
    calculate_properties
)

from database.sqlite_db import (
    initialize_database,
    get_compound_by_name,
    get_all_compounds,
    save_compound
)


def calculate_compound_properties(compound):
    """
    Calculate molecular properties and attach them
    to the Compound object.
    """

    properties = calculate_properties(
        compound.smiles
    )

    compound.molecular_formula = (
        properties["molecular_formula"]
    )

    compound.molecular_weight = (
        properties["molecular_weight"]
    )

    compound.logp = (
        properties["logp"]
    )

    compound.tpsa = (
        properties["tpsa"]
    )

    compound.h_bond_donors = (
        properties["h_bond_donors"]
    )

    compound.h_bond_acceptors = (
        properties["h_bond_acceptors"]
    )

    compound.rotatable_bonds = (
        properties["rotatable_bonds"]
    )

    compound.ring_count = (
        properties["ring_count"]
    )

    compound.heavy_atoms = (
        properties["heavy_atoms"]
    )


def display_compound(compound):
    """
    Display detailed information about a compound.
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

    print("----------- MOLECULAR PROPERTIES -----------")
    print()

    print(
        "Formula            :",
        compound.molecular_formula
    )

    print(
        "Molecular Weight   :",
        f"{compound.molecular_weight:.3f}"
    )

    print(
        "LogP               :",
        f"{compound.logp:.4f}"
    )

    print(
        "TPSA               :",
        f"{compound.tpsa:.2f}"
    )

    print(
        "H-Bond Donors      :",
        compound.h_bond_donors
    )

    print(
        "H-Bond Acceptors   :",
        compound.h_bond_acceptors
    )

    print(
        "Rotatable Bonds    :",
        compound.rotatable_bonds
    )

    print(
        "Ring Count         :",
        compound.ring_count
    )

    print(
        "Heavy Atoms        :",
        compound.heavy_atoms
    )

    print()

    print(
        "RDKit validation:",
        validate_smiles(compound.smiles)
    )

    print()


def search_compound(compound_name):
    """
    Search for a compound locally first.

    If the compound is not found locally,
    search PubChem.

    Molecular properties are calculated after
    obtaining the compound structure.

    Returns:
        Compound object if successful.
        None if not found.
    """

    # --------------------------------------------------
    # STEP 1: Check local database
    # --------------------------------------------------

    print()
    print("Checking local database...")

    compound = get_compound_by_name(
        compound_name
    )

    if compound:

        print(
            "✓ Compound found in local database."
        )

        # Calculate properties for the
        # locally retrieved compound.
        calculate_compound_properties(
            compound
        )

        return compound

    # --------------------------------------------------
    # STEP 2: Search PubChem
    # --------------------------------------------------

    print(
        "Compound not found locally."
    )

    print("Searching PubChem...")
    print()

    try:

        data = get_compound_from_pubchem(
            compound_name
        )

        compound = extract_compound_info(
            data
        )

    except LookupError:

        print("✗ Compound not found.")
        print()

        print(
            "Please check the chemical name "
            "and try again."
        )

        return None

    except ValueError as error:

        print(
            f"✗ {error}"
        )

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

    print(
        "Validating SMILES with RDKit..."
    )

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
    # STEP 5: Calculate molecular properties
    # --------------------------------------------------

    print(
        "Calculating molecular properties..."
    )

    calculate_compound_properties(
        compound
    )

    print(
        "✓ Molecular properties calculated."
    )

    # --------------------------------------------------
    # STEP 6: Save compound
    # --------------------------------------------------

    save_compound(
        compound,
        compound_name
    )

    print(
        "✓ Compound saved to local database."
    )

    return compound


def list_saved_compounds():
    """
    Display all compounds stored locally.
    """

    compounds = get_all_compounds()

    print()
    print("========================================")
    print("         SAVED COMPOUNDS")
    print("========================================")
    print()

    if not compounds:

        print("No compounds saved yet.")
        print()

        return

    print(
        f"{'No.':<5}"
        f"{'Name':<45}"
        f"{'CID':<12}"
        f"InChIKey"
    )

    print("-" * 100)

    for index, compound in enumerate(
        compounds,
        start=1
    ):

        print(
            f"{index:<5}"
            f"{compound.name[:43]:<45}"
            f"{str(compound.cid):<12}"
            f"{compound.inchikey}"
        )

    print()

    print(
        f"Total compounds: {len(compounds)}"
    )

    print()


def show_menu():
    """
    Display the main application menu.
    """

    print()
    print("========================================")
    print("        CHEMINFORMATICS TOOL")
    print("========================================")
    print()

    print("1. Search compound")
    print("2. List saved compounds")
    print("3. Exit")

    print()


def main():
    """
    Main application entry point.
    """

    # Make sure the database exists.
    initialize_database()

    while True:

        show_menu()

        choice = input(
            "Select an option: "
        ).strip()

        # --------------------------------------------------
        # SEARCH
        # --------------------------------------------------

        if choice == "1":

            print()

            compound_name = input(
                "Enter compound name: "
            ).strip()

            if not compound_name:

                print(
                    "✗ Compound name cannot be empty."
                )

                continue

            compound = search_compound(
                compound_name
            )

            if compound:

                display_compound(
                    compound
                )

        # --------------------------------------------------
        # LIST
        # --------------------------------------------------

        elif choice == "2":

            list_saved_compounds()

        # --------------------------------------------------
        # EXIT
        # --------------------------------------------------

        elif choice == "3":

            print()

            print(
                "Exiting Chemoinformatics Tool..."
            )

            print()

            break

        # --------------------------------------------------
        # INVALID OPTION
        # --------------------------------------------------

        else:

            print()

            print(
                "✗ Invalid option."
            )

            print(
                "Please select 1, 2, or 3."
            )


if __name__ == "__main__":
    main()


