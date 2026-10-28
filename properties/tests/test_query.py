from unittest.mock import patch

import pytest

import data.db_connect as dbc
from data.db_fixture import clear_properties as clear_property_collection
import properties.query as qry


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


def test_check_valid_property(test_property):
    with patch("properties.query.nqry.exists", return_value=True):
        assert qry.check_valid_property(**test_property)


def test_create_property(test_property):
    with patch("properties.query.nqry.exists", return_value=True):
        created = qry.create(**test_property)

    assert created == {
        "id": test_property["property_id"],
        **{key: value for key, value in test_property.items()
           if key != "property_id"},
    }
    assert qry.read(test_property["property_id"]) == created


def test_create_property_requires_existing_neighborhood(test_property):
    with patch("properties.query.nqry.exists", return_value=False):
        with pytest.raises(ValueError, match="does not exist"):
            qry.create(**test_property)


def test_update_property(test_property):
    with patch("properties.query.nqry.exists", return_value=True):
        qry.create(**test_property)
        updated = qry.update("prop-test", {"price": 300000})

    assert updated["id"] == "prop-test"
    assert updated["price"] == 300000
    assert updated["address"] == test_property["address"]


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"price": -1}, "Price"),
        ({"neighborhood_id": "missing-neighborhood"}, "does not exist"),
        ({"id": "changed-id"}, "Cannot update fields"),
    ],
)
def test_update_property_rejects_invalid_changes(test_property, changes,
                                                 message):
    with patch("properties.query.nqry.exists", return_value=True):
        qry.create(**test_property)
    neighborhood_exists = (
        changes.get("neighborhood_id", test_property["neighborhood_id"])
        == test_property["neighborhood_id"]
    )
    with patch("properties.query.nqry.exists",
               return_value=neighborhood_exists):
        with pytest.raises(ValueError, match=message):
            qry.update("prop-test", changes)


def test_update_missing_property_returns_none():
    assert qry.update("missing-property", {"price": 100}) is None


def test_delete_property():
    assert qry.delete("prop-001") is True
    assert qry.delete("prop-001") is False


@patch("properties.query.is_db_up", return_value=False)
def test_update_and_delete_database_unavailable(mock_is_db_up):
    assert qry.update("prop-test", {"price": 100}) is None
    assert qry.delete("prop-test") is None


def test_each_property_has_required_fields():
    required_fields = {
        "address",
        "neighborhood_id",
        "price",
        "bedrooms",
        "bathrooms",
        "latitude",
        "longitude",
    }

    for property_id, property_data in qry.PROPERTY_TEST_DATA.items():
        assert isinstance(property_id, str)
        assert property_id
        assert required_fields <= property_data.keys()
        assert isinstance(property_data["neighborhood_id"], str)
        assert property_data["neighborhood_id"]


def test_property_exists_and_read_returns_record():
    assert qry.exists("prop-001")
    prop = qry.read("prop-001")
    assert prop["id"] == "prop-001"
    assert prop["address"]


def test_read_returns_seeded_properties():
    properties = qry.read()
    assert len(properties) == len(qry.PROPERTY_TEST_DATA)
    assert {prop["id"] for prop in properties} == set(qry.PROPERTY_TEST_DATA)
    assert all(dbc.MONGO_ID not in prop for prop in properties)


def test_read_missing_property_returns_none():
    assert qry.read("missing-prop") is None


@pytest.mark.parametrize(
    "property_id",
    [pytest.param("", id="empty")],
)
def test_check_valid_property_invalid_id(property_id, test_property):
    with pytest.raises(ValueError):
        qry.check_valid_property(
            **{**test_property, "property_id": property_id}
        )


def test_check_valid_property_duplicate_id(test_property):
    test_property["property_id"] = "prop-001"
    with pytest.raises(ValueError):
        qry.check_valid_property(**test_property)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("address", "", id="address"),
        pytest.param("neighborhood_id", "", id="neighborhood-id"),
    ],
)
def test_check_valid_property_empty_required_text(field, value, test_property):
    with pytest.raises(ValueError):
        qry.check_valid_property(**{**test_property, field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("price", -1, id="negative-price"),
        pytest.param("price", "250000", id="text-price"),
        pytest.param("price", float("inf"), id="infinite-price"),
        pytest.param("bedrooms", -1, id="negative-bedrooms"),
        pytest.param("bedrooms", 2.5, id="fractional-bedrooms"),
        pytest.param("bedrooms", True, id="boolean-bedrooms"),
        pytest.param("bathrooms", -1, id="negative-bathrooms"),
        pytest.param("bathrooms", "2", id="text-bathrooms"),
        pytest.param("bathrooms", float("inf"), id="infinite-bathrooms"),
    ],
)
def test_check_valid_property_bad_numeric_fields(field, value, test_property):
    with pytest.raises(ValueError):
        qry.check_valid_property(**{**test_property, field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("latitude", 91, id="latitude-too-high"),
        pytest.param("latitude", "40.7", id="text-latitude"),
        pytest.param("longitude", -181, id="longitude-too-low"),
        pytest.param("longitude", float("inf"), id="infinite-longitude"),
    ],
)
def test_check_valid_property_bad_coordinates(field, value, test_property):
    with pytest.raises(ValueError):
        qry.check_valid_property(**{**test_property, field: value})
