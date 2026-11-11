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


def _validate_numeric_range(
    min_value, max_value, field_label, allow_float=True
):
    """Validate inclusive numeric bounds for property search filters."""
    if min_value is None and max_value is None:
        raise ValueError(
            f"At least one {field_label.lower()} bound is required."
        )

    def _validate_bound(value, bound_name):
        if value is None:
            return None
        if not _is_number(value):
            raise ValueError(
                f"{bound_name} {field_label} must be a valid number."
            )

        if _is_integer(value):
            numeric = value
        else:
            if not allow_float and not value.is_integer():
                raise ValueError(
                    f"{bound_name} {field_label} must be a "
                    "non-negative integer."
                )
            numeric = int(value) if not allow_float else value

        if numeric < 0:
            raise ValueError(
                f"{bound_name} {field_label} must be non-negative."
            )
        return numeric

    min_value = _validate_bound(min_value, "Minimum")
    max_value = _validate_bound(max_value, "Maximum")
    if (
        min_value is not None
        and max_value is not None
        and min_value > max_value
    ):
        raise ValueError(
            f"Minimum {field_label.lower()} cannot exceed "
            f"maximum {field_label.lower()}."
        )
    return min_value, max_value


def search(
    min_price=None,
    max_price=None,
    min_bedrooms=None,
    max_bedrooms=None,
    min_bathrooms=None,
    max_bathrooms=None,
):
    """Return properties matching all supplied numeric range filters."""
    ranges = (
        ("price", min_price, max_price, True),
        ("bedrooms", min_bedrooms, max_bedrooms, False),
        ("bathrooms", min_bathrooms, max_bathrooms, True),
    )
    filters = {}
    for field_name, minimum, maximum, allow_float in ranges:
        if minimum is None and maximum is None:
            continue
        minimum, maximum = _validate_numeric_range(
            minimum,
            maximum,
            field_name,
            allow_float=allow_float,
        )
        field_filter = {}
        if minimum is not None:
            field_filter["$gte"] = minimum
        if maximum is not None:
            field_filter["$lte"] = maximum
        filters[field_name] = field_filter

    if not filters:
        raise ValueError("At least one property filter is required.")
    if not is_db_up():
        print("Database is down.")
        return None

    _ensure_seeded()
    return dbc.read(PROPERTIES_COLLECTION, filt=filters)


def search_by_price(min_price=None, max_price=None):
    """Return properties within an inclusive price range from seDB."""
    return search(min_price=min_price, max_price=max_price)


def search_by_bedrooms(min_bedrooms=None, max_bedrooms=None):
    """Return properties within an inclusive bedroom range from seDB."""
    return search(
        min_bedrooms=min_bedrooms,
        max_bedrooms=max_bedrooms,
    )


def search_by_bathrooms(min_bathrooms=None, max_bathrooms=None):
    """Return properties within an inclusive bathroom range from seDB."""
    return search(
        min_bathrooms=min_bathrooms,
        max_bathrooms=max_bathrooms,
    )


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


def _is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


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
    if not _is_integer(bedrooms) or bedrooms < 0:
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
    if not is_db_up():
        print("Database is down.")
        return None
    check_valid_property(
        property_id, address, neighborhood_id, price, bedrooms, bathrooms,
        latitude, longitude,
    )

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
