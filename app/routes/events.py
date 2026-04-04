import json

from datetime import datetime

from flask import Blueprint, Response, jsonify, request
from playhouse.shortcuts import model_to_dict

from app.models.events import Events

events_bp = Blueprint("events", __name__)

# This helper is designed the handle all the misformatting that
# might be done while trying to parse certain values from the
# Events class
# Keys processed:
# "details", "timestamp"
def prepare_values(event_val):
    # details is a string, so it needs to be prased into a json
    if event_val.get("details"):
        try:
            event_val["details"] = json.loads(event_val["details"])
        except:
            event_val["details"] = None
    # Ive heard that jsonify doesnt format timestamps either so i think json.loads doesnt either
    # Added this for continuity
    if event_val.get("timestamp"):
        try:
            # date is already close to the format but missing 'T' in the center
            event_val["timestamp"] = datetime.isoformat(event_val["timestamp"])
        except:
            event_val["timestamp"] = None

    return event_val # The event with processed values or the unchanged if none of the keys needed it

@events_bp.route("/events")
def list_events():

    if request.method == 'GET':
        try:
            events = Events.select().dicts()

            json_list = []
            for conv_dict in events:
                if conv_dict is None:
                    continue
                json_list.append(prepare_values(conv_dict))

            #This is the only way i could figure out how to keep the order. Otherwise jsonify is much simpler
            return Response(
                json.dumps(json_list, indent=2, default=str),
                mimetype="application/json"
            )
        except Exception as e:
            # Inspired changes, apparently this can happen if there is something wrong with the db
            return jsonify({"error": f"Internal Error: {e}"}), 500

    if request.method == 'POST':
        print("Some post logic")
