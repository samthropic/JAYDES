import pytest

from data.db_fixture import (
    clear_properties,
    clear_states_and_regions,
    seed_states_and_regions,
)


@pytest.fixture(autouse=True)
def seeded_db():
    """Load sample data and isolate the property collection for each test."""
    seed_states_and_regions()
    clear_properties()
    yield
    clear_properties()
    clear_states_and_regions()
