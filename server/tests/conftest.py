import pytest

from data.db_fixture import clear_states_and_regions, seed_states_and_regions


@pytest.fixture(autouse=True)
def seeded_db():
    """Load sample states and regions, then remove them."""
    seed_states_and_regions()
    yield
    clear_states_and_regions()
