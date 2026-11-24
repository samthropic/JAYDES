"""Region uniqueness setup and duplicate-insert HTTP handling."""
from unittest.mock import MagicMock, patch

import pytest
from pymongo.errors import DuplicateKeyError, OperationFailure

import data.db_connect as dbc
import regions.query as qry
from server import endpoints as ep


@pytest.fixture(autouse=True)
def seeded_db():
    """Use controlled storage and isolate cached region data."""
    with patch.dict(qry.cache._store, {}, clear=True):
        yield


def test_unique_index_uses_requested_database_and_field():
    client = MagicMock()
    with patch.object(dbc, 'client', client), patch.object(dbc, 'connect_db'):
        dbc.ensure_unique_index('regions', 'id', db='test_regions')
    client['test_regions']['regions'].create_index.assert_called_once_with(
        'id', unique=True)


def test_create_ensures_index_even_with_cached_regions():
    qry.cache.put(qry.REGIONS_CACHE, [{'id': 'NE'}])
    calls = []
    with patch.object(qry, 'is_db_up', return_value=True), \
            patch.object(dbc, 'ensure_unique_index',
                         side_effect=lambda *args: calls.append('index')), \
            patch.object(dbc, 'create',
                         side_effect=lambda *args: calls.append('insert')):
        assert qry.create('TR', 'Test Region', 0, 'Test')['id'] == 'TR'
    assert calls == ['index', 'insert']
    assert qry.cache.get(qry.REGIONS_CACHE) is None


def test_duplicate_insert_returns_conflict_and_clears_stale_cache():
    # Both preflight lookups see the old cache before another writer inserts TR.
    qry.cache.put(qry.REGIONS_CACHE, [{'id': 'NE'}])
    with patch.object(qry, 'is_db_up', return_value=True), \
            patch.object(dbc, 'ensure_unique_index'), \
            patch.object(dbc, 'create', side_effect=DuplicateKeyError('duplicate')):
        response = ep.app.test_client().post('/regions', json={
            'id': 'TR', 'name': 'Test Region', 'population': 0,
            'description': 'Test'})
    assert response.status_code == 409
    assert 'already exists' in response.get_json()['message']
    assert qry.cache.get(qry.REGIONS_CACHE) is None


def test_seed_ensures_index_for_existing_collection():
    with patch.object(dbc, 'connect_db'), \
            patch.object(dbc, 'ensure_unique_index') as index, \
            patch.object(dbc, 'read', return_value=[{'id': 'NE'}]), \
            patch.object(dbc, 'create') as insert:
        qry._ensure_seeded()
    index.assert_called_once_with('regions', 'id')
    insert.assert_not_called()


def test_concurrent_seed_duplicate_does_not_abort_remaining_seeds():
    with patch.object(dbc, 'connect_db'), \
            patch.object(dbc, 'ensure_unique_index'), \
            patch.object(dbc, 'read', return_value=[]), \
            patch.object(dbc, 'create',
                         side_effect=[DuplicateKeyError('duplicate'), None, None]) \
            as insert:
        qry._ensure_seeded()
    assert insert.call_count == len(qry.REGION_TEST_DATA)


def test_existing_duplicate_data_blocks_writes_without_removing_records():
    with patch.object(qry, 'is_db_up', return_value=True), \
            patch.object(qry, 'exists', return_value=False), \
            patch.object(dbc, 'ensure_unique_index',
                         side_effect=DuplicateKeyError('existing duplicates')), \
            patch.object(dbc, 'create') as insert:
        with pytest.raises(DuplicateKeyError):
            qry.create('TR', 'Test Region', 0, 'Test')
    insert.assert_not_called()


def test_seed_does_not_hide_other_database_errors():
    with patch.object(dbc, 'connect_db'), \
            patch.object(dbc, 'ensure_unique_index'), \
            patch.object(dbc, 'read', return_value=[]), \
            patch.object(dbc, 'create', side_effect=OperationFailure('denied')):
        with pytest.raises(OperationFailure):
            qry._ensure_seeded()
