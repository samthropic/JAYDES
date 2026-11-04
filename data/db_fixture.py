"""
Load a known set of states and regions into seDB for tests.
"""
import data.cache as cache
import data.db_connect as dbc
import neighborhoods.query as nqry
import properties.query as pqry
import regions.query as rqry
import states.query as sqry


def clear_properties():
    """Remove every document from the properties collection."""
    dbc.connect_db()
    dbc.delete_many(pqry.PROPERTIES_COLLECTION)


def clear_neighborhoods():
    """Remove every document from the neighborhoods collection."""
    dbc.connect_db()
    dbc.delete_many(nqry.NEIGHBORHOODS_COLLECTION)


def clear_states_and_regions():
    """
    Remove states and regions, plus child collections that reference them.

    Neighborhoods and properties are cleared too so leftover rows from other
    packages or earlier runs cannot block state or region deletes.
    """
    dbc.connect_db()
    dbc.delete_many(pqry.PROPERTIES_COLLECTION)
    dbc.delete_many(nqry.NEIGHBORHOODS_COLLECTION)
    dbc.delete_many(sqry.STATES_COLLECTION)
    dbc.delete_many(rqry.REGIONS_COLLECTION)
    cache.invalidate(sqry.STATES_CACHE)
    cache.invalidate(rqry.REGIONS_CACHE)


def seed_states_and_regions():
    """Clear related collections, then insert sample states and regions."""
    clear_states_and_regions()
    sqry._ensure_seeded()
    rqry._ensure_seeded()
