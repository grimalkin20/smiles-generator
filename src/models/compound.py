from dataclasses import dataclass, field


@dataclass
class Compound:
    """
    Represents a chemical compound in our application.

    The object contains:
    1. Chemical identity
    2. Structural information
    3. Physicochemical descriptors
    4. Drug-likeness descriptors
    5. PubChem metadata
    """

    # -----------------------------
    # Chemical identity
    # -----------------------------

    cid: int
    name: str
    smiles: str
    inchi: str
    inchikey: str

    canonical_smiles: str | None = None
    isomeric_smiles: str | None = None

    iupac_name: str | None = None
    synonyms: list[str] = field(default_factory=list)
    cas_numbers: list[str] = field(default_factory=list)

    # -----------------------------
    # Basic molecular properties
    # -----------------------------

    molecular_formula: str | None = None
    molecular_weight: float | None = None
    exact_mass: float | None = None

    heavy_atoms: int | None = None
    total_atoms: int | None = None

    formal_charge: int | None = None
    fraction_csp3: float | None = None
    stereocenter_count: int | None = None

    # -----------------------------
    # Physicochemical descriptors
    # -----------------------------

    tpsa: float | None = None
    logp: float | None = None
    molar_refractivity: float | None = None

    h_bond_donors: int | None = None
    h_bond_acceptors: int | None = None

    rotatable_bonds: int | None = None

    ring_count: int | None = None
    aromatic_ring_count: int | None = None
    aliphatic_ring_count: int | None = None

    # -----------------------------
    # Drug-likeness
    # -----------------------------

    lipinski_pass: bool | None = None
    veber_pass: bool | None = None

    qed_score: float | None = None

    pains_alert: bool | None = None
    pains_alerts: list[str] = field(default_factory=list)

    # -----------------------------
    # PubChem calculated/reference
    # values
    # -----------------------------

    pubchem_xlogp: float | None = None
    pubchem_tpsa: float | None = None

    # -----------------------------
    # 3D properties
    # -----------------------------

    has_3d_conformer: bool = False

    radius_of_gyration: float | None = None
    asphericity: float | None = None
    spherocity_index: float | None = None

    pmi1: float | None = None
    pmi2: float | None = None
    pmi3: float | None = None

    conformer_energy: float | None = None
