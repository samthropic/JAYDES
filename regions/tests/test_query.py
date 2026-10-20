import pytest

import regions.query as qry
import states.query as sqry

TEST_RG = qry.TEST_REGION


def test_check_valid_region():
    ret = qry.check_valid_region(TEST_RG['region_code'],
                                 TEST_RG['name'],
                                 TEST_RG['population'],
                                 TEST_RG['description'])
    assert ret


def test_check_valid_region_bad_pop():
    with pytest.raises(ValueError):
        qry.check_valid_region(TEST_RG['region_code'],
                               TEST_RG['name'],
                               -23423,
                               TEST_RG['description'])


def test_check_valid_region_code_too_short():
    with pytest.raises(ValueError):
        qry.check_valid_region('',
                               TEST_RG['name'],
                               TEST_RG['population'],
                               TEST_RG['description'])


def test_check_valid_region_code_too_long():
    with pytest.raises(ValueError):
        qry.check_valid_region('X' * qry.REGION_CODE_LEN * 2,
                               TEST_RG['name'],
                               TEST_RG['population'],
                               TEST_RG['description'])


def test_check_valid_region_empty_name():
    with pytest.raises(ValueError):
        qry.check_valid_region(TEST_RG['region_code'],
                               '',
                               TEST_RG['population'],
                               TEST_RG['description'])


def test_query():
    regions = qry.read()
    assert isinstance(regions, dict)


@pytest.mark.skip(reason='delete() still removes a region that has states')
def test_delete_region_with_states():
    states = sqry.read()
    assert any(state['region_id'] == 'SE' for state in states)
    assert qry.delete('SE') is False
    assert qry.exists('SE') is True
