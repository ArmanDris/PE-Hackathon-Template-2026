from datetime import datetime

from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict

from app.models.urls import Urls

urls_bp = Blueprint("urls", __name__)


def urls_model_to_dict(u):
    output = model_to_dict(u)

    # Model to dict does not format dates properly
    output["created_at"] = datetime.isoformat(u.created_at)
    output["updated_at"] = datetime.isoformat(u.updated_at)

    return output


@urls_bp.route("/urls")
def list_urls():

    try:
        urls = Urls.select()

        # Filtering
        id = request.args.get("id", None)
        if id is not None:
            try:
                parsed_id = int(id)
            except ValueError:
                return jsonify({"error": f"Invalid ID: {id}"}), 400

            urls = urls.where(Urls.id == parsed_id)

        user_id = request.args.get("user_id", None)
        if user_id is not None:
            try:
                parsed_user_id = int(user_id)
            except ValueError:
                return jsonify({"error": f"Invalid user_id: {user_id}"}), 400

            urls = urls.where(Urls.user_id == parsed_user_id)

        short_code = request.args.get("short_code", None)
        if short_code is not None:
            urls = urls.where(Urls.short_code == short_code)

        original_url = request.args.get("original_url", None)
        if original_url is not None:
            urls = urls.where(Urls.original_url == original_url)

        title = request.args.get("title", None)
        if title is not None:
            urls = urls.where(Urls.title == title)

        is_active = request.args.get("is_active", None)
        if is_active is not None:
            true_values = {"true", "1", "yes", "y", "on"}
            false_values = {"false", "0", "no", "n", "off"}
            normalized = is_active.strip().lower()

            if normalized in true_values:
                parsed_is_active = True
            elif normalized in false_values:
                parsed_is_active = False
            else:
                return jsonify({"error": f"Invalid is_active: {is_active}"}), 400

            urls = urls.where(Urls.is_active == parsed_is_active)

        created_at = request.args.get("created_at", None)
        if created_at is not None:
            try:
                parsed_created_at = datetime.fromisoformat(created_at)
            except ValueError:
                return (
                    jsonify(
                        {
                            "error": "Invalid created_at. Use ISO format, for example 2026-04-03T10:15:00"
                        }
                    ),
                    400,
                )

            urls = urls.where(Urls.created_at == parsed_created_at)

        updated_at = request.args.get("updated_at", None)
        if updated_at is not None:
            try:
                parsed_updated_at = datetime.fromisoformat(updated_at)
            except ValueError:
                return (
                    jsonify(
                        {
                            "error": "Invalid updated_at. Use ISO format, for example 2026-04-03T10:15:00"
                        }
                    ),
                    400,
                )

            urls = urls.where(Urls.updated_at == parsed_updated_at)

        return jsonify([urls_model_to_dict(u) for u in urls])
    except Exception as e:
        # This should only happen if there's something wrong with the db
        return jsonify({"error": f"Internal Error: {e}"}), 500
