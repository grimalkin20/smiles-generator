from chemistry.rdkit_utils import (
    validate_smiles,
    canonicalize_smiles,
    generate_isomeric_smiles,
    generate_inchi,
    generate_inchikey,
    calculate_scientific_properties,
    calculate_3d_properties
)


def main():

    # ========================================================
    # TEST COMPOUND
    # ========================================================

    compound_name = "Aspirin"

    smiles = (
        "CC(=O)OC1=CC=CC=C1C(=O)O"
    )

    print("=" * 70)
    print("           RDKit SCIENTIFIC PROPERTIES TEST")
    print("=" * 70)

    print(f"\nCompound : {compound_name}")
    print(f"SMILES   : {smiles}")

    # ========================================================
    # 1. SMILES VALIDATION
    # ========================================================

    print("\n[1] SMILES Validation")
    print("-" * 50)

    is_valid = validate_smiles(smiles)

    print(
        f"Valid SMILES : {is_valid}"
    )

    if not is_valid:
        print(
            "\nERROR: Invalid SMILES."
        )
        return

    # ========================================================
    # 2. CHEMICAL IDENTIFIERS
    # ========================================================

    print("\n[2] Chemical Identifiers")
    print("-" * 50)

    canonical_smiles = canonicalize_smiles(
        smiles
    )

    isomeric_smiles = generate_isomeric_smiles(
        smiles
    )

    inchi = generate_inchi(
        smiles
    )

    inchikey = generate_inchikey(
        smiles
    )

    print(
        f"Canonical SMILES : {canonical_smiles}"
    )

    print(
        f"Isomeric SMILES  : {isomeric_smiles}"
    )

    print(
        f"InChI            : {inchi}"
    )

    print(
        f"InChIKey         : {inchikey}"
    )

    # ========================================================
    # 3. BASIC SCIENTIFIC PROPERTIES
    # ========================================================

    print("\n[3] Basic Molecular Properties")
    print("-" * 50)

    properties = calculate_scientific_properties(
        smiles
    )

    print(
        f"Molecular Formula : "
        f"{properties['molecular_formula']}"
    )

    print(
        f"Molecular Weight   : "
        f"{properties['molecular_weight']:.3f}"
    )

    print(
        f"Exact Mass         : "
        f"{properties['exact_mass']:.6f}"
    )

    print(
        f"Heavy Atom Count   : "
        f"{properties['heavy_atoms']}"
    )

    print(
        f"Total Atom Count   : "
        f"{properties['total_atoms']}"
    )

    print(
        f"Formal Charge      : "
        f"{properties['formal_charge']}"
    )

    print(
        f"Fraction CSP3      : "
        f"{properties['fraction_csp3']:.4f}"
    )

    print(
        f"Stereocenter Count : "
        f"{properties['stereocenter_count']}"
    )

    # ========================================================
    # 4. PHYSICOCHEMICAL DESCRIPTORS
    # ========================================================

    print("\n[4] Physicochemical Descriptors")
    print("-" * 50)

    print(
        f"TPSA               : "
        f"{properties['tpsa']:.2f}"
    )

    print(
        f"LogP               : "
        f"{properties['logp']:.4f}"
    )

    print(
        f"Molar Refractivity : "
        f"{properties['molar_refractivity']:.4f}"
    )

    print(
        f"H-Bond Donors      : "
        f"{properties['h_bond_donors']}"
    )

    print(
        f"H-Bond Acceptors   : "
        f"{properties['h_bond_acceptors']}"
    )

    print(
        f"Rotatable Bonds    : "
        f"{properties['rotatable_bonds']}"
    )

    # ========================================================
    # 5. RING INFORMATION
    # ========================================================

    print("\n[5] Ring Information")
    print("-" * 50)

    print(
        f"Total Rings        : "
        f"{properties['ring_count']}"
    )

    print(
        f"Aromatic Rings     : "
        f"{properties['aromatic_ring_count']}"
    )

    print(
        f"Aliphatic Rings    : "
        f"{properties['aliphatic_ring_count']}"
    )

    # ========================================================
    # 6. DRUG-LIKENESS
    # ========================================================

    print("\n[6] Drug-Likeness")
    print("-" * 50)

    print(
        f"Lipinski Rule of 5 : "
        f"{properties['lipinski_pass']}"
    )

    print(
        f"Veber Criteria      : "
        f"{properties['veber_pass']}"
    )

    print(
        f"QED Score           : "
        f"{properties['qed_score']:.4f}"
    )

    # ========================================================
    # 7. PAINS
    # ========================================================

    print("\n[7] PAINS Filter")
    print("-" * 50)

    print(
        f"PAINS Alert : "
        f"{properties['pains_alert']}"
    )

    if properties["pains_alerts"]:

        print("PAINS Matches:")

        for alert in properties["pains_alerts"]:

            print(
                f"  - {alert}"
            )

    else:

        print(
            "PAINS Matches : None"
        )

    # ========================================================
    # 8. 3D PROPERTIES
    # ========================================================

    print("\n[8] 3D Molecular Properties")
    print("-" * 50)

    try:

        properties_3d = calculate_3d_properties(
            smiles
        )

        print(
            f"3D Conformer Generated : "
            f"{properties_3d['has_3d_conformer']}"
        )

        print(
            f"Radius of Gyration     : "
            f"{properties_3d['radius_of_gyration']:.4f}"
        )

        print(
            f"Asphericity            : "
            f"{properties_3d['asphericity']:.4f}"
        )

        print(
            f"Spherocity Index       : "
            f"{properties_3d['spherocity_index']:.4f}"
        )

        print(
            f"PMI 1                  : "
            f"{properties_3d['pmi1']:.4f}"
        )

        print(
            f"PMI 2                  : "
            f"{properties_3d['pmi2']:.4f}"
        )

        print(
            f"PMI 3                  : "
            f"{properties_3d['pmi3']:.4f}"
        )

        if properties_3d["conformer_energy"] is not None:

            print(
                f"Conformer Energy       : "
                f"{properties_3d['conformer_energy']:.4f}"
            )

        else:

            print(
                "Conformer Energy       : Not available"
            )

    except Exception as error:

        print(
            "\n3D calculation failed:"
        )

        print(
            f"{error}"
        )

    # ========================================================
    # COMPLETE
    # ========================================================

    print("\n" + "=" * 70)
    print("       RDKit SCIENTIFIC PROPERTIES TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
