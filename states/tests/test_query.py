import sys

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


def test_update_bad_population():
    with pytest.raises(ValueError):
        qry.update('AL', {'population': -1})


def test_update_unknown_region():
    with pytest.raises(ValueError):
        qry.update('AL', {'region_id': 'ZZ'})


def test_delete():
    assert qry.delete('AL') is True
    assert qry.read_one('AL') is None


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

def test_create_is_readable_from_db():
    qry.create(TEST_ST['state_code'],
               TEST_ST['population'],
               TEST_ST['capital'],
               TEST_ST['area_sq_miles'],
               TEST_ST['name'])
    states = qry.read()
    ids = [state[qry.ID] for state in states]
    assert TEST_ST['state_code'] in ids