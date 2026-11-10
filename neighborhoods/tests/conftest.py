import pytest
from data.db_fixture import clear_all, reset_all
import neighborhoods.query as qry

@pytest.fixture
def base_nh():
    """Provides the baseline neighborhood data dictionary."""
    return {
        "id": "11111111-2222-3333-4444-555555555555",
        "name": "Test Neighborhood",
        "state_id": "AL"
    }

@pytest.fixture(autouse=True)
def seeded_db():
    """Reset all collections to the sample data around each test."""
    reset_all()
    yield
    clear_all()

@pytest.fixture
def temp_nh(base_nh):
    """Inserts a valid neighborhood into the DB, and removes it after."""
    qry.delete(base_nh['id'])
    qry.create(base_nh['id'], base_nh['name'], base_nh['state_id'])

    yield base_nh.copy()
    
    qry.delete(base_nh['id'])
