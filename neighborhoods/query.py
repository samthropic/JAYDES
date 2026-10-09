#!/usr/bin/env python3

from data.db_connect import is_db_up
import states.query as state_qry

UUID_STRING_LEN = 36
ID = 'id'

TEST_NEIGHBORHOOD = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": 'Test Neighborhood',
    "state_id": "AL"        # TN
}

NEIGHBORHOOD_TEST_DATA = {
    "73a1b2c3-d4e5-6f7a-8b9c-0123456789ab": {
        "name": 'Greenwich Village',
        "state_id": "AL"    # NY
    },
    "84b2c3d4-e5f6-7a8b-9c0d-123456789abc": {
        "name": 'Westlake',
        "state_id": "AK"    # CA
    },
    "d290f1ee-6c54-4b01-90e6-d701748f0851": {
        "name": 'Old City',
        "state_id": "AK"    # CA
    },
    "5f8a3c2b-1e9d-4a7b-8c6d-2f3e4a5b6c7d": {
        "name": "SoHo",
        "state_id": "AZ"    # NY
    },
    "9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d": {
        "name": "Lincoln Park",
        "state_id": "AL"    # IL
    }
}


def read():
    """
    Return a list of all neighborhoods in the test data.
    """
    if not is_db_up():
        print("Database is down.")
        return None

    return [
        {ID: code, **data}
        for code, data in NEIGHBORHOOD_TEST_DATA.items()
    ]


def exists(neighborhood_id: str):
    """
    Check if a neighborhood exists in the test data.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    return neighborhood_id in NEIGHBORHOOD_TEST_DATA


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
    Create a new neighborhood entry in the test data.
    """
    check_valid_neighborhood(neighborhood_id, name, state_id)

    if not is_db_up():
        print("Database is down.")
        return None

    NEIGHBORHOOD_TEST_DATA[neighborhood_id] = {
        "name": name,
        "state_id": state_id,
    }

    return {ID: neighborhood_id, **NEIGHBORHOOD_TEST_DATA[neighborhood_id]}


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
