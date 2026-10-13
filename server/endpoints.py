"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
from http import HTTPStatus

from flask import Flask  # , request
from flask_restx import Resource, Api, fields  # Namespace
from flask_cors import CORS

import properties.query as pqry
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

state_model = api.model('State', {
    sqry.ID: fields.String(description='Two-letter state code', example='NY'),
    'name': fields.String(description='State name', example='New York'),
    'capital': fields.String(description='State capital', example='Albany'),
    'population': fields.Integer(description='Population'),
    'area_sq_miles': fields.Float(description='Area in square miles'),
})

property_model = api.model('Property', {
    'id': fields.String(description='Property id'),
    'address': fields.String(description='Property address',
                             example='125 Perry Street, New York, NY'),
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
