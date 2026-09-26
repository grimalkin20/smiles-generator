from chemistry.rdkit_utils import (
    smiles_to_molecule,
    validate_smiles,
    canonicalize_smiles
)


smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"


print("Original SMILES:")
print(smiles)

print()

print("Valid:")
print(validate_smiles(smiles))

print()

print("Canonical SMILES:")
print(canonicalize_smiles(smiles))

print()

print("Molecule object:")
print(smiles_to_molecule(smiles))