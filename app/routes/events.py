import json
from flask import Blueprint, jsonify, Response
from playhouse.shortcuts import model_to_dict

from app.models.events import Events

events_bp = Blueprint("events", __name__)

@events_bp.route("/events")
def list_events():
    events = Events.select().dicts()

    json_list = []
    for x in events:
        conv_dict = x
        if conv_dict.get("details"):
            conv_dict["details"] = json.loads(conv_dict["details"])
        json_list.append(conv_dict)

    return Response(
        json.dumps(json_list, indent=2, default=str),
        mimetype="application/json"
    )
