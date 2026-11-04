"""Required state parent contracts, isolated from MongoDB."""
from unittest.mock import patch

import pytest

import states.query as qry
from server import endpoints as ep


@pytest.fixture(autouse=True)
def seeded_db():
    """Replace database seeding with controlled query results."""
    with patch.object(qry, 'is_db_up', return_value=True), \
            patch.object(qry, 'exists', return_value=False), \
            patch.object(qry.rqry, 'exists', side_effect=lambda r: r == 'NE'), \
            patch.object(qry.dbc, 'create') as create, \
            patch.object(qry.dbc, 'update') as update:
        yield create, update


def state_payload():
    return {'id': 'TS', 'name': 'Test State', 'capital': 'Test Capital',
            'population': 0, 'area_sq_miles': 1, 'region_id': 'NE'}


INVALID_PARENTS = [None, '', ' ', '12', 'N1', 'ABC', 12, False, 'ZZ']


@pytest.mark.parametrize('region_id', INVALID_PARENTS)
def test_create_rejects_invalid_parent(region_id, seeded_db):
    create, _ = seeded_db
    with pytest.raises(ValueError):
        qry.create('TS', 0, 'Capital', 1, 'Test State', region_id)
    create.assert_not_called()


def test_create_requires_parent_when_omitted(seeded_db):
    create, _ = seeded_db
    with pytest.raises(ValueError):
        qry.create('TS', 0, 'Capital', 1, 'Test State')
    create.assert_not_called()


@pytest.mark.parametrize('region_id', INVALID_PARENTS)
def test_update_rejects_invalid_parent(region_id, seeded_db):
    _, update = seeded_db
    with patch.object(qry, 'exists', return_value=True):
        with pytest.raises(ValueError):
            qry.update('TS', {'region_id': region_id})
    update.assert_not_called()


def test_create_accepts_existing_parent(seeded_db):
    create, _ = seeded_db
    assert qry.create('TS', 0, 'Capital', 1, 'Test State', 'NE')['region_id'] == 'NE'
    assert create.call_args.args[1]['region_id'] == 'NE'


@pytest.mark.parametrize('changes', [{'capital': 'New Capital'},
                                     {'region_id': 'NE'}])
def test_update_accepts_omitted_or_existing_parent(changes, seeded_db):
    _, update = seeded_db
    stored = state_payload()
    with patch.object(qry, 'exists', return_value=True), \
            patch.object(qry, 'read_one', return_value=stored):
        assert qry.update('TS', changes)['region_id'] == 'NE'
    update.assert_called_once_with(qry.STATES_COLLECTION, {'id': 'TS'}, changes)


@pytest.mark.parametrize('region_id', INVALID_PARENTS)
def test_post_rejects_invalid_parent(region_id, seeded_db):
    create, _ = seeded_db
    payload = state_payload()
    payload['region_id'] = region_id
    response = ep.app.test_client().post('/states', json=payload)
    assert response.status_code == 400
    create.assert_not_called()


def test_post_requires_parent(seeded_db):
    create, _ = seeded_db
    payload = state_payload()
    del payload['region_id']
    assert ep.app.test_client().post('/states', json=payload).status_code == 400
    create.assert_not_called()


@pytest.mark.parametrize('region_id', INVALID_PARENTS)
def test_patch_rejects_invalid_parent(region_id, seeded_db):
    _, update = seeded_db
    with patch.object(qry, 'exists', return_value=True):
        response = ep.app.test_client().patch(
            '/states/TS', json={'region_id': region_id})
    assert response.status_code == 400
    update.assert_not_called()


def test_swagger_requires_parent_only_on_creation():
    definitions = ep.app.test_client().get('/swagger.json').get_json()['definitions']
    assert 'region_id' in definitions['StateInput']['required']
    assert 'region_id' not in definitions['StateUpdate'].get('required', [])
