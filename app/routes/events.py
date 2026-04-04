import json

from datetime import datetime

from flask import Blueprint, Response, jsonify, request
from playhouse.shortcuts import model_to_dict

from app.models.events import Events

events_bp = Blueprint("events", __name__)

QUERY_FIELDS = {
    "id": Events.id,
    "url_id": Events.url_id,
    "user_id": Events.user_id,
    "event_type": Events.event_type,
    "timestamp": Events.timestamp,
    "details": Events.details
}

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

def build_search_list(query_json):
    filters = []
    for key, value, in query_json.items():
        field = QUERY_FIELDS.get(key)
        if not field or value is None:
            continue
        #temp fix for details
        if key == "details":
            try:
                filters.append(field.contains(json.dumps(value)))
            except Exception:
                continue
        else:
            filters.append(field == value)

    return filters

# Will filter the Events based on query param, if none are provided it will return the whole list
def get_events_filtered(query_param):
    print("QUery params: ", query_param)
    try :
        filters = build_search_list(query_param)
    except Exception as e:
        return jsonify({"error": f"Filter build error"}), 500
        
    query = Events.select()

    try :
        if filters:
            query = query.where(*filters)
    except:
        return jsonify({"error": "There was a problem while filtering the events"}), 500

    query = query.dicts()

    cleaned_result = [prepare_values(r) for r in query]
    return jsonify(cleaned_result)


@events_bp.route("/events", methods=['GET', 'POST'])
def list_events():
    if request.method == 'GET':

        query = request.args.to_dict()
        try:
            filtered_response = get_events_filtered(query)
            return filtered_response

            # Legacy response used to format properly, might still need to be used
            #return Response(
            #    json.dumps(json_list, indent=2, default=str),
            #    mimetype="application/json"
            #)
        except Exception as e:
            # Inspired changes, apparently this can happen if there is something wrong with the db
            return jsonify({"error": f"Internal Error: {e}"}), 500

        #try:
        #    query = request.get_json()
        #    if query is None:
        #        return jsonify({"error": "error"}), 400 # dont know what to do here because maybe empty post shoudl return something
        #    else: # Writing explicitly for clarity from comment above
        #        query_response = get_events_filtered(query)
        #        return query_response
        #except Exception as e:
        #    return jsonify({"error": f"Internal Erorr: {e}"}), 500

    if request.method == 'POST':
        return jsonify({"error:": "Be kind to all"}), 418
    return 1
