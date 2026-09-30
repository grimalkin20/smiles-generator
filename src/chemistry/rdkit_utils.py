from rdkit import Chem
from rdkit.Chem import (
    Descriptors,
    Crippen,
    Lipinski,
    rdMolDescriptors
)


def smiles_to_molecule(smiles):
    """
    Convert a SMILES string into an RDKit molecule.

    Returns:
        RDKit molecule object if valid.
        None if invalid.
    """

    if not smiles:
        return None

    molecule = Chem.MolFromSmiles(smiles)

    return molecule


def validate_smiles(smiles):
    """
    Check whether a SMILES string represents
    a valid molecule.

    Returns:
        True if valid.
        False if invalid.
    """

    molecule = smiles_to_molecule(smiles)

    return molecule is not None


def canonicalize_smiles(smiles):
    """
    Convert a valid SMILES into RDKit's
    canonical SMILES representation.

    Returns:
        Canonical SMILES string if valid.
        None if invalid.
    """

    molecule = smiles_to_molecule(smiles)

    if molecule is None:
        return None

    return Chem.MolToSmiles(molecule)


def calculate_properties(smiles):
    """
    Calculate common molecular properties using RDKit.

    Returns:
        Dictionary containing molecular properties.

    Raises:
        ValueError if the SMILES is invalid.
    """

    molecule = smiles_to_molecule(smiles)

    if molecule is None:
        raise ValueError(
            "Cannot calculate properties for invalid SMILES."
        )

    properties = {
        "molecular_formula": (
            rdMolDescriptors.CalcMolFormula(molecule)
        ),

        "molecular_weight": (
            Descriptors.MolWt(molecule)
        ),

        "logp": (
            Crippen.MolLogP(molecule)
        ),

        "tpsa": (
            rdMolDescriptors.CalcTPSA(molecule)
        ),

        "h_bond_donors": (
            Lipinski.NumHDonors(molecule)
        ),

        "h_bond_acceptors": (
            Lipinski.NumHAcceptors(molecule)
        ),

        "rotatable_bonds": (
            Lipinski.NumRotatableBonds(molecule)
        ),

        "ring_count": (
            Lipinski.RingCount(molecule)
        ),

        "heavy_atoms": (
            Lipinski.HeavyAtomCount(molecule)
        )
    }

    return properties
