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
    dbc.delete_many(pqry.PROPERTIES_COLLECTION)


def clear_neighborhoods():
    """Remove every document from the neighborhoods collection."""
    dbc.delete_many(nqry.NEIGHBORHOODS_COLLECTION)


def clear_states():
    """Remove every document from the states collection."""
    dbc.delete_many(sqry.STATES_COLLECTION)
    cache.invalidate(sqry.STATES_CACHE)


def clear_regions():
    """Remove every document from the regions collection."""
    dbc.delete_many(rqry.REGIONS_COLLECTION)
    cache.invalidate(rqry.REGIONS_CACHE)


def seed_regions():
    rqry._ensure_seeded()


def seed_states():
    sqry._ensure_seeded()


def seed_neighborhoods():
    nqry._ensure_seeded()


def seed_properties():
    pqry._ensure_seeded()


def clear_all():
    """Clear children before parents."""
    clear_properties()
    clear_neighborhoods()
    clear_states()
    clear_regions()


def seed_all():
    """Seed parents before children."""
    seed_regions()
    seed_states()
    seed_neighborhoods()
    seed_properties()


def reset_all():
    clear_all()
    seed_all()
