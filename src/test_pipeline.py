from resolver.pubchem import (
    get_compound_from_pubchem,
    extract_compound_info
)

from chemistry.rdkit_utils import (
    validate_smiles,
    canonicalize_smiles
)


compound_name = input("Enter compound name: ").strip()

print()

if not compound_name:
    print("✗ Compound name cannot be empty.")
    exit()


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


print("✓ Compound found!")
print()

print("CID        :", compound.cid)
print("Name       :", compound.name)
print("SMILES     :", compound.smiles)
print("InChIKey   :", compound.inchikey)
print()


is_valid = validate_smiles(compound.smiles)

print("RDKit validation:", is_valid)

if is_valid:
    canonical_smiles = canonicalize_smiles(compound.smiles)

    print("Canonical SMILES:", canonical_smiles)
else:
    print("✗ The SMILES returned by PubChem is invalid.")