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


def test_get_neighborhoods():
    resp = TEST_CLIENT.get(ep.NEIGHBORHOODS_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.NEIGHBORHOODS_RESP in resp_json
    neighborhoods = resp_json[ep.NEIGHBORHOODS_RESP]
    assert isinstance(neighborhoods, list)
    assert len(neighborhoods) > 0
    for neighborhood in neighborhoods:
        assert 'id' in neighborhood
        assert 'name' in neighborhood
        assert 'state_id' in neighborhood


def test_post_neighborhood(new_neighborhood):
    with patch.dict(nqry.NEIGHBORHOOD_TEST_DATA):
        resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)
    
    assert resp.status_code == CREATED
    data = resp.get_json()['Neighborhood']
    assert data['id'] == new_neighborhood['id']
    assert data['name'] == new_neighborhood['name']
    assert data['state_id'] == new_neighborhood['state_id']


def test_post_neighborhood_missing_optional_name(new_neighborhood):
    del new_neighborhood['name']
    
    with patch.dict(nqry.NEIGHBORHOOD_TEST_DATA):
        resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)
        
    assert resp.status_code == CREATED
    data = resp.get_json()['Neighborhood']
    assert data['name'] == 'Unnamed Neighborhood'


def test_post_neighborhood_already_exists(new_neighborhood):
    new_neighborhood['id'] = '73a1b2c3-d4e5-6f7a-8b9c-0123456789ab'
    resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)
    assert resp.status_code == CONFLICT


def test_post_neighborhood_missing_id(new_neighborhood):
    del new_neighborhood['id']
    resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)
    assert resp.status_code == BAD_REQUEST


def test_post_neighborhood_missing_state(new_neighborhood):
    del new_neighborhood['state_id']
    resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)
    assert resp.status_code == BAD_REQUEST


def test_post_neighborhood_bad_id_format(new_neighborhood):
    new_neighborhood['id'] = 'too-short'
    resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)
    assert resp.status_code == BAD_REQUEST


def test_post_neighborhood_unknown_state(new_neighborhood):
    new_neighborhood['state_id'] = 'ZZ'
    resp = TEST_CLIENT.post(ep.NEIGHBORHOODS_EP, json=new_neighborhood)
    assert resp.status_code == BAD_REQUEST


def test_get_neighborhood_by_id():
    valid_id = "73a1b2c3-d4e5-6f7a-8b9c-0123456789ab"
    
    resp = TEST_CLIENT.get(f"{ep.NEIGHBORHOODS_EP}/{valid_id}")
    assert resp.status_code == OK
    
    resp_json = resp.get_json()
    assert resp_json['id'] == valid_id
    assert 'name' in resp_json
    assert 'state_id' in resp_json


def test_get_missing_neighborhood_by_id():
    resp = TEST_CLIENT.get(f"{ep.NEIGHBORHOODS_EP}/missing-neighborhood")
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


def test_get_property_by_id():
    resp = TEST_CLIENT.get(f"{ep.PROPERTIES_EP}/prop-001")
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert resp_json['id'] == 'prop-001'
    assert 'address' in resp_json


def test_get_missing_property_by_id():
    resp = TEST_CLIENT.get(f"{ep.PROPERTIES_EP}/missing-prop")
    assert resp.status_code == NOT_FOUND


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