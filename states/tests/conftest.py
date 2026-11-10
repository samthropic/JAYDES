import pytest

from data.db_fixture import clear_all, reset_all


@pytest.fixture(autouse=True)
def seeded_db():
    """Reset all collections to the sample data around each test."""
    reset_all()
    yield
    clear_all()
