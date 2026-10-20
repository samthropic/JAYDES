from unittest.mock import patch

import pytest

import properties.query as qry

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
}


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


@patch.object(qry, "PROPERTY_TEST_DATA", PROPERTY_TEST_DATA)
def test_check_valid_property(test_property):
    with patch("properties.query.nqry.exists", return_value=True):
        assert qry.check_valid_property(**test_property)


def test_create_property(test_property):
    with patch.object(qry, "PROPERTY_TEST_DATA", dict(PROPERTY_TEST_DATA)):
        with patch("properties.query.nqry.exists", return_value=True):
            created = qry.create(**test_property)

        expected_stored = {key: value for key, value in test_property.items()
                           if key != "property_id"}
        assert (qry.PROPERTY_TEST_DATA[test_property["property_id"]]
                == expected_stored)

    assert created == {
        "id": test_property["property_id"],
        **{key: value for key, value in test_property.items()
           if key != "property_id"},
    }


def test_create_property_requires_existing_neighborhood(test_property):
    with patch.object(qry, "PROPERTY_TEST_DATA", dict(PROPERTY_TEST_DATA)):
        with patch("properties.query.nqry.exists", return_value=False):
            with pytest.raises(ValueError, match="does not exist"):
                qry.create(**test_property)


@patch.object(qry, "PROPERTY_TEST_DATA", PROPERTY_TEST_DATA)
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


@patch.object(qry, "PROPERTY_TEST_DATA", PROPERTY_TEST_DATA)
def test_property_exists_and_read_returns_record():
    assert qry.exists("prop-001")
    prop = qry.read("prop-001")
    assert prop["id"] == "prop-001"
    assert prop["address"]


@patch.object(qry, "PROPERTY_TEST_DATA", PROPERTY_TEST_DATA)
def test_read_missing_property_returns_none():
    assert qry.read("missing-prop") is None

@pytest.mark.parametrize(
    "property_id",
    [
        pytest.param("", id="empty"),
        pytest.param(
            "prop-001",
            id="duplicate",
            marks=pytest.mark.skip(reason="Covered by the patched duplicate-id test."),
        ),
    ],
)
@patch.object(qry, "PROPERTY_TEST_DATA", PROPERTY_TEST_DATA)
def test_check_valid_property_invalid_id(property_id, test_property):
    with pytest.raises(ValueError):
        qry.check_valid_property(**{**test_property, "property_id": property_id})


@patch.object(qry, "PROPERTY_TEST_DATA", {"prop-test": {}})
def test_check_valid_property_duplicate_id(test_property):
    with pytest.raises(ValueError):
        qry.check_valid_property(**test_property)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("address", "", id="address"),
        pytest.param("neighborhood_id", "", id="neighborhood-id"),
    ],
)
@patch.object(qry, "PROPERTY_TEST_DATA", PROPERTY_TEST_DATA)
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
@patch.object(qry, "PROPERTY_TEST_DATA", PROPERTY_TEST_DATA)
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
@patch.object(qry, "PROPERTY_TEST_DATA", PROPERTY_TEST_DATA)
def test_check_valid_property_bad_coordinates(field, value, test_property):
    with pytest.raises(ValueError):
        qry.check_valid_property(**{**test_property, field: value})
