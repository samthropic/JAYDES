import pytest

import data.db_connect as dbc
import regions.query as rqry
import states.query as sqry


def _stored(collection, code):
    return dbc.read_one(collection, {'id': code})


def test_state_create_is_stored():
    sqry.create('TS', 1000000, 'Test Capital', 50000, 'Test State', 'NE')
    stored = _stored(sqry.STATES_COLLECTION, 'TS')
    assert stored['name'] == 'Test State'
    assert stored['capital'] == 'Test Capital'
    assert stored['population'] == 1000000
    assert stored['region_id'] == 'NE'


def test_state_create_unknown_region_is_not_stored():
    with pytest.raises(ValueError):
        sqry.create('TS', 1000000, 'Test Capital', 50000, 'Test State', 'ZZ')
    assert _stored(sqry.STATES_COLLECTION, 'TS') is None


def test_state_update_is_stored():
    sqry.update('AL', {'capital': 'Birmingham', 'region_id': 'NE'})
    stored = _stored(sqry.STATES_COLLECTION, 'AL')
    assert stored['capital'] == 'Birmingham'
    assert stored['region_id'] == 'NE'


def test_state_delete_removes_document():
    sqry.create('TS', 1000000, 'Test Capital', 50000, 'Test State')
    assert sqry.delete('TS') is True
    assert _stored(sqry.STATES_COLLECTION, 'TS') is None


def test_region_create_is_stored():
    rqry.create('TR', 'Test Region', 500000, 'A test region')
    stored = _stored(rqry.REGIONS_COLLECTION, 'TR')
    assert stored['name'] == 'Test Region'
    assert stored['population'] == 500000
    assert stored['description'] == 'A test region'


def test_region_update_is_stored():
    rqry.update('NE', {'name': 'New Northeast', 'population': 1})
    stored = _stored(rqry.REGIONS_COLLECTION, 'NE')
    assert stored['name'] == 'New Northeast'
    assert stored['population'] == 1


def test_region_delete_removes_document():
    assert rqry.delete('NE') is True
    assert _stored(rqry.REGIONS_COLLECTION, 'NE') is None


def test_region_with_states_is_not_deleted():
    with pytest.raises(rqry.RegionHasStatesError):
        rqry.delete('SE')
    assert _stored(rqry.REGIONS_COLLECTION, 'SE') is not None
    assert _stored(sqry.STATES_COLLECTION, 'AL')['region_id'] == 'SE'
