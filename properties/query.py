#!/usr/bin/env python3

import math

from data.db_connect import is_db_up
import neighborhoods.query as nqry

ID = "id"
UPDATABLE_FIELDS = (
    "address", "neighborhood_id", "price", "bedrooms", "bathrooms",
    "latitude", "longitude",
)

PROPERTY_TEST_DATA = {
    "prop-001": {
        "address": "125 Perry Street, New York, NY",
        "neighborhood_id": "manhattan-west-village",
        "price": 1850000,
        "bedrooms": 2,
        "bathrooms": 2,
        "latitude": 40.7358,
        "longitude": -74.0068,
    },
    "prop-002": {
        "address": "210 West 89th Street, New York, NY",
        "neighborhood_id": "manhattan-upper-west-side",
        "price": 2450000,
        "bedrooms": 3,
        "bathrooms": 2,
        "latitude": 40.7901,
        "longitude": -73.9745,
    },
    "prop-003": {
        "address": "184 Bedford Avenue, Brooklyn, NY",
        "neighborhood_id": "brooklyn-williamsburg",
        "price": 1350000,
        "bedrooms": 2,
        "bathrooms": 2,
        "latitude": 40.7163,
        "longitude": -73.9582,
    },
    "prop-004": {
        "address": "52 8th Avenue, Brooklyn, NY",
        "neighborhood_id": "brooklyn-park-slope",
        "price": 1950000,
        "bedrooms": 3,
        "bathrooms": 2,
        "latitude": 40.6761,
        "longitude": -73.9734,
    },
    "prop-005": {
        "address": "31-18 Broadway, Queens, NY",
        "neighborhood_id": "queens-astoria",
        "price": 875000,
        "bedrooms": 2,
        "bathrooms": 1,
        "latitude": 40.7601,
        "longitude": -73.9242,
    },
}


TEST_PROPERTY = {
    "property_id": "prop-test",
    "address": "1 Test Street, Test City, NY",
    "neighborhood_id": "test-neighborhood",
    "price": 250000,
    "bedrooms": 3,
    "bathrooms": 2,
    "latitude": 40.7128,
    "longitude": -74.0060,
}


def read(property_id: str = None):
    """
    Return either a list of all properties or a single property by id.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    if property_id is None:
        return [{ID: prop_id, **data}
                for prop_id, data in PROPERTY_TEST_DATA.items()]
    if property_id not in PROPERTY_TEST_DATA:
        return None
    return {ID: property_id, **PROPERTY_TEST_DATA[property_id]}


def exists(property_id: str):
    """
    Check if a property exists in the test data.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    return property_id in PROPERTY_TEST_DATA


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _is_number(value):
    return (isinstance(value, (int, float))
            and not isinstance(value, bool)
            and (not isinstance(value, float) or math.isfinite(value)))


def _check_neighborhood_exists(neighborhood_id: str):
    if not nqry.exists(neighborhood_id):
        raise ValueError(f"Neighborhood id {neighborhood_id} does not exist.")
    return True


def check_valid_property(property_id: str, address: str,
                         neighborhood_id: str, price: float,
                         bedrooms: int, bathrooms: float,
                         latitude: float, longitude: float):
    if not _is_non_empty_string(property_id):
        raise ValueError("Property id must be a non-empty string.")
    if exists(property_id):
        raise ValueError(f"Property id {property_id} already exists.")
    _check_property_fields(
        address, neighborhood_id, price, bedrooms, bathrooms, latitude,
        longitude,
    )
    _check_neighborhood_exists(neighborhood_id)
    return True


def _check_property_fields(address: str, neighborhood_id: str, price: float,
                           bedrooms: int, bathrooms: float, latitude: float,
                           longitude: float):
    if not _is_non_empty_string(address):
        raise ValueError("Property address must be a non-empty string.")
    if not _is_non_empty_string(neighborhood_id):
        raise ValueError("Neighborhood id must be a non-empty string.")
    if not _is_number(price) or price < 0:
        raise ValueError("Price must be a non-negative number.")
    if (not isinstance(bedrooms, int) or isinstance(bedrooms, bool)
            or bedrooms < 0):
        raise ValueError("Bedrooms must be a non-negative integer.")
    if not _is_number(bathrooms) or bathrooms < 0:
        raise ValueError("Bathrooms must be a non-negative number.")
    if not _is_number(latitude) or not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90.")
    if not _is_number(longitude) or not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180.")
    return True


def create(property_id: str, address: str, neighborhood_id: str,
           price: float, bedrooms: int, bathrooms: float,
           latitude: float, longitude: float):
    """Create a property record in the in-memory test data."""
    check_valid_property(
        property_id, address, neighborhood_id, price, bedrooms, bathrooms,
        latitude, longitude,
    )
    if not is_db_up():
        print("Database is down.")
        return None

    PROPERTY_TEST_DATA[property_id] = {
        "address": address,
        "neighborhood_id": neighborhood_id,
        "price": price,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "latitude": latitude,
        "longitude": longitude,
    }
    return {ID: property_id, **PROPERTY_TEST_DATA[property_id]}


def update(property_id: str, changes: dict):
    """Update a property and return it, or None if it does not exist."""
    if not is_db_up():
        print("Database is down.")
        return None
    unknown = set(changes) - set(UPDATABLE_FIELDS)
    if unknown:
        raise ValueError(f"Cannot update fields: {sorted(unknown)}.")
    if property_id not in PROPERTY_TEST_DATA:
        return None

    updated = {**PROPERTY_TEST_DATA[property_id], **changes}
    _check_property_fields(
        updated["address"], updated["neighborhood_id"], updated["price"],
        updated["bedrooms"], updated["bathrooms"], updated["latitude"],
        updated["longitude"],
    )
    if "neighborhood_id" in changes:
        _check_neighborhood_exists(updated["neighborhood_id"])
    PROPERTY_TEST_DATA[property_id] = updated
    return {ID: property_id, **updated}


def delete(property_id: str):
    """Delete a property; return False if missing and None if the database
    is down.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    return PROPERTY_TEST_DATA.pop(property_id, None) is not None
