import pytest

import neighborhoods.query as qry
from states.query import STATE_CODE_LEN

TEST_NH = qry.TEST_NEIGHBORHOOD

def test_check_valid_neighborhood():
    ret = qry.check_valid_neighborhood(TEST_NH['id'],
                                       TEST_NH['name'],
                                       TEST_NH['state_id'])
    assert ret


def test_check_valid_neighborhood_bad_name():
    with pytest.raises(ValueError):
        ret = qry.check_valid_neighborhood(TEST_NH['id'],
                                           '',
                                           TEST_NH['state_id'])


def test_check_valid_neighborhood_id_too_short():
    with pytest.raises(ValueError):
        ret = qry.check_valid_neighborhood('',
                                           TEST_NH['name'],
                                           TEST_NH['state_id'])


def test_check_valid_neighborhood_id_too_long():
    with pytest.raises(ValueError):
        ret = qry.check_valid_neighborhood('X' * qry.UUID_STRING_LEN * 2,
                                           TEST_NH['name'],
                                           TEST_NH['state_id'])

def test_check_valid_neighborhood_state_not_found():
    with pytest.raises(ValueError):
        ret = qry.check_valid_neighborhood(TEST_NH['id'],
                                           TEST_NH['name'],
                                           'ZZ')


def test_check_valid_neighborhood_already_exists():
    # Grab an ID that is already in the mock database
    existing_id = list(qry.NEIGHBORHOOD_TEST_DATA.keys())[0]
    with pytest.raises(ValueError):
        ret = qry.check_valid_neighborhood(existing_id,
                                           TEST_NH['name'],
                                           TEST_NH['state_id'])


def test_query():
    neighborhoods = qry.read()
    assert isinstance(neighborhoods, list)
    for neighborhood in neighborhoods:
        assert isinstance(neighborhood[qry.ID], str)
        assert len(neighborhood[qry.ID]) == qry.UUID_STRING_LEN
        assert isinstance(neighborhood['name'], str)
        assert isinstance(neighborhood['state_id'], str)
        assert len(neighborhood['state_id']) == STATE_CODE_LEN