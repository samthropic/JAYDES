"""Region input validation without a MongoDB connection."""
from unittest.mock import patch

import pytest

import regions.query as qry
from server import endpoints as ep


@pytest.fixture(autouse=True)
def seeded_db():
    """Use mocked persistence instead of the package's database fixture."""
    with patch.object(qry, 'is_db_up', return_value=True), \
            patch.object(qry, 'exists', return_value=False), \
            patch.object(qry.dbc, 'create') as create, \
            patch.object(qry.dbc, 'update') as update:
        yield create, update


INVALID_CHANGES = [
    {'name': ''}, {'name': '   '}, {'name': '\t\n'},
    {'population': True}, {'population': False},
]
INVALID_CODES = ['12', 'N1', 'N-', ' N', 'éN', '', 'ABC', None, 12]


@pytest.mark.parametrize('code', INVALID_CODES)
def test_create_rejects_nonletter_codes(code, seeded_db):
    create, _ = seeded_db
    with pytest.raises(ValueError, match='letter string'):
        qry.create(code, 'Test Region', 0, None)
    create.assert_not_called()


@pytest.mark.parametrize('changes', INVALID_CHANGES)
def test_create_rejects_blank_names_and_booleans(changes, seeded_db):
    create, _ = seeded_db
    payload = {'name': 'Test Region', 'population': 0, **changes}
    with pytest.raises(ValueError):
        qry.create('TR', description=None, **payload)
    create.assert_not_called()


@pytest.mark.parametrize('changes', INVALID_CHANGES)
def test_update_rejects_blank_names_and_booleans(changes, seeded_db):
    _, update = seeded_db
    with patch.object(qry, 'exists', return_value=True):
        with pytest.raises(ValueError):
            qry.update('TR', changes)
    update.assert_not_called()


@pytest.mark.parametrize('code', ['TR', 'tr'])
@pytest.mark.parametrize('population', [0, 1])
def test_valid_letters_names_and_populations(code, population):
    assert qry.check_valid_region(code, ' Test Region ', population, None)


@pytest.mark.parametrize('changes', INVALID_CHANGES)
def test_post_rejects_invalid_region_values(changes, seeded_db):
    create, _ = seeded_db
    payload = {'id': 'TR', 'name': 'Test Region', 'population': 0,
               'description': 'Test', **changes}
    response = ep.app.test_client().post('/regions', json=payload)
    assert response.status_code == 400
    create.assert_not_called()


@pytest.mark.parametrize('code', ['12', 'N1', 'N-', 'éN'])
def test_post_rejects_nonletter_codes(code, seeded_db):
    create, _ = seeded_db
    response = ep.app.test_client().post('/regions', json={
        'id': code, 'name': 'Test Region', 'population': 0,
        'description': 'Test'})
    assert response.status_code == 400
    create.assert_not_called()


@pytest.mark.parametrize('changes', INVALID_CHANGES)
def test_patch_rejects_invalid_region_values(changes, seeded_db):
    _, update = seeded_db
    with patch.object(qry, 'exists', return_value=True):
        response = ep.app.test_client().patch('/regions/TR', json=changes)
    assert response.status_code == 400
    update.assert_not_called()
