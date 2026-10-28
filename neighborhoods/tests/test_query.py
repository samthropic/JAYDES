from unittest.mock import patch
import pytest

import neighborhoods.query as qry
import states.query as state_qry

EXISTING_ID = "73a1b2c3-d4e5-6f7a-8b9c-0123456789ab"

@pytest.fixture
def test_nh():
    """Fixture providing a valid neighborhood for testing."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Test Neighborhood",
        "state_id": "AL"
    }

@pytest.fixture
def mock_db():
    """Simulates the MongoDB database using an in-memory dictionary."""
    mock_data = {
        EXISTING_ID: {"name": "Old Name", "state_id": "NY"}
    }

    def mock_read(collection):
        return [{"id": k, **v} for k, v in mock_data.items()]

    def mock_read_one(collection, filt):
        n_id = filt.get('id')
        if n_id in mock_data:
            return {"id": n_id, **mock_data[n_id]}
        return None

    def mock_create(collection, doc):
        n_id = doc.get('id')
        mock_data[n_id] = {k: v for k, v in doc.items() if k != 'id'}
        return doc

    def mock_update(collection, filters, update_dict):
        n_id = filters.get('id')
        if n_id in mock_data:
            mock_data[n_id].update(update_dict)

    def mock_delete(collection, filt):
        n_id = filt.get('id')
        if n_id in mock_data:
            del mock_data[n_id]
            return 1
        return 0

    with patch('neighborhoods.query.dbc.read', side_effect=mock_read), \
         patch('neighborhoods.query.dbc.read_one', side_effect=mock_read_one), \
         patch('neighborhoods.query.dbc.create', side_effect=mock_create), \
         patch('neighborhoods.query.dbc.update', side_effect=mock_update), \
         patch('neighborhoods.query.dbc.delete', side_effect=mock_delete), \
         patch('neighborhoods.query.dbc.is_db_up', return_value=True):
         yield mock_data


@patch.object(state_qry, "exists", return_value=True)
def test_check_valid_neighborhood(mock_state_exists, test_nh, mock_db):
    ret = qry.check_valid_neighborhood(test_nh['id'],
                                       test_nh['name'],
                                       test_nh['state_id'])
    assert ret


def test_check_valid_neighborhood_already_exists(test_nh, mock_db):
    mock_db[test_nh['id']] = {"name": "Existing", "state_id": "AL"}
    with pytest.raises(ValueError, match="already exists"):
        qry.check_valid_neighborhood(test_nh['id'],
                                     test_nh['name'],
                                     test_nh['state_id'])

@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("name", "", id="empty-name"),
        pytest.param("id", "", id="empty-id"),
        pytest.param("id", "X" * (qry.UUID_STRING_LEN - 1), id="id-too-short"),
        pytest.param("id", "X" * qry.UUID_STRING_LEN * 2, id="id-too-long"),
    ]
)

@patch.object(state_qry, "exists", return_value=True)
def test_check_valid_neighborhood_invalid_fields(mock_state_exists, field, value, test_nh, mock_db):
    test_nh[field] = value
    
    with pytest.raises(ValueError):
        qry.check_valid_neighborhood(test_nh['id'],
                                     test_nh['name'],
                                     test_nh['state_id'])

@patch.object(state_qry, "exists", return_value=False)
def test_check_valid_neighborhood_state_not_found(mock_state_exists, test_nh, mock_db):
    with pytest.raises(ValueError, match="does not exist in the database"):
        qry.check_valid_neighborhood(test_nh['id'],
                                     test_nh['name'],
                                     test_nh['state_id'])


def test_update_valid_name(mock_db):
    updated = qry.update(EXISTING_ID, {"name": "New Name"})

    assert updated["name"] == "New Name"
    assert updated["state_id"] == "NY"
    assert mock_db[EXISTING_ID]["name"] == "New Name"


@patch.object(state_qry, "exists", return_value=True)
def test_update_valid_state(mock_state_exists, mock_db):
    updated = qry.update(EXISTING_ID, {"state_id": "CA"})
    assert updated["name"] == "Old Name"
    assert updated["state_id"] == "CA"


def test_update_missing_id(mock_db):
    result = qry.update("missing-id-123", {"name": "New Name"})
    assert result is None

def test_update_invalid_name(mock_db):
    with pytest.raises(ValueError, match="non-empty string"):
        qry.update(EXISTING_ID, {"name": "   "})


def test_update_invalid_state_length(mock_db):
    with pytest.raises(ValueError, match="letter string"):
        qry.update(EXISTING_ID, {"state_id": "Z"})


@patch.object(state_qry, "exists", return_value=False)
def test_update_state_not_found(mock_state_exists, mock_db):
    with pytest.raises(ValueError, match="does not exist"):
        qry.update(EXISTING_ID, {"state_id": "ZZ"})

def test_delete_success(mock_db):
    result = qry.delete(EXISTING_ID)
    assert result is True
    assert EXISTING_ID not in mock_db


def test_delete_not_found(mock_db):
    db_length_before = len(mock_db)
    result = qry.delete("missing-id-123")
    
    assert result is False
    assert len(mock_db) == db_length_before


@patch('neighborhoods.query.dbc.is_db_up', return_value=False)
def test_delete_db_unavailable(mock_is_db_up, mock_db):
    result = qry.delete(EXISTING_ID)
    assert result is None


def test_query(mock_db):
    neighborhoods = qry.read()
    assert isinstance(neighborhoods, list)
    assert len(neighborhoods) == 1
    
    for neighborhood in neighborhoods:
        assert isinstance(neighborhood[qry.ID], str)
        assert len(neighborhood[qry.ID]) == qry.UUID_STRING_LEN
        assert isinstance(neighborhood['name'], str)
        assert isinstance(neighborhood['state_id'], str)
        assert len(neighborhood['state_id']) == state_qry.STATE_CODE_LEN