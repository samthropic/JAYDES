from unittest.mock import patch
import neighborhoods.query as qry
import states.query as state_qry


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