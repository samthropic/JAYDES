"""Region HTTP contracts using real query logic and isolated storage."""
from copy import deepcopy
from unittest.mock import patch

import pytest

from server import endpoints as ep


@pytest.fixture(autouse=True)
def seeded_db():
    """Override MongoDB seeding and isolate the region cache for each test."""
    records = [{'id': 'NE', 'name': 'Northeast', 'population': 55000000,
                'description': 'Northeastern United States'}]

    def insert(collection, doc):
        assert collection == ep.rqry.REGIONS_COLLECTION
        records.append(deepcopy(doc))

    def update(collection, filters, changes):
        assert collection == ep.rqry.REGIONS_COLLECTION
        for record in records:
            if record['id'] == filters['id']:
                record.update(deepcopy(changes))

    with patch.object(ep.rqry, 'is_db_up', return_value=True), \
            patch.object(ep.rqry.dbc, 'connect_db'), \
            patch.object(ep.rqry.dbc, 'read',
                         side_effect=lambda c: deepcopy(records)), \
            patch.object(ep.rqry.dbc, 'create', side_effect=insert), \
            patch.object(ep.rqry.dbc, 'update', side_effect=update), \
            patch.dict(ep.rqry.cache._store, {}, clear=True):
        yield records


@pytest.fixture
def client():
    return ep.app.test_client()


@pytest.fixture
def new_region():
    return {'id': 'TR', 'name': 'Test Region', 'population': 0,
            'description': 'A new region'}


def test_post_region_is_readable(client, new_region):
    # Prime the cache before the write to verify subsequent reads are fresh.
    client.get('/regions/NE')
    response = client.post('/regions', json=new_region)
    assert response.status_code == 201
    assert response.get_json() == {ep.REGION_RESP: new_region}
    response = client.get('/regions/TR')
    assert response.status_code == 200
    assert response.get_json() == {ep.REGION_RESP: new_region}


def test_post_duplicate_region_preserves_original(client, new_region, seeded_db):
    new_region['id'] = 'NE'
    before = deepcopy(seeded_db)
    response = client.post('/regions', json=new_region)
    assert response.status_code == 409
    assert seeded_db == before


@pytest.mark.parametrize('field', ['id', 'name', 'population', 'description'])
def test_post_missing_required_field(client, new_region, field, seeded_db):
    del new_region[field]
    response = client.post('/regions', json=new_region)
    assert response.status_code == 400
    assert len(seeded_db) == 1


@pytest.mark.parametrize('changes', [
    {'id': '12'}, {'name': ' '}, {'population': -1},
    {'population': True}, {'description': 123},
])
def test_post_invalid_region(client, new_region, changes, seeded_db):
    response = client.post('/regions', json={**new_region, **changes})
    assert response.status_code == 400
    assert len(seeded_db) == 1


def test_get_single_region(client, seeded_db):
    response = client.get('/regions/NE')
    assert response.status_code == 200
    assert response.get_json() == {ep.REGION_RESP: seeded_db[0]}


def test_get_missing_region(client):
    assert client.get('/regions/ZZ').status_code == 404


@pytest.mark.parametrize('changes', [
    {'name': 'New Northeast'}, {'population': 0},
    {'description': 'Updated description'},
    {'name': 'Updated Region', 'population': 1, 'description': 'Updated'},
])
def test_patch_region_persists_and_preserves_other_fields(
        client, changes, seeded_db):
    original = client.get('/regions/NE').get_json()[ep.REGION_RESP]
    expected = {**original, **changes}
    response = client.patch('/regions/NE', json=changes)
    assert response.status_code == 200
    assert response.get_json() == {ep.REGION_RESP: expected}
    assert seeded_db == [expected]
    assert client.get('/regions/NE').get_json() == {ep.REGION_RESP: expected}


@pytest.mark.parametrize('changes', [
    {}, {'name': ' '}, {'population': -1}, {'population': False},
    {'description': 123}, {'id': 'XX'}, {'unknown': 'value'},
])
def test_patch_invalid_region_does_not_change_storage(
        client, changes, seeded_db):
    before = deepcopy(seeded_db)
    response = client.patch('/regions/NE', json=changes)
    assert response.status_code == 400
    assert seeded_db == before


def test_patch_missing_region(client, seeded_db):
    before = deepcopy(seeded_db)
    response = client.patch('/regions/ZZ', json={'name': 'Missing Region'})
    assert response.status_code == 404
    assert seeded_db == before


@pytest.mark.parametrize('method,path', [
    ('post', '/regions'), ('get', '/regions/NE'), ('patch', '/regions/NE'),
])
def test_region_database_unavailable(client, new_region, method, path, seeded_db):
    before = deepcopy(seeded_db)
    with patch.object(ep.rqry, 'is_db_up', return_value=False):
        if method == 'get':
            response = client.get(path)
        elif method == 'post':
            response = client.post(path, json=new_region)
        else:
            response = client.patch(path, json={'name': 'Updated'})
    assert response.status_code == 503
    assert seeded_db == before
