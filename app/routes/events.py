import logging

logger = logging.getLogger(__name__)

import json

from datetime import datetime, timezone

from flask import Blueprint, Response, jsonify, request

from app.models.events import Events
from app.models.users import Users

events_bp = Blueprint("events", __name__)

EVENT_FIELDS = {
    "id": {"field": Events.id, "type": int},
    "url_id": {"field": Events.url_id, "type": int},
    "user_id": {"field": Events.user_id, "type": int},
    "event_type": {"field": Events.event_type, "type": str},
    "timestamp": {"field": Events.timestamp, "type": "datetime"},
    "details": {"field": Events.details, "type": "json"},
}

CREATE_FIELDS = {
    "url_id": Events.url_id,
    "user_id": Events.user_id,
    "event_type": Events.event_type,
    "details": Events.details
}

# This perserves the order of each item, jsonify might be able to do this
# I just dont know how :()
def better_jsonify(jval, mimetype="application/json", status=200, indent=2):
    return Response(
                json.dumps(jval, indent=indent, default=str),
                mimetype=mimetype,
                status=status
            )

# This function is designed the handle all the misformatting that
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
            # not really worth it to log
        except:
            event_val["timestamp"] = None

    return event_val # The event with processed values or the unchanged if none of the keys needed it

# Constructs list of filteres specified by qurey parameters
# to be used in get_events_filtered
def build_search_list(query_json):
    filters = []
    for key, value, in query_json.items():
        config = EVENT_FIELDS.get(key)
        if not config or value is None:
            continue
        field = config["field"]

        #temp fix for details
        if key == "details":
            try:
                logger.warning("Someone tried to use details as a query parameter. This has a high chance of failing. No server risk")
                filters.append(field.contains(json.dumps(value)))
            except Exception:
                continue
        else:
            filters.append(field == value)

    logger.debug("Events search filters successfully processed",
                 extra={"filters:": filters})

    return filters

# Will filter the Events based on query param, if none are provided it will return the whole list
def get_events_filtered(query_param):
    filters = build_search_list(query_param)
         
    query = Events.select()

    # applies the fitler to query
    if filters:
        query = query.where(*filters)

    # gets the json value from selected query
    query = query.dicts()

    logger.debug("Event query results(limited 2)")

    cleaned_result = [prepare_values(r) for r in query]
    return cleaned_result


#--------------------------------------------------------------------
#-------------------------POST SANITIZATION-------------------------
#--------------------------------------------------------------------
def validate_post_format(key, value):

    logger.debug("Event POST value to check:",
                 extra={"Key:": key, "Value:": value})
    
    if EVENT_FIELDS[key]["type"] == int:
        try:
            return int(value)
        except ValueError:
            return None

        
    elif EVENT_FIELDS[key]["type"] == str:
        return value

        
    elif EVENT_FIELDS[key]["type"] == "datetime":
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

        
    elif EVENT_FIELDS[key]["type"] == "json":
        try:
            return json.dumps(value)
        except ValueError:
            return None
        
    return None
#--------------------------------------------------------------------
#--------------------------------------------------------------------
#--------------------------------------------------------------------



@events_bp.route("/events", methods=['GET', 'POST'])
def list_events():

    logger.info(
        "Incoming request",
        extra={
            "method": request.method,
            "path": request.path,
            "query_params": request.args.to_dict()
            }
    )


    #----------------------------------------------------------
    #-----------------------GET--------------------------------
    #----------------------------------------------------------
    if request.method == 'GET':
        
        query = request.args.to_dict()
        try:
            filtered_response = get_events_filtered(query)

            logging.info(
                "Events fetched succesfully",
                extra={
                    "results_count": len(filtered_response)        
                    }
            )

            return better_jsonify(filtered_response)
        except Exception as e:
            logger.exception(
                "Failed to fetch events",
                extra={
                    "query_params": query
                }
            )
            return jsonify({"error": f"Internal Error: {e}"}), 500


    #----------------------------------------------------------
    #------------------------POST------------------------------
    #----------------------------------------------------------

    # Should only be for creating an event
    if request.method == 'POST':
        try:
            event_json = request.get_json()
        except:
            return jsonify({"error": "Error: Invalid json"}), 400

        if not event_json:
            return jsonify({"error": "Error: Invalid JSON"}), 400

        create_event = {}
        for key in CREATE_FIELDS.keys():
            # Checks if post data is missing any 
            if key not in event_json.keys():
                return jsonify({"error": f"Error: {key} is required when creating an event"}), 400
            else:
                safe_val = validate_post_format(key, event_json[key]) # -----POST SANITIZATION--------
                if safe_val is None:
                    return jsonify({"error": f"Error: {key} must be of type {EVENT_FIELDS[key]['type']}"})
                create_event[key] = safe_val

        try:
            # Verify user actually exists
            if Users.get_or_none(Users.id == create_event["user_id"]) is None:
                return jsonify({"error": f"Error: No user with matching id {create_event['user_id']}"})
            
        except Exception as e:
            return jsonify({"error": "Error: There was a problem during authentication"}), 400 # ..."authentication"
            
        try:
            Events.create(
                url_id=create_event["url_id"],
                user_id=create_event["user_id"],
                event_type=create_event["event_type"],
                timestamp=datetime.now(timezone.utc),
                details=create_event["details"]
            )

            logger.info("Event succusfully create",
                        extra={
                            "url_id": create_event["url_id"],
                            "user_id": create_event["user_id"],
                            "even_type": create_event["event_type"],
                            "timestamp": datetime.now(timezone.utc),
                            "details": create_event["details"]
                        })
    
            return better_jsonify(create_event, status=201)
            
        except Exception as e:
            logger.exception(
                "Failed to create event",
                extra={"body": event_json}
            )
            return jsonify({"error": f"Internal Error: {e}"}), 500

    
    logger.info("Reached end of /event with no response, serving 500")
    return jsonify({""}), 500 # fallback not sure if this is needed
