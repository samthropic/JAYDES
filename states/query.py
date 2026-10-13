#!/usr/bin/env python3

from data.db_connect import is_db_up
import regions.query as rqry


STATE_CODE_LEN = 2
ID = 'id'

TEST_STATE = {
    "state_code": "TS",
    "population": 1000000,
    "capital": "Test Capital",
    "area_sq_miles": 50000,
    "name": 'Test State',
    "region_id": None,
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


def read():
    """
    Return a list of all states in the test data. The state code is used
    as each state's id.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    return [{ID: code, **data} for code, data in STATE_TEST_DATA.items()]


def exists(state_code: str):
    """
    Check if a state exists in the test data.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    return state_code in STATE_TEST_DATA


def check_valid_state(state_code: str, population: int, capital: str,
                      area_sq_miles: float, name: str,
                      region_id: str = None):
    if exists(state_code):
        raise ValueError(f"State code {state_code} already exists.")
    if not isinstance(state_code, str) or len(state_code) != STATE_CODE_LEN:
        raise ValueError(f"State code must be {STATE_CODE_LEN}-letter string.")
    if not isinstance(population, int) or population < 0:
        raise ValueError("Population must be a non-negative integer.")
    if region_id is not None:
        if not isinstance(region_id, str) or len(region_id) != rqry.REGION_CODE_LEN:
            raise ValueError(
                f"Region ID must be a {rqry.REGION_CODE_LEN}-letter string."
            )
        if not rqry.exists(region_id):
            raise ValueError(f"Region ID '{region_id}' does not exist.")
    return True


def create(state_code: str, population: int, capital: str,
           area_sq_miles: float, name: str, region_id: str = None):
    """
    Create a new state entry in the test data.
    """
    # check_valid_state raises ValueError if the state is invalid, so we don't
    # need to check the return value.
    check_valid_state(state_code, population, capital, area_sq_miles, name,
                      region_id)
    if not is_db_up():
        print("Database is down.")
        return None
    STATE_TEST_DATA[state_code] = {
        "population": population,
        "capital": capital,
        "area_sq_miles": area_sq_miles,
        "name": name,
        "region_id": region_id,
    }
    return STATE_TEST_DATA[state_code]


def main():
    states = read()
    for data in states:
        print(f"State: {data[ID]}")
        print(f"Population: {data['population']}")
        print(f"Capital: {data['capital']}")
        print(f"Area (sq miles): {data['area_sq_miles']}")
        print(f"Region ID: {data.get('region_id')}")
        print("-" * 40)


if __name__ == "__main__":
    main()
