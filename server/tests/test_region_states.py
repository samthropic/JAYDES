"""Region-state endpoint contracts, isolated from MongoDB."""
from unittest.mock import patch

import pytest

from server import endpoints as ep


@pytest.fixture(autouse=True)
def seeded_db():
    """Override the package fixture: these tests use mocked query results."""
    yield


@pytest.fixture
def region_queries():
    with patch.object(ep.rqry, 'exists', return_value=True) as exists, \
            patch.object(ep.sqry, 'read', return_value=[]) as read:
        yield exists, read


def test_region_states_filters_by_parent(region_queries):
    exists, read = region_queries
    matching = [{'id': 'AK', 'region_id': 'MW'},
                {'id': 'AZ', 'region_id': 'MW'}]
    read.return_value = matching + [{'id': 'AL', 'region_id': 'SE'},
                                    {'id': 'TS', 'region_id': None},
                                    {'id': 'TX'}]
    response = ep.app.test_client().get('/regions/MW/states')
    assert response.status_code == 200
    assert response.get_json() == {ep.STATES_RESP: matching}
    exists.assert_called_once_with('MW')


def test_empty_region_states(region_queries):
    response = ep.app.test_client().get('/regions/NE/states')
    assert response.status_code == 200
    assert response.get_json() == {ep.STATES_RESP: []}


def test_missing_region_states(region_queries):
    exists, read = region_queries
    exists.return_value = False
    response = ep.app.test_client().get('/regions/ZZ/states')
    assert response.status_code == 404
    read.assert_not_called()


def test_region_lookup_unavailable(region_queries):
    exists, read = region_queries
    exists.return_value = None
    response = ep.app.test_client().get('/regions/MW/states')
    assert response.status_code == 503
    read.assert_not_called()


def test_states_lookup_unavailable(region_queries):
    _, read = region_queries
    read.return_value = None
    response = ep.app.test_client().get('/regions/MW/states')
    assert response.status_code == 503


def test_region_states_swagger():
    response = ep.app.test_client().get('/swagger.json')
    assert response.status_code == 200
    schema = response.get_json()
    operation = schema['paths']['/regions/{region_id}/states']['get']
    assert {'200', '404', '503'} <= set(operation['responses'])
    assert operation['responses']['200']['schema'] == {
        '$ref': '#/definitions/RegionStates'}
    items = schema['definitions']['RegionStates']['properties']['States:']
    assert items['type'] == 'array'
    assert items['items']['$ref'] == '#/definitions/State'
    assert 'region_id' in schema['definitions']['State']['properties']
