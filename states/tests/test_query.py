import sys
from unittest.mock import patch

import pytest

import states.query as qry

TEST_ST = qry.TEST_STATE


def test_check_valid_state():
    ret = qry.check_valid_state(TEST_ST['state_code'],
                                TEST_ST['population'],
                                TEST_ST['capital'],
                                TEST_ST['area_sq_miles'],
                                TEST_ST['name'],
                                TEST_ST['region_id'])
    assert ret


def test_check_valid_state_bad_pop():
    with pytest.raises(ValueError):
        qry.check_valid_state(TEST_ST['state_code'],
                              -23423,
                              TEST_ST['capital'],
                              TEST_ST['area_sq_miles'],
                              TEST_ST['name'],
                              TEST_ST['region_id'])


@pytest.mark.parametrize('population', [True, False])
def test_check_valid_state_rejects_boolean_population(population):
    with pytest.raises(ValueError, match='non-negative integer'):
        qry.check_valid_state(TEST_ST['state_code'],
                              population,
                              TEST_ST['capital'],
                              TEST_ST['area_sq_miles'],
                              TEST_ST['name'],
                              TEST_ST['region_id'])


def test_check_valid_state_bad_region_id():
    with pytest.raises(ValueError):
        qry.check_valid_state(TEST_ST['state_code'],
                              TEST_ST['population'],
                              TEST_ST['capital'],
                              TEST_ST['area_sq_miles'],
                              TEST_ST['name'],
                              'ZZ')


def test_check_valid_state_code_too_short():
    with pytest.raises(ValueError):
        qry.check_valid_state('',
                              TEST_ST['population'],
                              TEST_ST['capital'],
                              TEST_ST['area_sq_miles'],
                              TEST_ST['name'],
                              TEST_ST['region_id'])


def test_check_valid_state_code_too_long():
    with pytest.raises(ValueError):
        qry.check_valid_state('X' * qry.STATE_CODE_LEN * 2,
                              TEST_ST['population'],
                              TEST_ST['capital'],
                              TEST_ST['area_sq_miles'],
                              TEST_ST['name'],
                              TEST_ST['region_id'])


@pytest.mark.skipif(sys.version_info < (3, 9),
                    reason='The project requires Python 3.9 or newer.')
def test_create_unknown_region():
    with pytest.raises(ValueError, match='does not exist'):
        qry.create(TEST_ST['state_code'],
                   TEST_ST['population'],
                   TEST_ST['capital'],
                   TEST_ST['area_sq_miles'],
                   TEST_ST['name'],
                   'ZZ')


def test_read_one():
    state = qry.read_one('AL')
    assert state['id'] == 'AL'
    assert state['name'] == 'Alabama'
    assert state['latitude'] == 32.318231
    assert state['longitude'] == -86.902298
    assert qry.dbc.MONGO_ID not in state


def test_read_one_not_found():
    assert qry.read_one('ZZ') is None


def test_update():
    state = qry.update('AL', {'capital': 'Birmingham', 'population': 5})
    assert state['capital'] == 'Birmingham'
    assert state['population'] == 5
    assert qry.read_one('AL')['capital'] == 'Birmingham'


def test_update_not_found():
    assert qry.update('ZZ', {'capital': 'Nowhere'}) is None


def test_update_unknown_field():
    with pytest.raises(ValueError):
        qry.update('AL', {'flag': 'red'})


@pytest.mark.parametrize('population', [-1, True, False])
def test_update_bad_population(population):
    with pytest.raises(ValueError):
        qry.update('AL', {'population': population})


def test_update_unknown_region():
    with pytest.raises(ValueError):
        qry.update('AL', {'region_id': 'ZZ'})


def test_update_coordinates():
    state = qry.update('AL', {'latitude': 33.5, 'longitude': -86.8})
    assert state['latitude'] == 33.5
    assert state['longitude'] == -86.8
    assert qry.read_one('AL')['latitude'] == 33.5


def test_update_bad_latitude():
    with pytest.raises(ValueError, match='Latitude'):
        qry.update('AL', {'latitude': 100})


def test_seed_data_has_csv_coordinates():
    assert qry.STATE_TEST_DATA['AL']['latitude'] == 32.318231
    assert qry.STATE_TEST_DATA['AK']['longitude'] == -154.493062


@pytest.fixture
def neighborhood_in_al():
    """A neighborhood that references state AL, removed after the test."""
    doc = {'id': 'test-neighborhood', 'name': 'Test', 'state_id': 'AL'}
    qry.dbc.create(qry.NEIGHBORHOODS_COLLECTION, dict(doc))
    yield doc
    qry.dbc.delete(qry.NEIGHBORHOODS_COLLECTION, {'id': doc['id']})


def test_delete():
    qry.create(TEST_ST['state_code'],
               TEST_ST['population'],
               TEST_ST['capital'],
               TEST_ST['area_sq_miles'],
               TEST_ST['name'], TEST_ST['region_id'])
    assert qry.delete(TEST_ST['state_code']) is True
    assert qry.read_one(TEST_ST['state_code']) is None


def test_delete_state_with_neighborhoods(neighborhood_in_al):
    with pytest.raises(qry.StateHasNeighborhoodsError):
        qry.delete('AL')
    assert qry.read_one('AL') is not None


def test_delete_not_found():
    assert qry.delete('ZZ') is False


def test_query():
    states = qry.read()
    assert isinstance(states, list)
    for state in states:
        assert isinstance(state[qry.ID], str)
        assert len(state[qry.ID]) == qry.STATE_CODE_LEN
        assert 'region_id' in state
        assert isinstance(state['region_id'], str)
        assert len(state['region_id']) == qry.STATE_CODE_LEN
        assert 'latitude' in state
        assert 'longitude' in state
        assert -90 <= state['latitude'] <= 90
        assert -180 <= state['longitude'] <= 180


def test_create_is_readable_from_db():
    qry.create(TEST_ST['state_code'],
               TEST_ST['population'],
               TEST_ST['capital'],
               TEST_ST['area_sq_miles'],
               TEST_ST['name'], TEST_ST['region_id'])
    states = qry.read()
    ids = [state[qry.ID] for state in states]
    assert TEST_ST['state_code'] in ids


DB_DOWN_CALLS = [
    ('read', ()),
    ('read_one', ('AL',)),
    ('exists', ('AL',)),
    ('update', ('AL', {'capital': 'Birmingham'})),
    ('delete', ('AL',)),
]


@pytest.mark.parametrize('func_name, args', DB_DOWN_CALLS)
def test_db_down_returns_none(func_name, args):
    with patch('states.query.is_db_up', return_value=False, autospec=True):
        assert getattr(qry, func_name)(*args) is None


def test_create_db_down_returns_none():
    with patch('states.query.is_db_up', return_value=False, autospec=True):
        assert qry.create(TEST_ST['state_code'],
                          TEST_ST['population'],
                          TEST_ST['capital'],
                          TEST_ST['area_sq_miles'],
                          TEST_ST['name'],
                          TEST_ST['region_id']) is None
    assert qry.read_one(TEST_ST['state_code']) is None


def test_check_valid_state_already_exists():
    with pytest.raises(ValueError, match='already exists'):
        qry.check_valid_state('AL',
                              TEST_ST['population'],
                              TEST_ST['capital'],
                              TEST_ST['area_sq_miles'],
                              TEST_ST['name'],
                              TEST_ST['region_id'])


def test_update_with_no_changes_leaves_state_unchanged():
    before = qry.read_one('AL')
    with patch.object(qry.dbc, 'update', autospec=True) as mock_update:
        assert qry.update('AL', {}) == before
    mock_update.assert_not_called()


def test_read_is_served_from_cache_after_first_call():
    first = qry.read()
    with patch.object(qry.dbc, 'read',
                      side_effect=AssertionError('read hit the database')):
        assert qry.read() == first


def test_read_returns_a_copy_of_the_cache():
    qry.read()[0]['name'] = 'Changed'
    assert qry.read()[0]['name'] != 'Changed'


@pytest.mark.parametrize('changes', [
    {'name': ''},
    {'name': '   '},
    {'capital': ''},
    {'capital': None},
])
def test_update_rejects_empty_text(changes):
    before = qry.read_one('AL')
    with pytest.raises(ValueError, match='non-empty string'):
        qry.update('AL', changes)
    assert qry.read_one('AL') == before


@pytest.mark.parametrize('name, capital', [('', 'C'), ('N', '   ')])
def test_create_rejects_empty_text(name, capital):
    with pytest.raises(ValueError, match='non-empty string'):
        qry.create(TEST_ST['state_code'],
                   TEST_ST['population'],
                   capital,
                   TEST_ST['area_sq_miles'],
                   name,
                   TEST_ST['region_id'])
    assert qry.read_one(TEST_ST['state_code']) is None


@pytest.mark.parametrize('area', [0, -5, None, True, float('nan')])
def test_update_rejects_bad_area(area):
    before = qry.read_one('AL')
    with pytest.raises(ValueError, match='Area'):
        qry.update('AL', {'area_sq_miles': area})
    assert qry.read_one('AL') == before


def test_create_rejects_bad_area():
    with pytest.raises(ValueError, match='Area'):
        qry.create(TEST_ST['state_code'],
                   TEST_ST['population'],
                   TEST_ST['capital'],
                   -1,
                   TEST_ST['name'],
                   TEST_ST['region_id'])
    assert qry.read_one(TEST_ST['state_code']) is None
