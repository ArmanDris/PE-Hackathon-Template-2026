import json

from datetime import datetime

from flask import Blueprint, jsonify, Response
from playhouse.shortcuts import model_to_dict

from app.models.events import Events

events_bp = Blueprint("events", __name__)

def prepare_values(event_val):
    if event_val.get("details"):
        try:
            event_val["details"] = json.loads(event_val["details"])
        except:
            event_val["details"] = None

    if event_val.get("timestamp"):
        try:
            event_val["timestamp"] = datetime.isoformat(event_val["timestamp"])
        except:
            event_val["timestamp"] = None

    return event_dict

@events_bp.route("/events")
def list_events():
    try:
        events = Events.select().dicts()

        json_list = []
        for x in events:
            if x is None:
                continue
            
            conv_dict = x
            # Details is a string containing a json, therefor needs to be parsed
            if conv_dict.get("details"):
                conv_dict["details"] = json.loads(conv_dict["details"])
            # Ive heard that model to dict does not format dates properly
            # Which makes me think json.loads probably doesnt either
            if conv_dict.get("timestamp"):
                conv_dict["timestamp"] = datetime.isoformat(conv_dict["timestamp"])
            json_list.append(conv_dict)

        #This is the only way i could figure out how to keep the order. Otherwise jsonify is much simpler
        return Response(
            json.dumps(json_list, indent=2, default=str),
            mimetype="application/json"
        )
    except Exception as e:
        # Inspired changes, apparently this can happen if there is something wrong with the db
        return jsonify({"error": f"Internal Error: {e}"}), 500
