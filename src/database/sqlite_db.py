import sqlite3
from pathlib import Path

from models.compound import Compound


# Project root:
# smiles-generator/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Database location:
DATABASE_PATH = PROJECT_ROOT / "data" / "chemicals.db"


def get_connection():
    """
    Create and return a connection to the SQLite database.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
    """
    Create the compounds table if it does not already exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS compounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cid INTEGER UNIQUE,
            name TEXT NOT NULL,
            smiles TEXT NOT NULL,
            inchi TEXT,
            inchikey TEXT UNIQUE
        )
        """
    )

    connection.commit()
    connection.close()


def save_compound(compound):
    """
    Save a Compound object to the database.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO compounds
        (cid, name, smiles, inchi, inchikey)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            compound.cid,
            compound.name,
            compound.smiles,
            compound.inchi,
            compound.inchikey
        )
    )

    connection.commit()
    connection.close()


def get_compound_by_name(name):
    """
    Search for a compound by name.

    Returns:
        Compound object if found.
        None if not found.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT cid, name, smiles, inchi, inchikey
        FROM compounds
        WHERE LOWER(name) = LOWER(?)
        LIMIT 1
        """,
        (name,)
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
        inchikey=row[4]
    )