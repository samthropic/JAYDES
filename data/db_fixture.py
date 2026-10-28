"""
Load a known set of states and regions into seDB for tests.
"""
import data.cache as cache
import data.db_connect as dbc
import regions.query as rqry
import states.query as sqry


def clear_states_and_regions():
    """Remove every document from the states and regions collections."""
    dbc.connect_db()
    dbc.delete_many(sqry.STATES_COLLECTION)
    dbc.delete_many(rqry.REGIONS_COLLECTION)
    cache.invalidate(sqry.STATES_CACHE)
    cache.invalidate(rqry.REGIONS_CACHE)


def seed_states_and_regions():
    """Clear states and regions, then insert the sample rows."""
    clear_states_and_regions()
    sqry._ensure_seeded()
    rqry._ensure_seeded()
