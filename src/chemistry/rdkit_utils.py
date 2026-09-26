from rdkit import Chem


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
    Check whether a SMILES string represents a valid molecule.

    Returns:
        True if valid.
        False if invalid.
    """

    molecule = smiles_to_molecule(smiles)

    return molecule is not None


def canonicalize_smiles(smiles):
    """
    Convert a valid SMILES into RDKit's canonical SMILES representation.

    Returns:
        Canonical SMILES string if valid.
        None if invalid.
    """

    molecule = smiles_to_molecule(smiles)

    if molecule is None:
        return None

    return Chem.MolToSmiles(molecule)