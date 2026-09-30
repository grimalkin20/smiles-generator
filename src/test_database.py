from database.sqlite_db import (
    initialize_database,
    save_compound,
    get_compound_by_name
)

from models.compound import Compound


initialize_database()

test_compound = Compound(
    cid=2244,
    name="Aspirin",
    smiles="CC(=O)OC1=CC=CC=C1C(=O)O",
    inchi="InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)",
    inchikey="BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
)


save_compound(test_compound)

print("Compound saved.")

compound = get_compound_by_name("aspirin")

if compound:
    print()
    print("Compound found in database!")
    print("CID      :", compound.cid)
    print("Name     :", compound.name)
    print("SMILES   :", compound.smiles)
    print("InChIKey :", compound.inchikey)
else:
    print("Compound not found.")