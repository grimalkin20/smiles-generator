from chemistry.rdkit_utils import calculate_properties


smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"

properties = calculate_properties(smiles)


print()
print("========================================")
print("       MOLECULAR PROPERTIES")
print("========================================")
print()

print(
    "Molecular Formula :",
    properties["molecular_formula"]
)

print(
    "Molecular Weight  :",
    properties["molecular_weight"]
)

print(
    "LogP              :",
    properties["logp"]
)

print(
    "TPSA              :",
    properties["tpsa"]
)

print(
    "H-Bond Donors     :",
    properties["h_bond_donors"]
)

print(
    "H-Bond Acceptors  :",
    properties["h_bond_acceptors"]
)

print(
    "Rotatable Bonds   :",
    properties["rotatable_bonds"]
)

print(
    "Ring Count        :",
    properties["ring_count"]
)

print(
    "Heavy Atoms       :",
    properties["heavy_atoms"]
)

print()

