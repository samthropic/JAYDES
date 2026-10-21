from unittest.mock import patch
import pytest

import neighborhoods.query as qry
import states.query as state_qry

MOCK_NEIGHBORHOOD_DATA = {
    "73a1b2c3-d4e5-6f7a-8b9c-0123456789ab": {
        "name": "Greenwich Village",
        "state_id": "AL"    # NY
    }
}
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
def mock_update_db():
    """Provides a fresh mock database for update tests."""
    return {EXISTING_ID: {"name": "Old Name", "state_id": "NY"}}


@patch.object(qry, "NEIGHBORHOOD_TEST_DATA", MOCK_NEIGHBORHOOD_DATA)
@patch.object(state_qry, "exists", return_value=True)
def test_check_valid_neighborhood(mock_state_exists, test_nh):
    ret = qry.check_valid_neighborhood(test_nh['id'],
                                       test_nh['name'],
                                       test_nh['state_id'])
    assert ret


@patch.object(qry, "NEIGHBORHOOD_TEST_DATA", 
              {"550e8400-e29b-41d4-a716-446655440000": {}})
def test_check_valid_neighborhood_already_exists(test_nh):
    # Patching the data directly to contain our test ID forces the duplicate error
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

@patch.object(qry, "NEIGHBORHOOD_TEST_DATA", MOCK_NEIGHBORHOOD_DATA)
@patch.object(state_qry, "exists", return_value=True)
def test_check_valid_neighborhood_invalid_fields(mock_state_exists, field, value, test_nh):
    test_nh[field] = value
    
    with pytest.raises(ValueError):
        qry.check_valid_neighborhood(test_nh['id'],
                                     test_nh['name'],
                                     test_nh['state_id'])

@patch.object(qry, "NEIGHBORHOOD_TEST_DATA", MOCK_NEIGHBORHOOD_DATA)
@patch.object(state_qry, "exists", return_value=False)
def test_check_valid_neighborhood_state_not_found(mock_state_exists, test_nh):
    with pytest.raises(ValueError, match="does not exist in the database"):
        qry.check_valid_neighborhood(test_nh['id'],
                                     test_nh['name'],
                                     test_nh['state_id'])


def test_update_valid_name(mock_update_db):
    with patch.object(qry, "NEIGHBORHOOD_TEST_DATA", mock_update_db):
        updated = qry.update(EXISTING_ID, {"name": "New Name"})

        assert updated["name"] == "New Name"
        assert updated["state_id"] == "NY"
        assert mock_update_db[EXISTING_ID]["name"] == "New Name"


@patch.object(state_qry, "exists", return_value=True)
def test_update_valid_state(mock_state_exists, mock_update_db):
    with patch.object(qry, "NEIGHBORHOOD_TEST_DATA", mock_update_db):
        updated = qry.update(EXISTING_ID, {"state_id": "CA"})
        
        assert updated["name"] == "Old Name"
        assert updated["state_id"] == "CA"


def test_update_missing_id(mock_update_db):
    with patch.object(qry, "NEIGHBORHOOD_TEST_DATA", mock_update_db):
        result = qry.update("missing-id-123", {"name": "New Name"})
        assert result is None


def test_update_invalid_name(mock_update_db):
    with patch.object(qry, "NEIGHBORHOOD_TEST_DATA", mock_update_db):
        with pytest.raises(ValueError, match="non-empty string"):
            qry.update(EXISTING_ID, {"name": "   "})


def test_update_invalid_state_length(mock_update_db):
    with patch.object(qry, "NEIGHBORHOOD_TEST_DATA", mock_update_db):
        with pytest.raises(ValueError, match="letter string"):
            qry.update(EXISTING_ID, {"state_id": "Z"})


@patch.object(state_qry, "exists", return_value=False)
def test_update_state_not_found(mock_state_exists, mock_update_db):
    with patch.object(qry, "NEIGHBORHOOD_TEST_DATA", mock_update_db):
        with pytest.raises(ValueError, match="does not exist"):
            qry.update(EXISTING_ID, {"state_id": "ZZ"})


@patch.object(qry, "NEIGHBORHOOD_TEST_DATA", MOCK_NEIGHBORHOOD_DATA)
def test_query():
    neighborhoods = qry.read()
    assert isinstance(neighborhoods, list)
    assert len(neighborhoods) == 1
    
    for neighborhood in neighborhoods:
        assert isinstance(neighborhood[qry.ID], str)
        assert len(neighborhood[qry.ID]) == qry.UUID_STRING_LEN
        assert isinstance(neighborhood['name'], str)
        assert isinstance(neighborhood['state_id'], str)
        assert len(neighborhood['state_id']) == state_qry.STATE_CODE_LEN