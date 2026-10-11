import pytest

import properties.query as qry

TEST_PROP = qry.TEST_PROPERTY


def test_check_valid_property():
    assert qry.check_valid_property(**TEST_PROP)


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


@pytest.mark.parametrize(
    "property_id",
    [pytest.param("", id="empty"), pytest.param("prop-001", id="duplicate")],
)
def test_check_valid_property_invalid_id(property_id):
    with pytest.raises(ValueError):
        qry.check_valid_property(**{**TEST_PROP, "property_id": property_id})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("address", "", id="address"),
        pytest.param("neighborhood_id", "", id="neighborhood-id"),
    ],
)
def test_check_valid_property_empty_required_text(field, value):
    with pytest.raises(ValueError):
        qry.check_valid_property(**{**TEST_PROP, field: value})


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
def test_check_valid_property_bad_numeric_fields(field, value):
    with pytest.raises(ValueError):
        qry.check_valid_property(**{**TEST_PROP, field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("latitude", 91, id="latitude-too-high"),
        pytest.param("latitude", "40.7", id="text-latitude"),
        pytest.param("longitude", -181, id="longitude-too-low"),
        pytest.param("longitude", float("inf"), id="infinite-longitude"),
    ],
)
def test_check_valid_property_bad_coordinates(field, value):
    with pytest.raises(ValueError):
        qry.check_valid_property(**{**TEST_PROP, field: value})
