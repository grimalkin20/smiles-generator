from dataclasses import dataclass


@dataclass
class Compound:
    """
    Represents a chemical compound in our application.
    """

    cid: int
    name: str
    smiles: str
    inchi: str
    inchikey: str

    canonical_smiles: str | None = None

    molecular_formula: str | None = None
    molecular_weight: float | None = None
    logp: float | None = None
    tpsa: float | None = None
    h_bond_donors: int | None = None
    h_bond_acceptors: int | None = None
    rotatable_bonds: int | None = None
    ring_count: int | None = None
    heavy_atoms: int | None = None



