import pytest
from data.db_fixture import clear_all, reset_all


@pytest.fixture(autouse=True)
def seeded_db():
    """Reset the database before each test."""
    reset_all()
    yield
    clear_all()