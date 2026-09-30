from resolver.pubchem import (
    get_compound_from_pubchem,
    extract_compound_info,
    get_complete_pubchem_data
)

from chemistry.rdkit_utils import (
    calculate_scientific_properties,
    calculate_3d_properties,
    generate_isomeric_smiles,
    generate_inchi,
    generate_inchikey
)


def main():

    compound_name = "aspirin"

    print("=" * 70)
    print("             SCIENTIFIC COMPOUND PIPELINE")
    print("=" * 70)

    # ========================================================
    # PUBCHEM
    # ========================================================

    print("\n[1] PubChem lookup")

    data = get_compound_from_pubchem(
        compound_name
    )

    compound = extract_compound_info(
        data
    )

    print("-" * 50)

    print(
        f"CompoundName: {compound.name}"
    )

    print(
        f"CID: {compound.cid}"
    )

    # ========================================================
    # PUBCHEM SCIENTIFIC DATA
    # ========================================================

    print("\n[2] PubChem scientific data")

    pubchem_data = get_complete_pubchem_data(
        compound.cid
    )

    print("-" * 50)

    print(
        f"IUPAC name : "
        f"{pubchem_data['iupac_name']}"
    )

    print(
        f"Synonyms   : "
        f"{len(pubchem_data['synonyms'])}"
    )

    print(
        f"CAS numbers: "
        f"{pubchem_data['cas_numbers']}"
    )

    # ========================================================
    # RDKit IDENTIFIERS
    # ========================================================

    print("\n[3] RDKit identifiers")

    smiles = compound.smiles

    print("-" * 50)

    print(
        f"Canonical SMILES : "
        f"{compound.canonical_smiles}"
    )

    print(
        f"RDKit Isomeric SMILES : "
        f"{generate_isomeric_smiles(smiles)}"
    )

    print(
        f"RDKit InChI : "
        f"{generate_inchi(smiles)}"
    )

    print(
        f"RDKit InChIKey : "
        f"{generate_inchikey(smiles)}"
    )

    # ========================================================
    # RDKit 2D SCIENTIFIC DATA
    # ========================================================

    print("\n[4] RDKit scientific descriptors")

    properties = calculate_scientific_properties(
        smiles
    )

    print("-" * 50)

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
        f"Heavy Atoms        : "
        f"{properties['heavy_atoms']}"
    )

    print(
        f"Total Atoms        : "
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
        f"Stereocenters      : "
        f"{properties['stereocenter_count']}"
    )

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
        f"HBD                : "
        f"{properties['h_bond_donors']}"
    )

    print(
        f"HBA                : "
        f"{properties['h_bond_acceptors']}"
    )

    print(
        f"Rotatable Bonds    : "
        f"{properties['rotatable_bonds']}"
    )

    print(
        f"Total Rings        : "
        f"{properties['ring_count']}"
    )

    print(
        f"Aromatic Rings     : "
        f"{properties['aromatic_ring_count']}"
    )

    print(
        f"Aliphatic Rings     : "
        f"{properties['aliphatic_ring_count']}"
    )

    # ========================================================
    # DRUG LIKENESS
    # ========================================================

    print("\n[5] Drug-likeness")

    print("-" * 50)

    print(
        f"Lipinski Ro5       : "
        f"{properties['lipinski_pass']}"
    )

    print(
        f"Veber              : "
        f"{properties['veber_pass']}"
    )

    print(
        f"QED Score          : "
        f"{properties['qed_score']:.4f}"
    )

    print(
        f"PAINS Alert        : "
        f"{properties['pains_alert']}"
    )

    if properties["pains_alerts"]:

        print("PAINS matches:")

        for alert in properties["pains_alerts"]:

            print(
                f"  - {alert}"
            )

    # ========================================================
    # 3D
    # ========================================================

    print("\n[6] RDKit 3D descriptors")

    try:

        properties_3d = calculate_3d_properties(
            smiles
        )

        print("-" * 50)

        print(
            f"Radius of Gyration : "
            f"{properties_3d['radius_of_gyration']:.4f}"
        )

        print(
            f"Asphericity        : "
            f"{properties_3d['asphericity']:.4f}"
        )

        print(
            f"Spherocity         : "
            f"{properties_3d['spherocity_index']:.4f}"
        )

        print(
            f"PMI1               : "
            f"{properties_3d['pmi1']:.4f}"
        )

        print(
            f"PMI2               : "
            f"{properties_3d['pmi2']:.4f}"
        )

        print(
            f"PMI3               : "
            f"{properties_3d['pmi3']:.4f}"
        )

        print(
            f"Conformer Energy   : "
            f"{properties_3d['conformer_energy']}"
        )

    except Exception as error:

        print(
            f"3D calculation failed: {error}"
        )

    # ========================================================
    # END
    # ========================================================

    print("\n" + "=" * 70)
    print("SCIENTIFIC PIPELINE TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
