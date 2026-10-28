from http import HTTPStatus

from flask import Flask, request
from flask_restx import Resource, Api, fields  # Namespace
from flask_cors import CORS

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
    'region_id': fields.String(description='Id of an existing region',
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
    @api.response(HTTPStatus.OK.value, 'Success', [state_model])
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
    @api.response(HTTPStatus.CREATED.value, 'Created', state_model)
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
                data.get('region_id'),
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
    @api.response(HTTPStatus.OK.value, 'Success', state_model)
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
    @api.response(HTTPStatus.OK.value, 'Updated', state_model)
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
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def delete(self, state_id):
        """
        The delete method will delete a state by its two-letter code.
        """
        if not sqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')

        if not sqry.delete(state_id):
            raise wz.NotFound(f'State {state_id} not found.')
        return '', HTTPStatus.NO_CONTENT


@api.route(f'{STATES_EP}/<state_id>/neighborhoods')
class StateNeighborhoods(Resource):
    """
    The get method will return all neighborhoods in a state.
    """
    @api.response(HTTPStatus.OK.value, 'Success', [neighborhood_model])
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
        if not nqry.dbc.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')

        neighborhood_id = data[nqry.ID]

        if nqry.exists(neighborhood_id):
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
        if not nqry.dbc.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')

        neighborhood = nqry.read(neighborhood_id)
        if neighborhood is None:
            raise wz.NotFound(f'Neighborhood {neighborhood_id} not found.')
        return neighborhood

    @api.expect(neighborhood_update_model, validate=True)
    @api.response(HTTPStatus.OK.value, 'Updated', neighborhood_model)
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Invalid neighborhood data')
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def patch(self, neighborhood_id):
        """Update one or more fields on a neighborhood."""
        if not nqry.dbc.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')

        changes = api.payload or {}
        if not changes:
            raise wz.BadRequest('At least one neighborhood field is required.')

        try:
            neighborhood = nqry.update(neighborhood_id, changes)
        except ValueError as err:
            raise wz.BadRequest(str(err))

        if neighborhood is None:
            raise wz.NotFound(f'Neighborhood {neighborhood_id} not found.')

        return {'Neighborhood': neighborhood}

    @api.response(HTTPStatus.NO_CONTENT.value, 'Deleted')
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def delete(self, neighborhood_id):
        """Delete one neighborhood by id."""
        if not nqry.dbc.is_db_up():
            return (
                {"message": "Database is down."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )

        if not nqry.delete(neighborhood_id):
            return (
                {"message": f"Neighborhood {neighborhood_id} not found."},
                HTTPStatus.NOT_FOUND,
            )

        return '', HTTPStatus.NO_CONTENT


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
        if not pqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')
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
})
class PropertySearch(Resource):
    """Search properties by an inclusive minimum and/or maximum price."""
    @api.response(HTTPStatus.OK.value, 'Success', [property_model])
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Invalid price range')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self):
        """Return properties matching the supplied price bounds."""
        try:
            min_price = (
                float(request.args['min_price'])
                if 'min_price' in request.args else None
            )
            max_price = (
                float(request.args['max_price'])
                if 'max_price' in request.args else None
            )
            properties = pqry.search_by_price(min_price, max_price)
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
        if not pqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')

        property_record = pqry.read(property_id)
        if property_record is None:
            raise wz.NotFound(f'Property {property_id} not found.')
        return property_record

    @api.expect(property_update_model, validate=True)
    @api.response(HTTPStatus.OK.value, 'Updated', property_model)
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Invalid property data')
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def patch(self, property_id):
        """Update one or more fields on a property."""
        if not pqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')
        changes = api.payload or {}
        if not changes:
            raise wz.BadRequest('At least one property field is required.')
        try:
            property_record = pqry.update(property_id, changes)
        except ValueError as err:
            raise wz.BadRequest(str(err))
        if property_record is None:
            raise wz.NotFound(f'Property {property_id} not found.')
        return {PROPERTY_RESP: property_record}

    @api.response(HTTPStatus.NO_CONTENT.value, 'Deleted')
    @api.response(HTTPStatus.NOT_FOUND.value, 'Not Found')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def delete(self, property_id):
        """Delete one property by id."""
        if not pqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')
        if not pqry.delete(property_id):
            raise wz.NotFound(f'Property {property_id} not found.')
        return '', HTTPStatus.NO_CONTENT
