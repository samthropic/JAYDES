import pytest

from data.db_fixture import clear_properties as clear_property_collection


@pytest.fixture
def test_property():
    return {
        "property_id": "prop-test",
        "address": "1 Test Street, Test City, NY",
        "neighborhood_id": "test-neighborhood",
        "price": 250000,
        "bedrooms": 3,
        "bathrooms": 2,
        "latitude": 40.7128,
        "longitude": -74.0060,
    }


@pytest.fixture(autouse=True)
def isolated_properties_collection():
    clear_property_collection()
    yield
    clear_property_collection()
