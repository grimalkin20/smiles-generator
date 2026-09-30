import sqlite3
from pathlib import Path

from models.compound import Compound


# --------------------------------------------------
# PROJECT PATH
# --------------------------------------------------

# Project root:
# smiles-generator/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Database location:
DATABASE_PATH = PROJECT_ROOT / "data" / "chemicals.db"


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():
    """
    Create and return a connection to the SQLite database.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return sqlite3.connect(DATABASE_PATH)


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

def initialize_database():
    """
    Create the required database tables if they
    do not already exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    # Main chemical identity table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS compounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cid INTEGER UNIQUE,
            name TEXT NOT NULL,
            smiles TEXT NOT NULL,
            canonical_smiles TEXT,
            inchi TEXT,
            inchikey TEXT UNIQUE
        )
        """
    )

    # Names / aliases associated with compounds
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS compound_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            compound_id INTEGER NOT NULL,
            name TEXT NOT NULL COLLATE NOCASE,
            
            UNIQUE(compound_id, name),

            FOREIGN KEY (compound_id)
                REFERENCES compounds(id)
                ON DELETE CASCADE
        )
        """
    )

    connection.commit()
    connection.close()


# --------------------------------------------------
# SAVE COMPOUND
# --------------------------------------------------


def save_compound(compound, search_name=None):
    """
    Save a compound to the database.

    Chemical identity is primarily represented by
    InChIKey.

    The PubChem name and the original search name
    are both stored as aliases.
    """

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------
    # Check whether this chemical already exists
    # --------------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM compounds
        WHERE inchikey = ?
        LIMIT 1
        """,
        (compound.inchikey,)
    )

    existing = cursor.fetchone()

    if existing:
        compound_id = existing[0]

    else:
        # --------------------------------------------------
        # Insert new compound
        # --------------------------------------------------

        cursor.execute(
            """
            INSERT INTO compounds
            (
                cid,
                name,
                smiles,
                canonical_smiles,
                inchi,
                inchikey
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                compound.cid,
                compound.name,
                compound.smiles,
                compound.canonical_smiles,
                compound.inchi,
                compound.inchikey
            )
        )

        compound_id = cursor.lastrowid

    # --------------------------------------------------
    # Save PubChem's name
    # --------------------------------------------------

    cursor.execute(
        """
        INSERT OR IGNORE INTO compound_names
        (
            compound_id,
            name
        )
        VALUES (?, ?)
        """,
        (
            compound_id,
            compound.name
        )
    )

    # --------------------------------------------------
    # Save the user's original search name
    # --------------------------------------------------

    if search_name:

        cursor.execute(
            """
            INSERT OR IGNORE INTO compound_names
            (
                compound_id,
                name
            )
            VALUES (?, ?)
            """,
            (
                compound_id,
                search_name.strip()
            )
        )

    connection.commit()
    connection.close()


# --------------------------------------------------
# SEARCH BY NAME / ALIAS
# --------------------------------------------------

def get_compound_by_name(name):
    """
    Search for a compound using its name or alias.

    Returns:
        Compound object if found.
        None if not found.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            c.cid,
            c.name,
            c.smiles,
            c.inchi,
            c.inchikey,
            c.canonical_smiles
        FROM compounds c
        INNER JOIN compound_names cn
            ON c.id = cn.compound_id
        WHERE LOWER(cn.name) = LOWER(?)
        LIMIT 1
        """,
        (name.strip(),)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return Compound(
        cid=row[0],
        name=row[1],
        smiles=row[2],
        inchi=row[3],
        inchikey=row[4],
        canonical_smiles=row[5]
    )


# --------------------------------------------------
# LIST SAVED COMPOUNDS BY NAME / ALIAS
# --------------------------------------------------

def get_all_compounds():
    """
    Retrieve all compounds stored in the database.

    Returns:
        List of Compound objects.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            cid,
            name,
            smiles,
            inchi,
            inchikey,
            canonical_smiles
        FROM compounds
        ORDER BY name COLLATE NOCASE
        """
    )

    rows = cursor.fetchall()

    connection.close()

    compounds = []

    for row in rows:

        compound = Compound(
            cid=row[0],
            name=row[1],
            smiles=row[2],
            inchi=row[3],
            inchikey=row[4],
            canonical_smiles=row[5]
        )

        compounds.append(compound)

    return compounds
