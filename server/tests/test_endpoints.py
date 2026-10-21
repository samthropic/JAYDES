from http.client import (
    BAD_REQUEST,
    CONFLICT,
    CREATED,
    FORBIDDEN,
    NO_CONTENT,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
)

from unittest.mock import patch

import pytest

from server import endpoints as ep
import states.query as sqry
import neighborhoods.query as nqry
import properties.query as pqry

TEST_CLIENT = ep.app.test_client()


def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json


def test_get_states():
    resp = TEST_CLIENT.get(ep.STATES_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.STATES_RESP in resp_json
    states = resp_json[ep.STATES_RESP]
    assert isinstance(states, list)
    assert len(states) > 0
    for state in states:
        assert 'id' in state
        assert 'name' in state


def test_states_in_swagger():
    resp = TEST_CLIENT.get('/swagger.json')
    assert resp.status_code == OK
    assert 'State' in resp.get_json()['definitions']


@patch('states.query.is_db_up', return_value=False, autospec=True)
def test_get_states_db_unavailable(mock_is_db_up):
    resp = TEST_CLIENT.get(ep.STATES_EP)
    assert resp.status_code == SERVICE_UNAVAILABLE


def test_get_state_by_id():
    resp = TEST_CLIENT.get(f'{ep.STATES_EP}/AL')
    assert resp.status_code == OK
    state = resp.get_json()[ep.STATE_RESP]
    assert state['id'] == 'AL'
    assert state['name'] == 'Alabama'


def test_get_missing_state_by_id():
    resp = TEST_CLIENT.get(f'{ep.STATES_EP}/ZZ')
    assert resp.status_code == NOT_FOUND


@patch('states.query.is_db_up', return_value=False, autospec=True)
def test_get_state_by_id_db_unavailable(mock_is_db_up):
    resp = TEST_CLIENT.get(f'{ep.STATES_EP}/AL')
    assert resp.status_code == SERVICE_UNAVAILABLE


def test_delete_state():
    resp = TEST_CLIENT.delete(f'{ep.STATES_EP}/AL')
    assert resp.status_code == NO_CONTENT
    resp = TEST_CLIENT.get(f'{ep.STATES_EP}/AL')
    assert resp.status_code == NOT_FOUND


def test_delete_missing_state():
    resp = TEST_CLIENT.delete(f'{ep.STATES_EP}/ZZ')
    assert resp.status_code == NOT_FOUND


@patch('states.query.is_db_up', return_value=False, autospec=True)
def test_delete_state_db_unavailable(mock_is_db_up):
    resp = TEST_CLIENT.delete(f'{ep.STATES_EP}/AL')
    assert resp.status_code == SERVICE_UNAVAILABLE


@pytest.fixture
def new_state():
    """A valid state that is not in the sample data."""
    return {
        'id': 'TS',
        'name': 'Test State',
        'capital': 'Test Capital',
        'population': 1000000,
        'area_sq_miles': 50000,
        'region_id': 'NE',
    }


def test_post_state(new_state):
    with patch.dict(sqry.STATE_TEST_DATA):
        resp = TEST_CLIENT.post(ep.STATES_EP, json=new_state)
    assert resp.status_code == CREATED
    state = resp.get_json()[ep.STATE_RESP]
    assert state['id'] == new_state['id']
    assert state['name'] == new_state['name']


def test_post_state_already_exists(new_state):
    new_state['id'] = 'AL'
    resp = TEST_CLIENT.post(ep.STATES_EP, json=new_state)
    assert resp.status_code == CONFLICT


def test_post_state_bad_code(new_state):
    new_state['id'] = 'TOO'
    resp = TEST_CLIENT.post(ep.STATES_EP, json=new_state)
    assert resp.status_code == BAD_REQUEST


def test_post_state_unknown_region(new_state):
    new_state['region_id'] = 'ZZ'
    resp = TEST_CLIENT.post(ep.STATES_EP, json=new_state)
    assert resp.status_code == BAD_REQUEST


def test_post_state_missing_field(new_state):
    del new_state['name']
    resp = TEST_CLIENT.post(ep.STATES_EP, json=new_state)
    assert resp.status_code == BAD_REQUEST


@patch('states.query.is_db_up', return_value=False, autospec=True)
def test_post_state_db_unavailable(mock_is_db_up, new_state):
    resp = TEST_CLIENT.post(ep.STATES_EP, json=new_state)
    assert resp.status_code == SERVICE_UNAVAILABLE


def test_get_regions():
    resp = TEST_CLIENT.get(ep.REGIONS_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.REGIONS_RESP in resp_json
    assert isinstance(resp_json[ep.REGIONS_RESP], dict)


@pytest.fixture
def new_neighborhood():
    """A valid neighborhood that is not in the sample data."""
    return {
        'id': '11112222-3333-4444-5555-666677778888',
        'name': 'Test POST Neighborhood',
        'state_id': 'AL'
    }


@pytest.fixture
def valid_patch_id():
    """Provides a known, valid ID from the test data."""
    return "73a1b2c3-d4e5-6f7a-8b9c-0123456789ab"


@pytest.fixture
def mock_neighborhood_db():
    """Automatically patches the database dictionary for the duration of the test."""
    fresh_test_data = {
        "73a1b2c3-d4e5-6f7a-8b9c-0123456789ab": {
            "name": "Greenwich Village",
            "state_id": "AL"
        },
        "550e8400-e29b-41d4-a716-446655440000": {
            "name": "Test Neighborhood",
            "state_id": "AL"
        }
    }
    with patch.dict(nqry.NEIGHBORHOOD_TEST_DATA, fresh_test_data, clear=True) as patched_dict:
        yield patched_dict


def test_get_neighborhoods(mock_neighborhood_db):
    resp = TEST_CLIENT.get(ep.NEIGHBORHOODS_EP)
    assert resp.status_code == OK
    
    resp_json = resp.get_json()
    assert ep.NEIGHBORHOODS_RESP in resp_json
    
    neighborhoods = resp_json[ep.NEIGHBORHOODS_RESP]
    assert isinstance(neighborhoods, list)
    assert len(neighborhoods) == 2      # this should match entries in mock_neighborhood_db
    
    for neighborhood in neighborhoods:
        assert 'id' in neighborhood
        assert 'name' in neighborhood
        assert 'state_id' in neighborhood


def test_get_neighborhood_by_id(valid_patch_id, mock_neighborhood_db):
    resp = TEST_CLIENT.get(f"{ep.NEIGHBORHOODS_EP}/{valid_patch_id}")
    assert resp.status_code == OK
    
    resp_json = resp.get_json()
    assert resp_json['id'] == valid_patch_id
    assert resp_json['name'] == "Greenwich Village"
    assert resp_json['state_id'] == "AL"


def test_get_missing_neighborhood_by_id(mock_neighborhood_db):
    resp = TEST_CLIENT.get(f"{ep.NEIGHBORHOODS_EP}/missing-neighborhood")
    assert resp.status_code == NOT_FOUND


def test_post_neighborhood(new_neighborhood, mock_neighborhood_db):
    resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)

    assert resp.status_code == CREATED
    data = resp.get_json()['Neighborhood']
    assert data['id'] == new_neighborhood['id']
    assert data['name'] == new_neighborhood['name']
    assert data['state_id'] == new_neighborhood['state_id']


def test_post_neighborhood_missing_optional_name(new_neighborhood, mock_neighborhood_db):
    del new_neighborhood['name']
    resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)
        
    assert resp.status_code == CREATED
    data = resp.get_json()['Neighborhood']
    assert data['name'] == 'Unnamed Neighborhood'


def test_post_neighborhood_already_exists(new_neighborhood, mock_neighborhood_db):
    new_neighborhood['id'] = '73a1b2c3-d4e5-6f7a-8b9c-0123456789ab'
    resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)
    assert resp.status_code == CONFLICT


def test_post_neighborhood_missing_id(new_neighborhood, mock_neighborhood_db):
    del new_neighborhood['id']
    resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)
    assert resp.status_code == BAD_REQUEST


def test_post_neighborhood_missing_state(new_neighborhood, mock_neighborhood_db):
    del new_neighborhood['state_id']
    resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)
    assert resp.status_code == BAD_REQUEST


def test_post_neighborhood_bad_id_format(new_neighborhood, mock_neighborhood_db):
    new_neighborhood['id'] = 'too-short'
    resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)
    assert resp.status_code == BAD_REQUEST


def test_post_neighborhood_unknown_state(new_neighborhood, mock_neighborhood_db):
    new_neighborhood['state_id'] = 'ZZ'
    resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)
    assert resp.status_code == BAD_REQUEST


@patch('states.query.exists', return_value=True)
def test_patch_neighborhood_state_only(mock_state_exists, valid_patch_id, mock_neighborhood_db):
    changes = {"state_id": "CA"}
    resp = TEST_CLIENT.patch(f"{ep.NEIGHBORHOODS_EP}/{valid_patch_id}", json=changes)
    assert resp.status_code == OK
    data = resp.get_json()['Neighborhood']
    assert data['state_id'] == "CA"
    assert data['name'] == "Greenwich Village"


@patch('states.query.exists', return_value=True)
def test_patch_neighborhood_multiple_fields(mock_state_exists, valid_patch_id, mock_neighborhood_db):
    changes = {
        "name": "Phoenix", 
        "state_id": "AZ"
    }

    resp = TEST_CLIENT.patch(f"{ep.NEIGHBORHOODS_EP}/{valid_patch_id}", json=changes)
    assert resp.status_code == OK
    data = resp.get_json()['Neighborhood']
    assert data['name'] == "Phoenix"
    assert data['state_id'] == "AZ"


def test_patch_neighborhood_name_only(valid_patch_id, mock_neighborhood_db):
    changes = {"name": "Updated Village"}
    resp = TEST_CLIENT.patch(f"{ep.NEIGHBORHOODS_EP}/{valid_patch_id}", json=changes)
    assert resp.status_code == OK
    data = resp.get_json()['Neighborhood']
    assert data['name'] == "Updated Village"
    assert data['state_id'] == "AL"


def test_patch_neighborhood_empty_payload(valid_patch_id, mock_neighborhood_db):
    resp = TEST_CLIENT.patch(f"{ep.NEIGHBORHOODS_EP}/{valid_patch_id}", json={})
    assert resp.status_code == BAD_REQUEST


def test_patch_neighborhood_invalid_data(valid_patch_id, mock_neighborhood_db):
    changes = {"state_id": "BAD_STATE_ID"}
    resp = TEST_CLIENT.patch(f"{ep.NEIGHBORHOODS_EP}/{valid_patch_id}", json=changes)
    assert resp.status_code == BAD_REQUEST


def test_patch_neighborhood_not_found(mock_neighborhood_db):
    changes = {"name": "Ghost Town"}
    missing_id = "missing-neighborhood-id-1234"

    resp = TEST_CLIENT.patch(f"{ep.NEIGHBORHOODS_EP}/{missing_id}", json=changes)
    assert resp.status_code == NOT_FOUND


def test_get_properties():
    resp = TEST_CLIENT.get(ep.PROPERTIES_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.PROPERTIES_RESP in resp_json
    properties = resp_json[ep.PROPERTIES_RESP]
    assert isinstance(properties, list)
    assert len(properties) > 0
    for prop in properties:
        assert 'id' in prop
        assert 'address' in prop
        assert 'neighborhood_id' in prop


NEW_PROPERTY = {
    'id': 'prop-api-test',
    'address': '1 Test Street, Test City, NY',
    'neighborhood_id': '73a1b2c3-d4e5-6f7a-8b9c-0123456789ab',
    'price': 250000,
    'bedrooms': 3,
    'bathrooms': 2,
    'latitude': 40.7128,
    'longitude': -74.0060,
}


def test_post_property():
    with patch.dict(pqry.PROPERTY_TEST_DATA):
        resp = TEST_CLIENT.post(ep.PROPERTIES_EP, json=NEW_PROPERTY)

    assert resp.status_code == CREATED
    property_record = resp.get_json()[ep.PROPERTY_RESP]
    assert property_record['id'] == NEW_PROPERTY['id']
    assert property_record['address'] == NEW_PROPERTY['address']
    assert property_record['neighborhood_id'] == NEW_PROPERTY['neighborhood_id']


def test_post_property_already_exists():
    resp = TEST_CLIENT.post(ep.PROPERTIES_EP,
                            json={**NEW_PROPERTY, 'id': 'prop-001'})
    assert resp.status_code == CONFLICT


def test_post_property_unknown_neighborhood():
    resp = TEST_CLIENT.post(
        ep.PROPERTIES_EP,
        json={**NEW_PROPERTY, 'neighborhood_id': 'missing-neighborhood'},
    )
    assert resp.status_code == BAD_REQUEST


def test_post_property_missing_field():
    incomplete_property = {
        key: value for key, value in NEW_PROPERTY.items() if key != 'price'
    }
    resp = TEST_CLIENT.post(ep.PROPERTIES_EP, json=incomplete_property)
    assert resp.status_code == BAD_REQUEST


@patch('properties.query.is_db_up', return_value=False, autospec=True)
def test_post_property_db_unavailable(mock_is_db_up):
    resp = TEST_CLIENT.post(ep.PROPERTIES_EP, json=NEW_PROPERTY)
    assert resp.status_code == SERVICE_UNAVAILABLE


def test_get_property_by_id():
    resp = TEST_CLIENT.get(f"{ep.PROPERTIES_EP}/prop-001")
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert resp_json['id'] == 'prop-001'
    assert 'address' in resp_json


def test_get_missing_property_by_id():
    resp = TEST_CLIENT.get(f"{ep.PROPERTIES_EP}/missing-prop")
    assert resp.status_code == NOT_FOUND


def test_patch_property():
    with patch.dict(pqry.PROPERTY_TEST_DATA):
        resp = TEST_CLIENT.patch(
            f"{ep.PROPERTIES_EP}/prop-001", json={"price": 1900000}
        )

    assert resp.status_code == OK
    property_record = resp.get_json()[ep.PROPERTY_RESP]
    assert property_record['id'] == 'prop-001'
    assert property_record['price'] == 1900000
    assert property_record['address'] == '125 Perry Street, New York, NY'


def test_patch_property_invalid_data():
    resp = TEST_CLIENT.patch(
        f"{ep.PROPERTIES_EP}/prop-001", json={"price": -1}
    )
    assert resp.status_code == BAD_REQUEST


def test_patch_property_unknown_neighborhood():
    resp = TEST_CLIENT.patch(
        f"{ep.PROPERTIES_EP}/prop-001",
        json={"neighborhood_id": "missing-neighborhood"},
    )
    assert resp.status_code == BAD_REQUEST


def test_patch_property_empty_changes():
    resp = TEST_CLIENT.patch(f"{ep.PROPERTIES_EP}/prop-001", json={})
    assert resp.status_code == BAD_REQUEST


def test_patch_missing_property():
    resp = TEST_CLIENT.patch(
        f"{ep.PROPERTIES_EP}/missing-property", json={"price": 100}
    )
    assert resp.status_code == NOT_FOUND


@patch('properties.query.is_db_up', return_value=False, autospec=True)
def test_patch_property_db_unavailable(mock_is_db_up):
    resp = TEST_CLIENT.patch(
        f"{ep.PROPERTIES_EP}/prop-001", json={"price": 100}
    )
    assert resp.status_code == SERVICE_UNAVAILABLE


def test_delete_property():
    with patch.dict(pqry.PROPERTY_TEST_DATA):
        resp = TEST_CLIENT.delete(f"{ep.PROPERTIES_EP}/prop-001")

    assert resp.status_code == NO_CONTENT


def test_delete_missing_property():
    resp = TEST_CLIENT.delete(f"{ep.PROPERTIES_EP}/missing-property")
    assert resp.status_code == NOT_FOUND


@patch('properties.query.is_db_up', return_value=False, autospec=True)
def test_delete_property_db_unavailable(mock_is_db_up):
    resp = TEST_CLIENT.delete(f"{ep.PROPERTIES_EP}/prop-001")
    assert resp.status_code == SERVICE_UNAVAILABLE


@patch('regions.query.is_db_up', return_value=False, autospec=True)
def test_get_regions_db_unavailable(mock_is_db_up):
    resp = TEST_CLIENT.get(ep.REGIONS_EP)
    assert resp.status_code == SERVICE_UNAVAILABLE


@patch('properties.query.is_db_up', return_value=False, autospec=True)
def test_get_properties_db_unavailable(mock_is_db_up):
    resp = TEST_CLIENT.get(ep.PROPERTIES_EP)
    assert resp.status_code == SERVICE_UNAVAILABLE


@patch('properties.query.is_db_up', return_value=False, autospec=True)
def test_get_property_by_id_db_unavailable(mock_is_db_up):
    resp = TEST_CLIENT.get(f"{ep.PROPERTIES_EP}/prop-001")
    assert resp.status_code == SERVICE_UNAVAILABLE


@patch('neighborhoods.query.is_db_up', return_value=False, autospec=True)
def test_get_neighborhoods_db_unavailable(mock_is_db_up):
    resp = TEST_CLIENT.get(ep.NEIGHBORHOODS_EP)
    assert resp.status_code == SERVICE_UNAVAILABLE


@patch('neighborhoods.query.is_db_up', return_value=False, autospec=True)
def test_get_neighborhood_by_id_db_unavailable(mock_is_db_up):
    dummy_id = "11111111-1111-1111-1111-111111111111"
    resp = TEST_CLIENT.get(f"{ep.NEIGHBORHOODS_EP}/{dummy_id}")
    assert resp.status_code == SERVICE_UNAVAILABLE

@patch('neighborhoods.query.is_db_up', return_value=False, autospec=True)
def test_post_neighborhood_db_unavailable(mock_is_db_up, new_neighborhood):
    resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)
    assert resp.status_code == SERVICE_UNAVAILABLE

@patch('neighborhoods.query.is_db_up', return_value=False, autospec=True)
def test_patch_neighborhood_db_unavailable(mock_is_db_up, valid_patch_id):
    changes = {"name": "Doesn't Matter"}
    resp = TEST_CLIENT.patch(f"{ep.NEIGHBORHOODS_EP}/{valid_patch_id}", json=changes)
    assert resp.status_code == SERVICE_UNAVAILABLE
