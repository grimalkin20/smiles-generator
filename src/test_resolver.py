from resolver.pubchem import (
    get_compound_from_pubchem,
    extract_compound_info
)


data = get_compound_from_pubchem("aspirin")

compound = extract_compound_info(data)

print("CID:", compound["cid"])
print("Name:", compound["name"])
print("SMILES:", compound["smiles"])
print("InChI:", compound["inchi"])
print("InChIKey:", compound["inchikey"])