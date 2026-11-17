import data.cache as cache
import neighborhoods.query as nqry
import regions.query as rqry
import states.query as sqry

NEW_NEIGHBORHOOD_ID = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'


def _by_id(records, code):
    for record in records:
        if record['id'] == code:
            return record
    return None


def test_state_create_clears_cached_list():
    sqry.read()
    sqry.create('TS', 1000000, 'Test Capital', 50000, 'Test State', 'NE')
    states = sqry.read()
    assert _by_id(states, 'TS')['name'] == 'Test State'


def test_state_update_replaces_stale_cache():
    sqry.read()
    stale = cache.get(sqry.STATES_CACHE)
    _by_id(stale, 'AL')['capital'] = 'Stale Capital'
    cache.put(sqry.STATES_CACHE, stale)
    sqry.update('AL', {'population': 5})
    alabama = _by_id(sqry.read(), 'AL')
    assert alabama['capital'] == 'Montgomery'
    assert alabama['population'] == 5


def test_state_delete_clears_cached_list():
    sqry.create('TS', 1000000, 'Test Capital', 50000, 'Test State', 'NE')
    assert _by_id(sqry.read(), 'TS') is not None
    assert sqry.delete('TS') is True
    assert _by_id(sqry.read(), 'TS') is None


def test_region_create_clears_cached_list():
    rqry.read()
    rqry.create('TR', 'Test Region', 500000, 'A test region')
    regions = rqry.read()
    assert _by_id(regions, 'TR')['name'] == 'Test Region'


def test_region_update_replaces_stale_cache():
    rqry.read()
    stale = cache.get(rqry.REGIONS_CACHE)
    _by_id(stale, 'NE')['name'] = 'Stale Name'
    cache.put(rqry.REGIONS_CACHE, stale)
    rqry.update('NE', {'population': 1})
    northeast = _by_id(rqry.read(), 'NE')
    assert northeast['name'] == 'Northeast'
    assert northeast['population'] == 1


def test_region_delete_clears_cached_list():
    rqry.read()
    assert rqry.delete('NE') is True
    assert _by_id(rqry.read(), 'NE') is None


def test_neighborhood_create_clears_cached_list():
    nqry.read()
    nqry.create(NEW_NEIGHBORHOOD_ID, 'Cache Test', 'AL')
    neighborhoods = nqry.read()
    assert _by_id(neighborhoods, NEW_NEIGHBORHOOD_ID)['name'] == 'Cache Test'


def test_neighborhood_update_replaces_stale_cache():
    existing_id = next(iter(nqry.NEIGHBORHOOD_TEST_DATA))
    nqry.read()
    stale = cache.get(nqry.NEIGHBORHOODS_CACHE)
    _by_id(stale, existing_id)['name'] = 'Stale Name'
    cache.put(nqry.NEIGHBORHOODS_CACHE, stale)
    nqry.update(existing_id, {'name': 'Fresh Name'})
    updated = _by_id(nqry.read(), existing_id)
    assert updated['name'] == 'Fresh Name'


def test_neighborhood_delete_clears_cached_list():
    nqry.create(NEW_NEIGHBORHOOD_ID, 'Cache Test', 'AL')
    assert _by_id(nqry.read(), NEW_NEIGHBORHOOD_ID) is not None
    assert nqry.delete(NEW_NEIGHBORHOOD_ID) is True
    assert _by_id(nqry.read(), NEW_NEIGHBORHOOD_ID) is None
