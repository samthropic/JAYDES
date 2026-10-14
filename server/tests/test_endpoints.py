from http.client import (
    BAD_REQUEST,
    CONFLICT,
    CREATED,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
)

from unittest.mock import patch

import pytest

from server import endpoints as ep
import states.query as sqry

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


NEW_STATE = {
    'id': 'TS',
    'name': 'Test State',
    'capital': 'Test Capital',
    'population': 1000000,
    'area_sq_miles': 50000,
    'region_id': 'NE',
}


def test_post_state():
    with patch.dict(sqry.STATE_TEST_DATA):
        resp = TEST_CLIENT.post(ep.STATES_EP, json=NEW_STATE)
    assert resp.status_code == CREATED
    state = resp.get_json()[ep.STATE_RESP]
    assert state['id'] == NEW_STATE['id']
    assert state['name'] == NEW_STATE['name']


def test_post_state_already_exists():
    resp = TEST_CLIENT.post(ep.STATES_EP, json={**NEW_STATE, 'id': 'AL'})
    assert resp.status_code == CONFLICT


def test_post_state_bad_code():
    resp = TEST_CLIENT.post(ep.STATES_EP, json={**NEW_STATE, 'id': 'TOO'})
    assert resp.status_code == BAD_REQUEST


def test_post_state_unknown_region():
    resp = TEST_CLIENT.post(ep.STATES_EP, json={**NEW_STATE,
                                                'region_id': 'ZZ'})
    assert resp.status_code == BAD_REQUEST


def test_post_state_missing_field():
    bad_state = {k: v for k, v in NEW_STATE.items() if k != 'name'}
    resp = TEST_CLIENT.post(ep.STATES_EP, json=bad_state)
    assert resp.status_code == BAD_REQUEST


@patch('states.query.is_db_up', return_value=False, autospec=True)
def test_post_state_db_unavailable(mock_is_db_up):
    resp = TEST_CLIENT.post(ep.STATES_EP, json=NEW_STATE)
    assert resp.status_code == SERVICE_UNAVAILABLE


def test_get_regions():
    resp = TEST_CLIENT.get(ep.REGIONS_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.REGIONS_RESP in resp_json
    assert isinstance(resp_json[ep.REGIONS_RESP], dict)

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
