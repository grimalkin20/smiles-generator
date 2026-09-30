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