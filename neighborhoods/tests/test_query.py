from unittest.mock import patch
import pytest

import neighborhoods.query as qry
import states.query as state_qry

EXISTING_ID = "73a1b2c3-d4e5-6f7a-8b9c-0123456789ab"

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


def test_update_valid_name(temp_nh):
    updated = qry.update(temp_nh['id'], {"name": "New Name"})
    
    assert updated["name"] == "New Name"
    assert updated["state_id"] == "AL"
    
    # Verify the change actually persisted to the local MongoDB
    db_nh = qry.read(temp_nh['id'])
    assert db_nh["name"] == "New Name"

def test_update_valid_state(temp_nh):
    updated = qry.update(temp_nh['id'], {"state_id": "AK"})
    assert updated["name"] == temp_nh['name']
    assert updated["state_id"] == "AK"


def test_update_missing_id():
    result = qry.update("missing-id-123", {"name": "New Name"})
    assert result is None

def test_update_invalid_name(temp_nh):
    with pytest.raises(ValueError, match="non-empty string"):
        qry.update(temp_nh['id'], {"name": "   "})


def test_update_invalid_state_length(temp_nh):
    with pytest.raises(ValueError, match="letter string"):
        qry.update(temp_nh['id'], {"state_id": "Z"})


def test_update_state_not_found(temp_nh):
    with pytest.raises(ValueError, match="does not exist"):
        qry.update(temp_nh['id'], {"state_id": "ZZ"})


def test_delete_success(temp_nh):
    result = qry.delete(temp_nh['id'])
    assert result is True
    assert qry.read(temp_nh['id']) is None


def test_delete_not_found():
    result = qry.delete("missing-id-123")
    assert result is False


@patch('neighborhoods.query.dbc.is_db_up', return_value=False)
def test_delete_db_unavailable(mock_is_db_up, temp_nh):
    result = qry.delete(temp_nh['id'])
    assert result is None


def test_query(temp_nh):
    neighborhoods = qry.read()
    assert isinstance(neighborhoods, list)

    ids = [n[qry.ID] for n in neighborhoods]
    assert temp_nh['id'] in ids
    
    for neighborhood in neighborhoods:
        assert isinstance(neighborhood[qry.ID], str)
        assert len(neighborhood[qry.ID]) == qry.UUID_STRING_LEN
        assert isinstance(neighborhood['name'], str)
        assert isinstance(neighborhood['state_id'], str)
        assert len(neighborhood['state_id']) == state_qry.STATE_CODE_LEN