import pytest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from pymongo.errors import DuplicateKeyError

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
    sqry.create('TS', 1000000, 'Test Capital', 50000, 'Test State', 'NE')
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


def test_region_unique_index_rejects_direct_duplicate_insert():
    # The fixture seeds regions, which must install the index first.
    with pytest.raises(DuplicateKeyError):
        dbc.create(rqry.REGIONS_COLLECTION, {
            'id': 'NE', 'name': 'Duplicate', 'population': 0,
            'description': 'Duplicate region'})
    stored = dbc.read(rqry.REGIONS_COLLECTION)
    assert sum(region['id'] == 'NE' for region in stored) == 1


def test_concurrent_region_creates_store_only_one_record():
    barrier = Barrier(2)

    def create_region():
        barrier.wait(timeout=10)
        try:
            rqry.create('TR', 'Test Region', 0, 'Concurrent creation')
            return 'created'
        except rqry.RegionAlreadyExistsError:
            return 'duplicate'

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: create_region(), range(2)))
    assert sorted(results) == ['created', 'duplicate']
    stored = dbc.read(rqry.REGIONS_COLLECTION)
    assert sum(region['id'] == 'TR' for region in stored) == 1
