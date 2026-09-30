from resolver.pubchem import (
    get_compound_from_pubchem,
    extract_compound_info,
    get_pubchem_properties,
    get_pubchem_synonyms,
    get_pubchem_cas,
    get_pubchem_3d,
    get_pubchem_cross_references
)


def main():

    compound_name = "aspirin"

    print("=" * 60)
    print("          PUBCHEM SCIENTIFIC DATA TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Basic compound lookup
    # --------------------------------------------------------

    print("\n[1] Searching PubChem...")

    data = get_compound_from_pubchem(
        compound_name
    )

    compound = extract_compound_info(
        data
    )

    print("✓ Compound found")

    print("\nBasic Identity")
    print("-" * 40)

    print(f"CID              : {compound.cid}")
    print(f"Name             : {compound.name}")
    print(f"Canonical SMILES : {compound.canonical_smiles}")
    print(f"Isomeric SMILES  : {compound.isomeric_smiles}")
    print(f"InChI            : {compound.inchi}")
    print(f"InChIKey         : {compound.inchikey}")

    # --------------------------------------------------------
    # 2. PubChem properties
    # --------------------------------------------------------

    print("\n[2] Retrieving PubChem properties...")

    properties = get_pubchem_properties(
        compound.cid
    )

    print("✓ Properties retrieved")

    print("\nPubChem Properties")
    print("-" * 40)

    for key, value in properties.items():

        print(
            f"{key:<30}: {value}"
        )

    # --------------------------------------------------------
    # 3. Synonyms
    # --------------------------------------------------------

    print("\n[3] Retrieving synonyms...")

    synonyms = get_pubchem_synonyms(
        compound.cid
    )

    print(
        f"✓ {len(synonyms)} synonyms found"
    )

    print("\nFirst 20 synonyms:")

    for synonym in synonyms[:20]:

        print(
            f"  - {synonym}"
        )

    # --------------------------------------------------------
    # 4. CAS numbers
    # --------------------------------------------------------

    print("\n[4] Extracting CAS numbers...")

    cas_numbers = get_pubchem_cas(
        compound.cid
    )

    print("CAS numbers:")

    if cas_numbers:

        for cas in cas_numbers:
            print(
                f"  - {cas}"
            )

    else:

        print(
            "  No CAS number found in PubChem synonyms."
        )

    # --------------------------------------------------------
    # 5. 3D record
    # --------------------------------------------------------

    print("\n[5] Testing PubChem 3D record...")

    try:

        data_3d = get_pubchem_3d(
            compound.cid
        )

        print(
            "✓ 3D record retrieved"
        )

        print(
            f"Response size: "
            f"{len(str(data_3d))} characters"
        )

    except Exception as error:

        print(
            f"⚠ 3D record unavailable: {error}"
        )

    # --------------------------------------------------------
    # 6. Cross references
    # --------------------------------------------------------

    print("\n[6] Testing cross references...")

    try:

        xrefs = get_pubchem_cross_references(
            compound.cid
        )

        print(
            "✓ Cross-reference record retrieved"
        )

        print(
            f"Response size: "
            f"{len(str(xrefs))} characters"
        )

    except Exception as error:

        print(
            f"⚠ Cross-reference data unavailable: {error}"
        )

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
