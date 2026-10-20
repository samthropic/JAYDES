#!/usr/bin/env python3

import data.db_connect as dbc
from data.db_connect import is_db_up


REGION_CODE_LEN = 2
ID = 'id'
REGIONS_COLLECTION = 'regions'
UPDATABLE_FIELDS = ('name', 'population', 'description')

TEST_REGION = {
    "region_code": "TR",
    "name": "Test Region",
    "population": 500000,
    "description": "A test region for validation",
}

REGION_TEST_DATA = {
    "NE": {
        "name": "Northeast",
        "population": 55000000,
        "description": "Northeastern United States",
    },
    "SE": {
        "name": "Southeast",
        "population": 40000000,
        "description": "Southeastern United States",
    },
    "MW": {
        "name": "Midwest",
        "population": 68000000,
        "description": "Midwestern United States",
    },
}


def _ensure_seeded():
    """Insert REGION_TEST_DATA when the regions collection is empty."""
    dbc.connect_db()
    if dbc.read(REGIONS_COLLECTION):
        return
    for code, data in REGION_TEST_DATA.items():
        dbc.create(REGIONS_COLLECTION, {ID: code, **data})


def read():
    """
    Return regions from seDB, keyed by id, without the id inside each record.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    _ensure_seeded()
    regions = {}
    for doc in dbc.read(REGIONS_COLLECTION):
        code = doc.pop(ID)
        regions[code] = doc
    return regions

def read_one(region_code: str):
    """
    Return a single region by code, or None if absent or DB is down.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    _ensure_seeded()
    region = dbc.read_one(REGIONS_COLLECTION, {ID: region_code})
    if region is not None:
        region.pop(dbc.MONGO_ID, None)
    return region


def exists(region_code: str):
    """
    Check if a region exists in seDB.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    _ensure_seeded()
    return dbc.read_one(REGIONS_COLLECTION, {ID: region_code}) is not None


def check_valid_region(region_code: str, name: str, population: int,
                       description: str):
    if exists(region_code):
        raise ValueError(f"Region code {region_code} already exists.")
    if not isinstance(region_code, str) or len(region_code) != REGION_CODE_LEN:
        raise ValueError(
            f"Region code must be {REGION_CODE_LEN}-letter string."
        )
    if not isinstance(name, str) or len(name) == 0:
        raise ValueError("Region name must be a non-empty string.")
    if not isinstance(population, int) or population < 0:
        raise ValueError("Population must be a non-negative integer.")
    return True


def create(region_code: str, name: str, population: int,
           description: str):
    """
    Create a new region in seDB.
    """
    check_valid_region(region_code, name, population, description)
    if not is_db_up():
        print("Database is down.")
        return None
    doc = {
        "name": name,
        "population": population,
        "description": description,
    }
    dbc.create(REGIONS_COLLECTION, {ID: region_code, **doc})
    return doc


def update(region_code: str, changes: dict):
    """
    Update fields on an existing region and return the updated region.
    """
    if not is_db_up():
        print("Database is down.")
        return None

    unknown = set(changes) - set(UPDATABLE_FIELDS)
    if unknown:
        raise ValueError(f"Cannot update fields: {sorted(unknown)}.")

    if not exists(region_code):
        return None

    if 'population' in changes:
        if not isinstance(changes['population'], int) or changes['population'] < 0:
            raise ValueError("Population must be a non-negative integer.")

    if 'name' in changes and (not isinstance(changes['name'], str) or len(changes['name']) == 0):
        raise ValueError("Region name must be a non-empty string.")

    dbc.update(REGIONS_COLLECTION, {ID: region_code}, changes)
    return read_one(region_code)

def delete(region_code: str):
    """
    Delete a region from seDB. Return True if it was deleted, False if there
    is no such region, and None if the database is down.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    _ensure_seeded()
    return dbc.delete(REGIONS_COLLECTION, {ID: region_code}) > 0


def main():
    regions = read()
    for region, data in regions.items():
        print(f"Region: {region}")
        print(f"Name: {data['name']}")
        print(f"Population: {data['population']}")
        print(f"Description: {data['description']}")
        print("-" * 40)


if __name__ == "__main__":
    main()
