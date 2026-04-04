from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.events import Events

events_bp = Blueprint("events", __name__)

@events_bp.route("/events")
def list_events():
    events = Events.select()
    return jsonify([model_to_dict(x) for x in events])

