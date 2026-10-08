#!/usr/bin/env python3

import math

ID = "id"

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


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _is_number(value):
    return (isinstance(value, (int, float))
            and not isinstance(value, bool)
            and (not isinstance(value, float) or math.isfinite(value)))


def check_valid_property(property_id: str, address: str,
                         neighborhood_id: str, price: float,
                         bedrooms: int, bathrooms: float,
                         latitude: float, longitude: float):
    if not _is_non_empty_string(property_id):
        raise ValueError("Property id must be a non-empty string.")
    if property_id in PROPERTY_TEST_DATA:
        raise ValueError(f"Property id {property_id} already exists.")
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
