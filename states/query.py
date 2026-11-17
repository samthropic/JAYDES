#!/usr/bin/env python3

import os

import data.cache as cache
import data.db_connect as dbc
from data.db_connect import is_db_up
from common.validation import is_finite_number, is_integer
import regions.query as rqry
from states.load import load_state_coordinates


STATE_CODE_LEN = 2
ID = 'id'
STATES_COLLECTION = 'states'
STATES_CACHE = 'states'
NEIGHBORHOODS_COLLECTION = 'neighborhoods'
STATES_CSV = os.path.join(os.path.dirname(__file__), 'raw_data', 'states.csv')
UPDATABLE_FIELDS = ('name', 'capital', 'population', 'area_sq_miles',
                    'region_id', 'latitude', 'longitude')

TEST_STATE = {
    "state_code": "TS",
    "population": 1000000,
    "capital": "Test Capital",
    "area_sq_miles": 50000,
    "name": 'Test State',
    "region_id": "NE",
    "latitude": 40.0,
    "longitude": -74.0,
}

STATE_TEST_DATA = {
    "AL": {
        "population": 4903185,
        "capital": "Montgomery",
        "area_sq_miles": 52420,
        "name": 'Alabama',
        "region_id": "SE",
    },
    "AK": {
        "population": 731545,
        "capital": "Juneau",
        "area_sq_miles": 665384,
        "name": 'Alaska',
        "region_id": "MW",
    },
    "AZ": {
        "population": 7278717,
        "capital": "Phoenix",
        "area_sq_miles": 113990,
        "name": 'Arizona',
        "region_id": "MW",
    },
    # Add more states as needed
}


def _apply_csv_coordinates(states):
    """Attach latitude/longitude from states.csv onto matching seed rows."""
    coords = load_state_coordinates(STATES_CSV)
    for code, data in states.items():
        if code in coords:
            data['latitude'] = coords[code]['latitude']
            data['longitude'] = coords[code]['longitude']
    return states


_apply_csv_coordinates(STATE_TEST_DATA)


class StateHasNeighborhoodsError(Exception):
    """Raised when deleting a state that neighborhoods still reference."""


def _state_docs():
    """Copy STATE_TEST_DATA into documents whose id is the state code."""
    return [{ID: code, **data} for code, data in STATE_TEST_DATA.items()]


def _ensure_seeded():
    """Insert STATE_TEST_DATA when the states collection is empty."""
    dbc.connect_db()
    if dbc.read(STATES_COLLECTION):
        return
    for doc in _state_docs():
        dbc.create(STATES_COLLECTION, doc)


def read():
    """
    Return a list of states from seDB. The state code is each state's id.
    A repeated call returns the in-memory copy until a write clears it.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    cached = cache.get(STATES_CACHE)
    if cached is not None:
        return cached
    _ensure_seeded()
    cache.put(STATES_CACHE, dbc.read(STATES_COLLECTION))
    return cache.get(STATES_CACHE)


def read_one(state_code: str):
    """
    Return the state with this code, or None if there is no such state or
    the database is down.
    """
    states = read()
    if states is None:
        return None
    for state in states:
        if state[ID] == state_code:
            return state
    return None


def exists(state_code: str):
    """
    Check if a state exists in seDB.
    """
    states = read()
    if states is None:
        return None
    return any(state[ID] == state_code for state in states)


def _check_region_id(region_id):
    """Require a two-letter code referencing an existing region."""
    if (not isinstance(region_id, str)
            or len(region_id) != rqry.REGION_CODE_LEN
            or not region_id.isascii() or not region_id.isalpha()):
        raise ValueError(
            f'Region ID must be a {rqry.REGION_CODE_LEN}-letter string.'
        )
    if not rqry.exists(region_id):
        raise ValueError(f"Region ID '{region_id}' does not exist.")


def _check_coordinates(latitude, longitude):
    """Require latitude/longitude in the valid geographic ranges."""
    if not is_finite_number(latitude) or not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90.")
    if not is_finite_number(longitude) or not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180.")


def check_valid_state(
    state_code: str,
    population: int,
    capital: str,
    area_sq_miles: float,
    name: str,
    region_id: str = None,
    latitude=None,
    longitude=None,
):
    if exists(state_code):
        raise ValueError(f"State code {state_code} already exists.")
    if not isinstance(state_code, str) or len(state_code) != STATE_CODE_LEN:
        raise ValueError(f"State code must be {STATE_CODE_LEN}-letter string.")
    if not is_integer(population) or population < 0:
        raise ValueError("Population must be a non-negative integer.")
    _check_region_id(region_id)
    if latitude is not None or longitude is not None:
        if latitude is None or longitude is None:
            raise ValueError(
                "Latitude and longitude must both be provided together."
            )
        _check_coordinates(latitude, longitude)
    return True


def create(
    state_code: str,
    population: int,
    capital: str,
    area_sq_miles: float,
    name: str,
    region_id: str = None,
    latitude=None,
    longitude=None,
):
    """
    Create a new state in seDB. An existing region_id is required.
    Latitude and longitude are optional and come from states.csv for seeds.
    """
    # check_valid_state raises ValueError if the state is invalid, so we don't
    # need to check the return value.
    check_valid_state(
        state_code,
        population,
        capital,
        area_sq_miles,
        name,
        region_id,
        latitude,
        longitude,
    )
    if not is_db_up():
        print("Database is down.")
        return None
    doc = {
        "population": population,
        "capital": capital,
        "area_sq_miles": area_sq_miles,
        "name": name,
        "region_id": region_id,
    }
    if latitude is not None and longitude is not None:
        doc['latitude'] = latitude
        doc['longitude'] = longitude
    dbc.create(STATES_COLLECTION, {ID: state_code, **doc})
    cache.invalidate(STATES_CACHE)
    return doc


def update(state_code: str, changes: dict):
    """
    Change fields of an existing state in seDB and return the updated state.
    Return None if there is no such state or the database is down. Raise
    ValueError if the changes are not valid.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    unknown = set(changes) - set(UPDATABLE_FIELDS)
    if unknown:
        raise ValueError(f"Cannot update fields: {sorted(unknown)}.")
    if 'population' in changes:
        population = changes['population']
        if not is_integer(population) or population < 0:
            raise ValueError("Population must be a non-negative integer.")
    if 'region_id' in changes:
        _check_region_id(changes['region_id'])
    if 'latitude' in changes or 'longitude' in changes:
        current = read_one(state_code)
        if current is None:
            return None
        latitude = changes.get('latitude', current.get('latitude'))
        longitude = changes.get('longitude', current.get('longitude'))
        if latitude is None or longitude is None:
            raise ValueError(
                "Latitude and longitude must both be set on a state."
            )
        _check_coordinates(latitude, longitude)
    if not exists(state_code):
        return None
    if changes:
        dbc.update(STATES_COLLECTION, {ID: state_code}, changes)
        cache.invalidate(STATES_CACHE)
    return read_one(state_code)


def delete(state_code: str):
    """
    Delete a state from seDB. Return True if it was deleted, False if there
    is no such state, and None if the database is down.
    Raise StateHasNeighborhoodsError if any neighborhood references the state.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    _ensure_seeded()
    if dbc.read_one(NEIGHBORHOODS_COLLECTION,
                    {'state_id': state_code}) is not None:
        raise StateHasNeighborhoodsError(
            f'State {state_code} still has neighborhoods. '
            'Reassign or delete those neighborhoods before deleting the '
            'state.'
        )
    deleted = dbc.delete(STATES_COLLECTION, {ID: state_code}) > 0
    if deleted:
        cache.invalidate(STATES_CACHE)
    return deleted


def main():
    states = read()
    for data in states:
        print(f"State: {data[ID]}")
        print(f"Population: {data['population']}")
        print(f"Capital: {data['capital']}")
        print(f"Area (sq miles): {data['area_sq_miles']}")
        print(f"Region ID: {data.get('region_id')}")
        print(f"Latitude: {data.get('latitude')}")
        print(f"Longitude: {data.get('longitude')}")
        print("-" * 40)


if __name__ == "__main__":
    main()
