from http import HTTPStatus

from flask import Flask, request
from flask_restx import Resource, Api, fields  # Namespace
from flask_cors import CORS

import data.db_connect as dbc
import properties.query as pqry
import neighborhoods.query as nqry
import regions.query as rqry

import werkzeug.exceptions as wz

import states.query as sqry

app = Flask(__name__)
CORS(app)
api = Api(app)

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
HEALTH_EP = '/health'
HEALTH_STATUS = 'status'
HEALTH_DATABASE = 'database'
STATES_EP = '/states'
STATES_RESP = 'States:'
STATE_RESP = 'State:'
MESSAGE = 'Message'
REGIONS_EP = '/regions'
REGIONS_RESP = 'Regions:'
REGION_RESP = 'Region:'
PROPERTIES_EP = '/properties'
PROPERTIES_RESP = 'Properties:'
PROPERTY_RESP = 'Property:'
NEIGHBORHOODS_EP = '/neighborhoods'
NEIGHBORHOODS_RESP = 'Neighborhoods:'

state_model = api.model('State', {
    sqry.ID: fields.String(description='Two-letter state code', example='NY'),
    'name': fields.String(description='State name', example='New York'),
    'capital': fields.String(description='State capital', example='Albany'),
    'population': fields.Integer(description='Population'),
    'area_sq_miles': fields.Float(description='Area in square miles'),
    'region_id': fields.String(description='Id of the parent region',
                               example='NE'),
})

region_states_model = api.model('RegionStates', {
    STATES_RESP: fields.List(fields.Nested(state_model)),
})

state_input_model = api.model('StateInput', {
    sqry.ID: fields.String(required=True, example='NY',
                           description='Two-letter state code'),
    'name': fields.String(required=True, example='New York'),
    'capital': fields.String(required=True, example='Albany'),
    'population': fields.Integer(required=True),
    'area_sq_miles': fields.Float(required=True),
    'region_id': fields.String(required=True,
                               description='Id of an existing region',
                               example='NE'),
})

region_model = api.model('Region', {
    rqry.ID: fields.String(description='Two-letter region code', example='NE'),
    'name': fields.String(description='Region name', example='Northeast'),
    'population': fields.Integer(description='Population'),
    'description': fields.String(description='Region description',
                                 example='Northeastern United States'),
})

region_input_model = api.model('RegionInput', {
    rqry.ID: fields.String(required=True, example='NE',
                           description='Two-letter region code'),
    'name': fields.String(required=True, example='Northeast'),
    'population': fields.Integer(required=True),
    'description': fields.String(required=True,
                                 example='Northeastern United States'),
})

region_update_model = api.model('RegionUpdate', {
    'name': fields.String(description='Region name', example='Midwest'),
    'population': fields.Integer(description='Population'),
    'description': fields.String(description='Region description'),
})

neighborhood_model = api.model('Neighborhood', {
    nqry.ID: fields.String(description='Neighborhood UUID'),
    'name': fields.String(description='Neighborhood name',
                          example='Greenwich Village'),
    'state_id': fields.String(description='Two-letter state code',
                              example='NY'),
})

states_model = api.model('States', {
    STATES_RESP: fields.List(fields.Nested(state_model)),
})

state_response_model = api.model('StateResponse', {
    STATE_RESP: fields.Nested(state_model),
})

state_neighborhoods_model = api.model('StateNeighborhoods', {
    NEIGHBORHOODS_RESP: fields.List(fields.Nested(neighborhood_model)),
})

neighborhood_input_model = api.model('NeighborhoodInput', {
    nqry.ID: fields.String(required=True, description='Neighborhood UUID',
                           example='550e8400-e29b-41d4-a716-446655440000'),
    'name': fields.String(description='Neighborhood name',
                          example='Greenwich Village'),
    'state_id': fields.String(required=True,
                              description='Two-letter state code',
                              example='NY'),
})

neighborhood_update_model = api.model('NeighborhoodUpdate', {
    'name': fields.String(description='Neighborhood name',
                          example='West Village'),
    'state_id': fields.String(description='Two-letter state code',
                              example='NY'),
})

state_update_model = api.model('StateUpdate', {
    'name': fields.String(example='New York'),
    'capital': fields.String(example='Albany'),
    'population': fields.Integer(),
    'area_sq_miles': fields.Float(),
    'region_id': fields.String(description='Id of an existing region',
                               example='NE'),
})

property_model = api.model('Property', {
    'id': fields.String(required=True, description='Property id'),
    'address': fields.String(required=True, description='Property address',
                             example='125 Perry Street, New York, NY'),
    'neighborhood_id': fields.String(required=True,
                                     description='Neighborhood id'),
    'price': fields.Float(required=True, description='Price'),
    'bedrooms': fields.Integer(required=True, description='Bedroom count'),
    'bathrooms': fields.Float(required=True, description='Bathroom count'),
    'latitude': fields.Float(required=True, description='Latitude'),
    'longitude': fields.Float(required=True, description='Longitude'),
})

property_update_model = api.model('PropertyUpdate', {
    'address': fields.String(description='Property address'),
    'neighborhood_id': fields.String(description='Neighborhood id'),
    'price': fields.Float(description='Price'),
    'bedrooms': fields.Integer(description='Bedroom count'),
    'bathrooms': fields.Float(description='Bathroom count'),
    'latitude': fields.Float(description='Latitude'),
    'longitude': fields.Float(description='Longitude'),
})

health_model = api.model('Health', {
    HEALTH_STATUS: fields.String(description='API status', example='ok'),
    HEALTH_DATABASE: fields.String(description='MongoDB status',
                                   example='up'),
})


@api.route(HELLO_EP)
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        """
        return {HELLO_RESP: 'world'}


@api.route(HEALTH_EP)
class Health(Resource):
    """
    Report whether the API process is up and whether MongoDB answers a ping.
    """
    @api.response(HTTPStatus.OK.value, 'API and database are up', health_model)
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Database is down')
    def get(self):
        """
        Return health status. HTTP 503 when MongoDB does not accept a ping.
        """
        if not dbc.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')
        return {HEALTH_STATUS: 'ok', HEALTH_DATABASE: 'up'}


@api.route(ENDPOINT_EP)
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a sorted list of available endpoints.
        """
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


@api.route(STATES_EP)
class States(Resource):
    """
    The get method will return a list of all states in the database.
    """
    @api.response(HTTPStatus.OK.value, 'Success', states_model)
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self):
        """
        The get method will return a list of all states in the database.
        """
        states = sqry.read()
        if states is None:
            raise wz.ServiceUnavailable('Database may be down.')
        return {STATES_RESP: states}

    @api.expect(state_input_model, validate=True)
    @api.response(HTTPStatus.CREATED.value, 'Created', state_response_model)
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Invalid state data')
    @api.response(HTTPStatus.CONFLICT.value, 'State already exists')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def post(self):
        """
        The post method will create a new state.
        """
        data = api.payload
        if not sqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')
        if sqry.exists(data[sqry.ID]):
            raise wz.Conflict(f'State {data[sqry.ID]} already exists.')

        try:
            state = sqry.create(
                data[sqry.ID],
                data['population'],
                data['capital'],
                data['area_sq_miles'],
                data['name'],
                data['region_id'],
            )
        except ValueError as err:
            raise wz.BadRequest(str(err))
        created = {sqry.ID: data[sqry.ID], **state}
        return {STATE_RESP: created}, HTTPStatus.CREATED


@api.route(f'{STATES_EP}/<state_id>')
class State(Resource):
    """
    The get method will return a single state by id.
    """
    @api.response(HTTPStatus.OK.value, 'Success', state_response_model)
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self, state_id):
        """
        The get method will return a single state by its two-letter code.
        """
        if not sqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')

        state = sqry.read_one(state_id)
        if state is None:
            raise wz.NotFound(f'State {state_id} not found.')
        return {STATE_RESP: state}

    @api.expect(state_update_model, validate=True)
    @api.response(HTTPStatus.OK.value, 'Updated', state_response_model)
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Invalid state data')
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def patch(self, state_id):
        """
        The patch method will update one or more fields of a state.
        """
        if not sqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')

        changes = api.payload or {}
        if not changes:
            raise wz.BadRequest('At least one state field is required.')

        try:
            state = sqry.update(state_id, changes)
        except ValueError as err:
            raise wz.BadRequest(str(err))

        if state is None:
            raise wz.NotFound(f'State {state_id} not found.')
        return {STATE_RESP: state}

    @api.response(HTTPStatus.NO_CONTENT.value, 'Deleted')
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.CONFLICT.value, 'State still has neighborhoods')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def delete(self, state_id):
        """
        The delete method will delete a state only when no neighborhoods
        reference it.
        """
        if not sqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')

        try:
            deleted = sqry.delete(state_id)
        except sqry.StateHasNeighborhoodsError as err:
            raise wz.Conflict(str(err))
        if not deleted:
            raise wz.NotFound(f'State {state_id} not found.')
        return '', HTTPStatus.NO_CONTENT


@api.route(f'{STATES_EP}/<state_id>/neighborhoods')
class StateNeighborhoods(Resource):
    """
    The get method will return all neighborhoods in a state.
    """
    @api.response(HTTPStatus.OK.value, 'Success', state_neighborhoods_model)
    @api.response(HTTPStatus.NOT_FOUND.value, 'State Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self, state_id):
        """
        The get method will return all neighborhoods in a state.
        """
        if not sqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')

        if not sqry.exists(state_id):
            raise wz.NotFound(f'State {state_id} not found.')

        neighborhoods = nqry.read()
        if neighborhoods is None:
            raise wz.ServiceUnavailable('Database may be down.')
        in_state = [n for n in neighborhoods if n['state_id'] == state_id]
        return {NEIGHBORHOODS_RESP: in_state}


@api.route(REGIONS_EP)
class Regions(Resource):
    """
    The get method will return a list of all regions in the database.
    """
    @api.response(HTTPStatus.OK.value, 'Success', [region_model])
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self):
        """
        The get method will return a list of all regions in the database.
        """
        regions = rqry.read()
        if regions is None:
            raise wz.ServiceUnavailable('Database may be down.')
        return {REGIONS_RESP: regions}

    @api.expect(region_input_model, validate=True)
    @api.response(HTTPStatus.CREATED.value, 'Created', region_model)
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Invalid region data')
    @api.response(HTTPStatus.CONFLICT.value, 'Region already exists')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def post(self):
        """Create a region."""
        data = api.payload
        if not rqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')
        if rqry.exists(data[rqry.ID]):
            raise wz.Conflict(f'Region {data[rqry.ID]} already exists.')

        try:
            region = rqry.create(
                data[rqry.ID],
                data['name'],
                data['population'],
                data.get('description'),
            )
        except ValueError as err:
            raise wz.BadRequest(str(err))

        created = {rqry.ID: data[rqry.ID], **region}
        return {REGION_RESP: created}, HTTPStatus.CREATED


@api.route(f'{REGIONS_EP}/<region_id>')
class Region(Resource):
    """Get, update, or delete a single region."""
    @api.response(HTTPStatus.OK.value, 'Success', region_model)
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self, region_id):
        """Return a single region by id."""
        if not rqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')

        region = rqry.read_one(region_id)
        if region is None:
            raise wz.NotFound(f'Region {region_id} not found.')
        return {REGION_RESP: region}

    @api.expect(region_update_model, validate=True)
    @api.response(HTTPStatus.OK.value, 'Updated', region_model)
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Invalid region data')
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def patch(self, region_id):
        """Update one or more fields on a region."""
        if not rqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')

        changes = api.payload or {}
        if not changes:
            raise wz.BadRequest('At least one region field is required.')

        try:
            region = rqry.update(region_id, changes)
        except ValueError as err:
            raise wz.BadRequest(str(err))

        if region is None:
            raise wz.NotFound(f'Region {region_id} not found.')

        return {REGION_RESP: region}

    @api.response(HTTPStatus.NO_CONTENT.value, 'Deleted')
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    @api.response(HTTPStatus.CONFLICT.value, 'Region still has states')
    def delete(self, region_id):
        """Delete a region only when no states reference it."""
        if not rqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')

        try:
            deleted = rqry.delete(region_id)
        except rqry.RegionHasStatesError as err:
            raise wz.Conflict(str(err))
        if not deleted:
            raise wz.NotFound(f'Region {region_id} not found.')
        return '', HTTPStatus.NO_CONTENT


@api.route(f'{REGIONS_EP}/<region_id>/states')
class RegionStates(Resource):
    """States belonging to an existing region."""

    @api.response(HTTPStatus.OK.value, 'Success', region_states_model)
    @api.response(HTTPStatus.NOT_FOUND.value, 'Region Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self, region_id):
        """List states in a region; an empty region returns an empty list."""
        region_exists = rqry.exists(region_id)
        if region_exists is None:
            raise wz.ServiceUnavailable('Database may be down.')
        if not region_exists:
            raise wz.NotFound(f'Region {region_id} not found.')

        states = sqry.read()
        if states is None:
            raise wz.ServiceUnavailable('Database may be down.')
        return {STATES_RESP: [state for state in states
                              if state.get('region_id') == region_id]}


@api.route(NEIGHBORHOODS_EP)
class Neighborhoods(Resource):
    """
    The get method will return a list of all neighborhoods in the database.
    """
    @api.response(HTTPStatus.OK.value, 'Success', [neighborhood_model])
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self):
        """
        The get method will return a list of all neighborhoods in the database.
        """
        neighborhoods = nqry.read()
        if neighborhoods is None:
            raise wz.ServiceUnavailable('Database may be down.')
        return {NEIGHBORHOODS_RESP: neighborhoods}

    @api.expect(neighborhood_input_model, validate=True)
    @api.response(HTTPStatus.CREATED.value, 'Created', neighborhood_model)
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Invalid neighborhood data')
    @api.response(HTTPStatus.CONFLICT.value, 'Neighborhood already exists')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def post(self):
        """
        The post method will create a new neighborhood.
        """
        data = api.payload
        neighborhood_id = data[nqry.ID]
        exists_status = nqry.exists(neighborhood_id)
        if exists_status is None:
            raise wz.ServiceUnavailable('Database may be down.')
        if exists_status:
            raise wz.Conflict(
                f'Neighborhood {neighborhood_id} already exists.'
            )

        state_id = data['state_id']
        name = data.get('name', 'Unnamed Neighborhood')

        try:
            neighborhood = nqry.create(
                neighborhood_id,
                name,
                state_id
            )
        except ValueError as err:
            raise wz.BadRequest(str(err))

        return {'Neighborhood': neighborhood}, HTTPStatus.CREATED


@api.route(f'{NEIGHBORHOODS_EP}/<neighborhood_id>')
class Neighborhood(Resource):
    """
    The get method will return a single neighborhood by id.
    """
    @api.response(HTTPStatus.OK.value, 'Success', neighborhood_model)
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self, neighborhood_id):
        """
        The get method will return a single neighborhood by id.
        """
        neighborhood = nqry.read(neighborhood_id)
        if neighborhood is None:
            if not nqry.dbc.is_db_up():
                raise wz.ServiceUnavailable('Database may be down.')
            raise wz.NotFound(f'Neighborhood {neighborhood_id} not found.')
        return neighborhood

    @api.expect(neighborhood_update_model, validate=True)
    @api.response(HTTPStatus.OK.value, 'Updated', neighborhood_model)
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Invalid neighborhood data')
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def patch(self, neighborhood_id):
        """Update one or more fields on a neighborhood."""
        changes = api.payload or {}
        if not changes:
            raise wz.BadRequest('At least one neighborhood field is required.')

        try:
            neighborhood = nqry.update(neighborhood_id, changes)
        except ValueError as err:
            raise wz.BadRequest(str(err))

        if neighborhood is None:
            if not nqry.dbc.is_db_up():
                raise wz.ServiceUnavailable('Database may be down.')
            raise wz.NotFound(f'Neighborhood {neighborhood_id} not found.')

        return {'Neighborhood': neighborhood}

    @api.response(HTTPStatus.NO_CONTENT.value, 'Deleted')
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def delete(self, neighborhood_id):
        """Delete one neighborhood by id."""
        delete_status = nqry.delete(neighborhood_id)

        if delete_status is None:
            return (
                {"message": "Database is down."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )

        if not delete_status:
            return (
                {"message": f"Neighborhood {neighborhood_id} not found."},
                HTTPStatus.NOT_FOUND,
            )

        return '', HTTPStatus.NO_CONTENT


@api.route(f'{NEIGHBORHOODS_EP}/<neighborhood_id>/properties')
class NeighborhoodProperties(Resource):
    """
    The get method will return all properties in a specific neighborhood.
    """
    @api.response(HTTPStatus.OK.value, 'Success', [property_model])
    @api.response(HTTPStatus.NOT_FOUND.value, 'Neighborhood Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self, neighborhood_id):
        """
        List properties in a neighborhood.
        Empty neighborhoods return an empty list,
        """
        neighborhood_exists = nqry.exists(neighborhood_id)
        if neighborhood_exists is None:
            raise wz.ServiceUnavailable('Database may be down.')
        if not neighborhood_exists:
            raise wz.NotFound(f'Neighborhood {neighborhood_id} not found.')

        properties = pqry.read()
        if properties is None:
            raise wz.ServiceUnavailable('Database may be down.')

        in_neighborhood = [
            p for p in properties
            if p.get('neighborhood_id') == neighborhood_id
        ]
        return {PROPERTIES_RESP: in_neighborhood}


@api.route(PROPERTIES_EP)
class Properties(Resource):
    """
    The get method will return a list of all properties in the database.
    """
    @api.response(HTTPStatus.OK.value, 'Success', [property_model])
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self):
        """
        The get method will return a list of all properties in the database.
        """
        properties = pqry.read()
        if properties is None:
            raise wz.ServiceUnavailable('Database may be down.')
        return {PROPERTIES_RESP: properties}

    @api.expect(property_model, validate=True)
    @api.response(HTTPStatus.CREATED.value, 'Created', property_model)
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Invalid property data')
    @api.response(HTTPStatus.CONFLICT.value, 'Property already exists')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def post(self):
        """Create a property associated with an existing neighborhood."""
        data = api.payload
        if pqry.exists(data['id']):
            raise wz.Conflict(f"Property {data['id']} already exists.")

        try:
            property_record = pqry.create(
                data['id'],
                data['address'],
                data['neighborhood_id'],
                data['price'],
                data['bedrooms'],
                data['bathrooms'],
                data['latitude'],
                data['longitude'],
            )
        except ValueError as err:
            raise wz.BadRequest(str(err))
        if property_record is None:
            raise wz.ServiceUnavailable('Database may be down.')
        return {PROPERTY_RESP: property_record}, HTTPStatus.CREATED


@api.route(f'{PROPERTIES_EP}/search')
@api.doc(params={
    'min_price': {
        'description': 'Inclusive minimum property price',
        'type': 'number',
    },
    'max_price': {
        'description': 'Inclusive maximum property price',
        'type': 'number',
    },
    'min_bedrooms': {
        'description': 'Inclusive minimum bedroom count',
        'type': 'number',
    },
    'max_bedrooms': {
        'description': 'Inclusive maximum bedroom count',
        'type': 'number',
    },
    'min_bathrooms': {
        'description': 'Inclusive minimum bathroom count',
        'type': 'number',
    },
    'max_bathrooms': {
        'description': 'Inclusive maximum bathroom count',
        'type': 'number',
    },
})
class PropertySearch(Resource):
    """Search properties by inclusive numeric bounds."""
    @api.response(HTTPStatus.OK.value, 'Success', [property_model])
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Invalid property filter')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self):
        """Return properties matching the supplied numeric bounds."""
        if not request.args:
            raise wz.BadRequest('At least one property filter is required.')

        try:
            filters = {
                key: float(request.args[key])
                for key in (
                    'min_price',
                    'max_price',
                    'min_bedrooms',
                    'max_bedrooms',
                    'min_bathrooms',
                    'max_bathrooms',
                )
                if key in request.args
            }
            properties = pqry.search(**filters)
        except ValueError as err:
            raise wz.BadRequest(str(err))

        if properties is None:
            raise wz.ServiceUnavailable('Database may be down.')
        return {PROPERTIES_RESP: properties}


@api.route(f'{PROPERTIES_EP}/<property_id>')
class Property(Resource):
    """
    The get method will return a single property by id.
    """
    @api.response(HTTPStatus.OK.value, 'Success', property_model)
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self, property_id):
        """
        The get method will return a single property by id.
        """
        property_record = pqry.read(property_id)
        if property_record is None:
            if not pqry.is_db_up():
                raise wz.ServiceUnavailable('Database may be down.')
            raise wz.NotFound(f'Property {property_id} not found.')
        return property_record

    @api.expect(property_update_model, validate=True)
    @api.response(HTTPStatus.OK.value, 'Updated', property_model)
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Invalid property data')
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def patch(self, property_id):
        """Update one or more fields on a property."""
        changes = api.payload or {}
        if not changes:
            raise wz.BadRequest('At least one property field is required.')
        try:
            property_record = pqry.update(property_id, changes)
        except ValueError as err:
            raise wz.BadRequest(str(err))
        if property_record is None:
            if not pqry.is_db_up():
                raise wz.ServiceUnavailable('Database may be down.')
            raise wz.NotFound(f'Property {property_id} not found.')
        return {PROPERTY_RESP: property_record}

    @api.response(HTTPStatus.NO_CONTENT.value, 'Deleted')
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def delete(self, property_id):
        """Delete one property by id."""
        deleted = pqry.delete(property_id)
        if deleted is None:
            raise wz.ServiceUnavailable('Database may be down.')
        if not deleted:
            raise wz.NotFound(f'Property {property_id} not found.')
        return '', HTTPStatus.NO_CONTENT
