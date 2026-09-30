from rdkit import Chem
from rdkit.Chem import (
    Descriptors,
    Crippen,
    Lipinski,
    QED,
    rdMolDescriptors,
    FilterCatalog,
    Descriptors3D,
    AllChem
)


# ============================================================
# BASIC SMILES FUNCTIONS
# ============================================================

def smiles_to_molecule(smiles):
    """
    Convert a SMILES string into an RDKit molecule.

    Returns:
        RDKit Mol object if valid.
        None if invalid.
    """

    if not smiles:
        return None

    return Chem.MolFromSmiles(smiles)


def validate_smiles(smiles):
    """
    Check whether a SMILES represents a valid molecule.
    """

    molecule = smiles_to_molecule(smiles)

    return molecule is not None


def canonicalize_smiles(smiles):
    """
    Generate RDKit canonical SMILES.
    """

    molecule = smiles_to_molecule(smiles)

    if molecule is None:
        return None

    return Chem.MolToSmiles(
        molecule,
        canonical=True
    )


def generate_isomeric_smiles(smiles):
    """
    Generate stereochemistry-aware SMILES.
    """

    molecule = smiles_to_molecule(smiles)

    if molecule is None:
        return None

    return Chem.MolToSmiles(
        molecule,
        isomericSmiles=True
    )


def generate_inchi(smiles):
    """
    Generate Standard InChI from SMILES.
    """

    molecule = smiles_to_molecule(smiles)

    if molecule is None:
        return None

    return Chem.MolToInchi(molecule)


def generate_inchikey(smiles):
    """
    Generate InChIKey from SMILES.
    """

    molecule = smiles_to_molecule(smiles)

    if molecule is None:
        return None

    return Chem.MolToInchiKey(molecule)


# ============================================================
# BASIC MOLECULAR PROPERTIES
# ============================================================

def calculate_properties(smiles):
    """
    Calculate 2D molecular descriptors using RDKit.

    Returns:
        Dictionary containing scientific descriptors.
    """

    molecule = smiles_to_molecule(smiles)

    if molecule is None:
        raise ValueError(
            "Cannot calculate properties for invalid SMILES."
        )

    # --------------------------------------------------------
    # Explicit hydrogen molecule
    # --------------------------------------------------------

    molecule_with_h = Chem.AddHs(molecule)

    # --------------------------------------------------------
    # Stereocenters
    # --------------------------------------------------------

    chiral_centers = Chem.FindMolChiralCenters(
        molecule,
        includeUnassigned=True
    )

    # --------------------------------------------------------
    # Rings
    # --------------------------------------------------------

    ring_count = rdMolDescriptors.CalcNumRings(molecule)

    aromatic_ring_count = (
        rdMolDescriptors.CalcNumAromaticRings(molecule)
    )

    aliphatic_ring_count = (
        ring_count - aromatic_ring_count
    )

    # --------------------------------------------------------
    # Properties
    # --------------------------------------------------------

    properties = {

        # Identity / structure
        "molecular_formula":
            rdMolDescriptors.CalcMolFormula(molecule),

        "molecular_weight":
            Descriptors.MolWt(molecule),

        "exact_mass":
            Descriptors.ExactMolWt(molecule),

        "heavy_atoms":
            molecule.GetNumHeavyAtoms(),

        "total_atoms":
            molecule_with_h.GetNumAtoms(),

        "formal_charge":
            Chem.GetFormalCharge(molecule),

        "fraction_csp3":
            rdMolDescriptors.CalcFractionCSP3(molecule),

        "stereocenter_count":
            len(chiral_centers),

        # Physicochemical
        "tpsa":
            Descriptors.TPSA(molecule),

        "logp":
            Crippen.MolLogP(molecule),

        "molar_refractivity":
            Crippen.MolMR(molecule),

        "h_bond_donors":
            Lipinski.NumHDonors(molecule),

        "h_bond_acceptors":
            Lipinski.NumHAcceptors(molecule),

        "rotatable_bonds":
            Lipinski.NumRotatableBonds(molecule),

        # Rings
        "ring_count":
            ring_count,

        "aromatic_ring_count":
            aromatic_ring_count,

        "aliphatic_ring_count":
            aliphatic_ring_count,
    }

    return properties


# ============================================================
# DRUG-LIKENESS
# ============================================================

def calculate_lipinski(properties):
    """
    Apply a simple Lipinski Rule-of-Five check.

    Rules:
        Molecular weight <= 500
        LogP <= 5
        HBD <= 5
        HBA <= 10

    Returns:
        True if all criteria pass.
    """

    return (
        properties["molecular_weight"] <= 500
        and properties["logp"] <= 5
        and properties["h_bond_donors"] <= 5
        and properties["h_bond_acceptors"] <= 10
    )


def calculate_veber(properties):
    """
    Apply Veber criteria.

    Rules:
        Rotatable bonds <= 10
        TPSA <= 140
    """

    return (
        properties["rotatable_bonds"] <= 10
        and properties["tpsa"] <= 140
    )


def calculate_qed(smiles):
    """
    Calculate Quantitative Estimate of Drug-likeness.
    """

    molecule = smiles_to_molecule(smiles)

    if molecule is None:
        raise ValueError(
            "Cannot calculate QED for invalid SMILES."
        )

    return QED.qed(molecule)


# ============================================================
# PAINS FILTER
# ============================================================

def check_pains(smiles):
    """
    Check molecule against the RDKit PAINS filter catalog.

    Returns:
        Dictionary containing:
            alerts
            has_alert
    """

    molecule = smiles_to_molecule(smiles)

    if molecule is None:
        raise ValueError(
            "Cannot run PAINS filter on invalid SMILES."
        )

    params = FilterCatalog.FilterCatalogParams()

    params.AddCatalog(
        FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS
    )

    catalog = FilterCatalog.FilterCatalog(params)

    matches = catalog.GetMatches(molecule)

    alerts = []

    for match in matches:
        alerts.append(match.GetDescription())

    return {
        "has_alert": len(alerts) > 0,
        "alerts": alerts
    }


# ============================================================
# COMPLETE SCIENTIFIC CALCULATION
# ============================================================

def calculate_scientific_properties(smiles):
    """
    Calculate the complete set of currently supported
    scientific descriptors.
    """

    properties = calculate_properties(smiles)

    # Drug-likeness
    properties["lipinski_pass"] = calculate_lipinski(
        properties
    )

    properties["veber_pass"] = calculate_veber(
        properties
    )

    properties["qed_score"] = calculate_qed(
        smiles
    )

    # PAINS
    pains = check_pains(smiles)

    properties["pains_alert"] = pains["has_alert"]
    properties["pains_alerts"] = pains["alerts"]

    return properties


# ============================================================
# 3D STRUCTURE
# ============================================================

def generate_3d_molecule(smiles):
    """
    Generate an optimized 3D conformer.

    Procedure:
        1. Parse SMILES
        2. Add hydrogens
        3. Generate 3D coordinates
        4. Optimize using MMFF
        5. Fall back to UFF if MMFF is unavailable

    Returns:
        RDKit molecule with 3D coordinates.
    """

    molecule = smiles_to_molecule(smiles)

    if molecule is None:
        raise ValueError(
            "Cannot generate 3D structure for invalid SMILES."
        )

    molecule = Chem.AddHs(molecule)

    status = AllChem.EmbedMolecule(
        molecule,
        randomSeed=42
    )

    if status != 0:
        raise RuntimeError(
            "RDKit failed to generate a 3D conformer."
        )

    # Try MMFF first
    if AllChem.MMFFHasAllMoleculeParams(molecule):

        AllChem.MMFFOptimizeMolecule(
            molecule
        )

    else:

        AllChem.UFFOptimizeMolecule(
            molecule
        )

    return molecule


def calculate_3d_properties(smiles):
    """
    Calculate basic 3D molecular descriptors.

    Returns:
        Dictionary containing 3D descriptors.
    """

    molecule = generate_3d_molecule(smiles)

    properties = {

        "has_3d_conformer": True,

        "radius_of_gyration":
            Descriptors3D.RadiusOfGyration(molecule),

        "asphericity":
            Descriptors3D.Asphericity(molecule),

        "spherocity_index":
            Descriptors3D.SpherocityIndex(molecule),

        "pmi1":
            Descriptors3D.PMI1(molecule),

        "pmi2":
            Descriptors3D.PMI2(molecule),

        "pmi3":
            Descriptors3D.PMI3(molecule),
    }

    # Calculate force-field energy
    try:

        if AllChem.MMFFHasAllMoleculeParams(molecule):

            force_field = AllChem.MMFFGetMoleculeForceField(
                molecule,
                AllChem.MMFFGetMoleculeProperties(molecule)
            )

        else:

            force_field = AllChem.UFFGetMoleculeForceField(
                molecule
            )

        properties["conformer_energy"] = (
            force_field.CalcEnergy()
        )

    except Exception:

        properties["conformer_energy"] = None

    return properties
