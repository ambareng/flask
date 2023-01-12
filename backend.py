import json

from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
from flask_restful import Api
import sqlite3

from utils import get_events, get_event_by_id, create_event, update_event, delete_event, validate_schedule, \
    validate_request

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    return {'message': 'ok'}, 200


@app.route('/v1/api/events/', methods=['GET'])
def api_get_events():
    return jsonify(get_events())


@app.route('/v1/api/events/<int:event_id>/', methods=['GET'])
def api_get_event_by_id(event_id=None):
    return jsonify(get_event_by_id(event_id))


@app.route('/v1/api/events/create/',  methods=['POST'])
def api_create_event():
    event = request.get_json()
    errors = validate_request(event)
    if errors is not None:
        return errors
    errors = validate_schedule(event['event_date'], event['start_time'], event['end_time'])
    if errors is not None:
        return errors
    return jsonify(create_event(event))


@app.route('/v1/api/events/update/',  methods=['PUT'])
def api_update_event():
    event = request.get_json()
    errors = validate_schedule(event['event_date'], event['start_time'], event['end_time'], event['id'])
    if errors is not None:
        return errors
    return jsonify(update_event(event))


@app.route('/v1/api/events/<int:event_id>/delete/',  methods=['DELETE'])
def api_delete_user(event_id=None):
    return jsonify(delete_event(event_id))
