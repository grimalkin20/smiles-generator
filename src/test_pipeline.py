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


# Make sure the database and table exist.
initialize_database()


compound_name = input("Enter compound name: ").strip()

print()

if not compound_name:
    print("✗ Compound name cannot be empty.")
    exit()


# --------------------------------------------------
# STEP 1: Check local database
# --------------------------------------------------

print("Checking local database...")

compound = get_compound_by_name(compound_name)

if compound:
    print("✓ Compound found in local database.")

else:

    # --------------------------------------------------
    # STEP 2: Search PubChem
    # --------------------------------------------------

    print("Compound not found locally.")
    print("Searching PubChem...")
    print()

    try:
        data = get_compound_from_pubchem(compound_name)

        compound = extract_compound_info(data)

    except LookupError:
        print("✗ Compound not found.")
        print()
        print("Please check the chemical name and try again.")
        exit()

    except ValueError as error:
        print(f"✗ {error}")
        exit()

    except RuntimeError as error:
        print("✗ Unable to retrieve compound information.")
        print()
        print(error)
        exit()

    # --------------------------------------------------
    # STEP 3: Validate using RDKit
    # --------------------------------------------------

    print("Validating SMILES with RDKit...")

    is_valid = validate_smiles(compound.smiles)

    if not is_valid:
        print("✗ PubChem returned an invalid SMILES.")
        exit()

    compound.canonical_smiles = canonicalize_smiles(
        compound.smiles
    )

    print("✓ SMILES validated.")

    # --------------------------------------------------
    # STEP 4: Save compound
    # --------------------------------------------------

    save_compound(compound, compound_name)

    print("✓ Compound saved to local database.")


# --------------------------------------------------
# STEP 5: Display result
# --------------------------------------------------

print()
print("========================================")
print("           COMPOUND RESULT")
print("========================================")
print()

print("CID        :", compound.cid)
print("Name       :", compound.name)
print("SMILES     :", compound.smiles)
print("InChIKey   :", compound.inchikey)

print()

print("RDKit validation:", validate_smiles(compound.smiles))

if validate_smiles(compound.smiles):
    print(
        "Canonical SMILES:",
        canonicalize_smiles(compound.smiles)
    )

print()