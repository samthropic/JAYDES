"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
from http import HTTPStatus

from flask import Flask  # , request
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

neighborhood_model = api.model('Neighborhood', {
    nqry.ID: fields.String(description='Neighborhood UUID'),
    'name': fields.String(description='Neighborhood name',
                          example='Greenwich Village'),
    'state_id': fields.String(description='Two-letter state code',
                              example='NY'),
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


@api.route(REGIONS_EP)
class Regions(Resource):
    """
    The get method will return a list of all regions in the database.
    """
    @api.response(HTTPStatus.OK.value, 'Success')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self):
        """
        The get method will return a list of all regions in the database.
        """
        regions = rqry.read()
        if regions is None:
            raise wz.ServiceUnavailable('Database may be down.')
        return {REGIONS_RESP: regions}


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
        if not nqry.is_db_up():
            raise wz.ServiceUnavailable('Database may be down.')

        neighborhood = nqry.read(neighborhood_id)
        if neighborhood is None:
            raise wz.NotFound(f'Neighborhood {neighborhood_id} not found.')
        return neighborhood


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
