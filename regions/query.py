#!/usr/bin/env python3

import data.cache as cache
import data.db_connect as dbc
from data.db_connect import is_db_up


REGION_CODE_LEN = 2
ID = 'id'
REGIONS_COLLECTION = 'regions'
REGIONS_CACHE = 'regions'
UPDATABLE_FIELDS = ('name', 'population', 'description')


class RegionHasStatesError(ValueError):
    """A region cannot be deleted while states reference it."""


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
    Return all regions as list records including the region code in `id`.
    A repeated call returns the in-memory copy until a write clears it.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    cached = cache.get(REGIONS_CACHE)
    if cached is not None:
        return cached
    _ensure_seeded()
    cache.put(REGIONS_CACHE, dbc.read(REGIONS_COLLECTION))
    return cache.get(REGIONS_CACHE)


def read_one(region_code: str):
    """
    Return a single region by code, or None if absent or DB is down.
    """
    regions = read()
    if regions is None:
        return None
    for region in regions:
        if region[ID] == region_code:
            return region
    return None


def exists(region_code: str):
    """Check if a region exists in seDB."""
    regions = read()
    if regions is None:
        return None
    return any(region[ID] == region_code for region in regions)


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
    if description is not None and not isinstance(description, str):
        raise ValueError("Region description must be a string.")
    return True


def create(region_code: str, name: str, population: int,
           description: str):
    """Create a new region in seDB."""
    check_valid_region(region_code, name, population, description)
    if not is_db_up():
        print("Database is down.")
        return None
    doc = {
        ID: region_code,
        "name": name,
        "population": population,
        "description": description,
    }
    dbc.create(REGIONS_COLLECTION, doc)
    cache.invalidate(REGIONS_CACHE)
    return {
        ID: region_code,
        "name": name,
        "population": population,
        "description": description,
    }


def update(region_code: str, changes: dict):
    """Update fields on an existing region and return the updated region."""
    if not is_db_up():
        print("Database is down.")
        return None

    unknown = set(changes) - set(UPDATABLE_FIELDS)
    if unknown:
        raise ValueError(f"Cannot update fields: {sorted(unknown)}.")

    if not exists(region_code):
        return None

    if 'population' in changes:
        pop = changes['population']
        if not isinstance(pop, int) or pop < 0:
            raise ValueError("Population must be a non-negative integer.")

    if 'name' in changes and (
        not isinstance(changes['name'], str)
        or len(changes['name']) == 0
    ):
        raise ValueError("Region name must be a non-empty string.")

    if 'description' in changes and changes['description'] is not None:
        if not isinstance(changes['description'], str):
            raise ValueError("Region description must be a string.")

    dbc.update(REGIONS_COLLECTION, {ID: region_code}, changes)
    cache.invalidate(REGIONS_CACHE)
    return read_one(region_code)


def delete(region_code: str):
    """
    Delete a region from seDB. Return True if it was deleted, False if there
    is no such region, and None if the database is down.
    Raise RegionHasStatesError if any state references the region.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    _ensure_seeded()
    if dbc.read_one('states', {'region_id': region_code}) is not None:
        raise RegionHasStatesError(
            f'Region {region_code} still has states. '
            'Reassign or delete those states before deleting the region.'
        )
    deleted = dbc.delete(REGIONS_COLLECTION, {ID: region_code}) > 0
    if deleted:
        cache.invalidate(REGIONS_CACHE)
    return deleted


def main():
    regions = read()
    for region in regions:
        print(f"Region: {region['id']}")
        print(f"Name: {region['name']}")
        print(f"Population: {region['population']}")
        print(f"Description: {region['description']}")
        print("-" * 40)


if __name__ == "__main__":
    main()
