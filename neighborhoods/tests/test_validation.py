import pytest

import neighborhoods.query as qry


def test_check_valid_neighborhood(base_nh):
    ret = qry.check_valid_neighborhood(base_nh['id'],
                                       base_nh['name'],
                                       base_nh['state_id'])
    assert ret


def test_check_valid_neighborhood_already_exists(temp_nh):
    with pytest.raises(ValueError, match="already exists"):
        qry.check_valid_neighborhood(temp_nh['id'],
                                     temp_nh['name'],
                                     temp_nh['state_id'])


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("name", "", id="empty-name"),
        pytest.param("id", "", id="empty-id"),
        pytest.param("id", "X" * (qry.UUID_STRING_LEN - 1), id="id-too-short"),
        pytest.param("id", "X" * qry.UUID_STRING_LEN * 2, id="id-too-long"),
    ]
)
def test_check_valid_neighborhood_invalid_fields(field, value, base_nh):
    test_data = base_nh.copy()
    test_data[field] = value

    with pytest.raises(ValueError):
        qry.check_valid_neighborhood(test_data['id'],
                                     test_data['name'],
                                     test_data['state_id'])


def test_check_valid_neighborhood_state_not_found(base_nh):
    with pytest.raises(ValueError, match="does not exist in the database"):
        qry.check_valid_neighborhood(base_nh['id'],
                                     base_nh['name'],
                                     "ZZ")


def test_update_invalid_name(temp_nh):
    with pytest.raises(ValueError, match="non-empty string"):
        qry.update(temp_nh['id'], {"name": "   "})


def test_update_invalid_state_length(temp_nh):
    with pytest.raises(ValueError, match="letter string"):
        qry.update(temp_nh['id'], {"state_id": "Z"})


def test_update_state_not_found(temp_nh):
    with pytest.raises(ValueError, match="does not exist"):
        qry.update(temp_nh['id'], {"state_id": "ZZ"})