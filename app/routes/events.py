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
    if len(query_json) <= 0:
        return jsonify({"error", "No post body was provided"}), 400

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

# This will get the values from the event db that correspond
# to the filter provided in the post body
def get_events_filtered(json_query):
    filters = build_search_list(json_query)
    if filters is None:
        return jsonify({"error": "No post body was provided"}), 400 # again not sure but wasnt comfortable leaving empty
    if len(filters) <= 0:
        return jsonify({"error": "Query parameters invalid."}), 400 # all these need to be changed with new logging setup i think
    query = Events.select().where(*filters).dicts()
    #result = query.where(*filters)
    cleaned_result = [prepare_values(r) for r in query]
    return jsonify(cleaned_result)



@events_bp.route("/events", methods=['GET', 'POST'])
def list_events():
    if request.method == 'GET':
        try:
            events = Events.select().dicts()
            # Cant use model_to_dict because it doesnt handle some values properly(ex. details or timestamps)
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
        try:
            query = request.get_json()
            if query is None:
                return jsonify({"error": "error"}), 400 # dont know what to do here because maybe empty post shoudl return something
            else: # Writing explicitly for clarity from comment above
                query_response = get_events_filtered(query)
                return query_response
        except Exception as e:
            return jsonify({"error": f"Internal Erorr: {e}"}), 500
            

    return 1
