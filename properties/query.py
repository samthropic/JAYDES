#!/usr/bin/env python3

import math

import data.db_connect as dbc
from data.db_connect import is_db_up
import neighborhoods.query as nqry

ID = "id"
PROPERTIES_COLLECTION = "properties"
UPDATABLE_FIELDS = (
    "address", "neighborhood_id", "price", "bedrooms", "bathrooms",
    "latitude", "longitude",
)

PROPERTY_TEST_DATA = {
    "prop-001": {
        "address": "125 Perry Street, New York, NY",
        "neighborhood_id": "73a1b2c3-d4e5-6f7a-8b9c-0123456789ab",
        "price": 1850000,
        "bedrooms": 2,
        "bathrooms": 2,
        "latitude": 40.7358,
        "longitude": -74.0068,
    },
    "prop-002": {
        "address": "210 West 89th Street, New York, NY",
        "neighborhood_id": "84b2c3d4-e5f6-7a8b-9c0d-123456789abc",
        "price": 2450000,
        "bedrooms": 3,
        "bathrooms": 2,
        "latitude": 40.7901,
        "longitude": -73.9745,
    },
    "prop-003": {
        "address": "184 Bedford Avenue, Brooklyn, NY",
        "neighborhood_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
        "price": 1350000,
        "bedrooms": 2,
        "bathrooms": 2,
        "latitude": 40.7163,
        "longitude": -73.9582,
    },
    "prop-004": {
        "address": "52 8th Avenue, Brooklyn, NY",
        "neighborhood_id": "5f8a3c2b-1e9d-4a7b-8c6d-2f3e4a5b6c7d",
        "price": 1950000,
        "bedrooms": 3,
        "bathrooms": 2,
        "latitude": 40.6761,
        "longitude": -73.9734,
    },
    "prop-005": {
        "address": "31-18 Broadway, Queens, NY",
        "neighborhood_id": "9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d",
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


def _ensure_seeded():
    """Insert the sample properties when the collection is empty."""
    dbc.connect_db()
    if dbc.read(PROPERTIES_COLLECTION):
        return
    for property_id, data in PROPERTY_TEST_DATA.items():
        dbc.create(PROPERTIES_COLLECTION, {ID: property_id, **data})


def read(property_id: str = None):
    """
    Return all properties or the property with the requested id from seDB.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    _ensure_seeded()
    if property_id is None:
        return dbc.read(PROPERTIES_COLLECTION)
    property_record = dbc.read_one(PROPERTIES_COLLECTION, {ID: property_id})
    if property_record is not None:
        property_record.pop(dbc.MONGO_ID, None)
    return property_record


def search_by_price(min_price=None, max_price=None):
    """Return properties within an inclusive price range from seDB."""
    if min_price is None and max_price is None:
        raise ValueError("At least one price bound is required.")
    if min_price is not None and (
            not _is_number(min_price) or min_price < 0):
        raise ValueError("Minimum price must be a non-negative number.")
    if max_price is not None and (
            not _is_number(max_price) or max_price < 0):
        raise ValueError("Maximum price must be a non-negative number.")
    if (min_price is not None and max_price is not None
            and min_price > max_price):
        raise ValueError("Minimum price cannot exceed maximum price.")
    if not is_db_up():
        print("Database is down.")
        return None

    price_filter = {}
    if min_price is not None:
        price_filter["$gte"] = min_price
    if max_price is not None:
        price_filter["$lte"] = max_price
    _ensure_seeded()
    return dbc.read(PROPERTIES_COLLECTION, filt={"price": price_filter})


def exists(property_id: str):
    """
    Check if a property exists in seDB.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    _ensure_seeded()
    return dbc.read_one(PROPERTIES_COLLECTION, {ID: property_id}) is not None


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
    """Create a property record in seDB."""
    check_valid_property(
        property_id, address, neighborhood_id, price, bedrooms, bathrooms,
        latitude, longitude,
    )
    if not is_db_up():
        print("Database is down.")
        return None

    property_record = {
        ID: property_id,
        "address": address,
        "neighborhood_id": neighborhood_id,
        "price": price,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "latitude": latitude,
        "longitude": longitude,
    }
    dbc.create(PROPERTIES_COLLECTION, property_record)
    return read(property_id)


def update(property_id: str, changes: dict):
    """Update a property and return it, or None if it does not exist."""
    if not is_db_up():
        print("Database is down.")
        return None
    unknown = set(changes) - set(UPDATABLE_FIELDS)
    if unknown:
        raise ValueError(f"Cannot update fields: {sorted(unknown)}.")
    _ensure_seeded()
    property_record = dbc.read_one(PROPERTIES_COLLECTION, {ID: property_id})
    if property_record is None:
        return None
    property_record.pop(dbc.MONGO_ID, None)

    updated = {**property_record, **changes}
    _check_property_fields(
        updated["address"], updated["neighborhood_id"], updated["price"],
        updated["bedrooms"], updated["bathrooms"], updated["latitude"],
        updated["longitude"],
    )
    if "neighborhood_id" in changes:
        _check_neighborhood_exists(updated["neighborhood_id"])
    if changes:
        dbc.update(PROPERTIES_COLLECTION, {ID: property_id}, changes)
    return read(property_id)


def delete(property_id: str):
    """Delete a property; return False if missing and None if the database
    is down.
    """
    if not is_db_up():
        print("Database is down.")
        return None
    _ensure_seeded()
    return dbc.delete(PROPERTIES_COLLECTION, {ID: property_id}) > 0
