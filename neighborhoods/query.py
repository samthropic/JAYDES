#!/usr/bin/env python3

import data.cache as cache
import data.db_connect as dbc

import states.query as state_qry

UUID_STRING_LEN = 36
ID = 'id'
NEIGHBORHOODS_COLLECTION = 'neighborhoods'
NEIGHBORHOODS_CACHE = 'neighborhoods'
UPDATABLE_FIELDS = ('name', 'state_id')

TEST_NEIGHBORHOOD = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": 'Test Neighborhood',
    "state_id": "TN"
}

NEIGHBORHOOD_TEST_DATA = {
    "73a1b2c3-d4e5-6f7a-8b9c-0123456789ab": {
        "name": 'Greenwich Village',
        "state_id": "TN"    # TN
    },
    "84b2c3d4-e5f6-7a8b-9c0d-123456789abc": {
        "name": 'Westlake',
        "state_id": "TN"    # TN
    },
    "d290f1ee-6c54-4b01-90e6-d701748f0851": {
        "name": 'Old City',
        "state_id": "CA"
    },
    "5f8a3c2b-1e9d-4a7b-8c6d-2f3e4a5b6c7d": {
        "name": "SoHo",
        "state_id": "NY"
    },
    "9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d": {
        "name": "Lincoln Park",
        "state_id": "IL"
    }
}


def _neighborhood_docs():
    """Copy NEIGHBORHOOD_TEST_DATA into documents whose id is the UUID."""
    return [
        {ID: code, **data}
        for code, data in NEIGHBORHOOD_TEST_DATA.items()
    ]


def _ensure_seeded():
    """Insert NEIGHBORHOOD_TEST_DATA when the collection is empty."""
    dbc.connect_db()
    if dbc.read(NEIGHBORHOODS_COLLECTION):
        return
    for doc in _neighborhood_docs():
        dbc.create(NEIGHBORHOODS_COLLECTION, doc)


def read(neighborhood_id: str = None):
    """
    Return all neighborhoods or one by id from seDB.
    List reads use an in-memory copy until a write clears it.
    """
    if not dbc.is_db_up():
        print("Database is down.")
        return None

    cached = cache.get(NEIGHBORHOODS_CACHE)
    if cached is None:
        _ensure_seeded()
        cache.put(NEIGHBORHOODS_CACHE, dbc.read(NEIGHBORHOODS_COLLECTION))
        cached = cache.get(NEIGHBORHOODS_CACHE)

    if neighborhood_id is None:
        return cached
    return next(
        (record for record in cached if record[ID] == neighborhood_id),
        None,
    )


def exists(neighborhood_id: str):
    """
    Check if a neighborhood exists in the database.
    """
    neighborhoods = read()
    if neighborhoods is None:
        return None
    return any(record[ID] == neighborhood_id for record in neighborhoods)


def check_valid_neighborhood(neighborhood_id: str, name: str, state_id: str):
    """
    Validate neighborhood fields and ensure the foreign key (state_id) exists.
    """
    if exists(neighborhood_id):
        raise ValueError(f"Neighborhood ID {neighborhood_id} already exists.")
    if (not isinstance(neighborhood_id, str) or
            len(neighborhood_id) != UUID_STRING_LEN):
        raise ValueError("Neighborhood ID must be a valid UUID string.")
    if not isinstance(name, str) or len(name.strip()) == 0:
        raise ValueError("Neighborhood name must be a non-empty string.")
    if (not isinstance(state_id, str) or
            len(state_id) != state_qry.STATE_CODE_LEN):
        raise ValueError(
            f"State ID must be a {state_qry.STATE_CODE_LEN}-letter string."
        )
    if not state_qry.exists(state_id):
        raise ValueError(
            f"State ID '{state_id}' does not exist in the database."
        )

    return True


def create(neighborhood_id: str, name: str, state_id: str):
    """
    Create a new neighborhood entry in the database.
    """
    check_valid_neighborhood(neighborhood_id, name, state_id)

    if not dbc.is_db_up():
        print("Database is down.")
        return None

    doc = {
        "name": name,
        "state_id": state_id,
    }
    dbc.create(NEIGHBORHOODS_COLLECTION, {ID: neighborhood_id, **doc})
    cache.invalidate(NEIGHBORHOODS_CACHE)
    return {ID: neighborhood_id, **doc}


def update(neighborhood_id: str, changes: dict):
    """
    Update an existing neighborhood entry with partial changes.
    """
    if not dbc.is_db_up():
        print("Database is down.")
        return None

    if not exists(neighborhood_id):
        return None

    unknown = set(changes) - set(UPDATABLE_FIELDS)
    if unknown:
        raise ValueError(f"Cannot update fields: {sorted(unknown)}.")

    if 'name' in changes:
        name = changes['name']
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Neighborhood name must be a non-empty string.")

    if 'state_id' in changes:
        state_id = changes['state_id']
        if (not isinstance(state_id, str) or
                len(state_id) != state_qry.STATE_CODE_LEN):
            raise ValueError(
                f"State ID must be a {state_qry.STATE_CODE_LEN}-letter string."
            )
        if not state_qry.exists(state_id):
            raise ValueError(
                f"State ID '{state_id}' does not exist in the database."
            )

    if changes:
        dbc.update(NEIGHBORHOODS_COLLECTION, {ID: neighborhood_id}, changes)
        cache.invalidate(NEIGHBORHOODS_CACHE)

    return read(neighborhood_id)


def delete(neighborhood_id: str):
    """
    Delete a neighborhood entry.
    """
    if not dbc.is_db_up():
        print("Database is down.")
        return None

    _ensure_seeded()
    deleted = dbc.delete(NEIGHBORHOODS_COLLECTION, {ID: neighborhood_id}) > 0
    if deleted:
        cache.invalidate(NEIGHBORHOODS_CACHE)
    return deleted


def main():
    neighborhoods = read()
    if neighborhoods:
        for data in neighborhoods:
            print(f"Neighborhood ID: {data[ID]}")
            print(f"Name: {data['name']}")
            print(f"State ID: {data['state_id']}")
            print("-" * 40)


if __name__ == "__main__":
    main()
