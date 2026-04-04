import ipaddress
import re
import secrets
from datetime import datetime, timezone
from urllib.parse import urlparse

from flask import Blueprint, abort, jsonify, redirect, request
from playhouse.shortcuts import model_to_dict

from app.models.urls import Urls
from app.models.users import Users

urls_bp = Blueprint("urls", __name__)


def is_valid_http_url(url: str) -> bool:
    if not isinstance(url, str):
        return False

    candidate = url.strip()
    if not candidate:
        return False

    if any(char.isspace() for char in candidate):
        return False

    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"}:
        return False

    if not parsed.netloc or not parsed.hostname:
        return False

    hostname = parsed.hostname
    if hostname == "localhost":
        return True

    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        pass

    if "." not in hostname:
        return False

    labels = hostname.split(".")
    for label in labels:
        if not label:
            return False
        if label.startswith("-") or label.endswith("-"):
            return False
        if not re.fullmatch(r"[A-Za-z0-9-]+", label):
            return False

    return True


def urls_model_to_dict(u):
    output = model_to_dict(u)

    # Model to dict does not format dates properly
    output["created_at"] = datetime.isoformat(u.created_at)
    output["updated_at"] = datetime.isoformat(u.updated_at)

    return output


@urls_bp.get("/urls")
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


def generate_short_code():
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    output = ""

    for _ in range(6):
        # Use secrets to ensure it's properly random
        output += secrets.choice(characters)

    return output


@urls_bp.post("/urls")
def create_url():
    data = request.json

    if data is None:
        return (
            jsonify({"error": "Error: Json data required"}),
            400,
        )

    user_id = data.get("user_id", None)
    if user_id is None:
        return (
            jsonify({"error": "Error: User id required"}),
            400,
        )

    # Check to ensure this user is real
    user = Users.get_or_none(Users.id == user_id)
    if user is None:
        return (
            jsonify({"error": f"Error: No user exists for id {user_id}"}),
            400,
        )

    original_url = data.get("original_url", None)
    if original_url is None:
        return (
            jsonify({"error": "Error: original_url required"}),
            400,
        )

    original_url = original_url.strip()
    if not is_valid_http_url(original_url):
        return (
            jsonify({"error": "Error: original_url must be a valid URL"}),
            400,
        )

    title = data.get("title", None)
    if title is None:
        return (
            jsonify({"error": "Error: title is required"}),
            400,
        )

    try:
        short_code = generate_short_code()
        new_url = Urls.create(
            user_id=user_id,
            original_url=original_url,
            title=title,
            is_active=True,
            short_code=short_code,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        return jsonify(urls_model_to_dict(new_url)), 201

    except Exception as e:
        # This should only happen if there's something wrong with the db
        return jsonify({"error": f"Internal Error: {e}"}), 500


@urls_bp.get("/urls/<int:id>")
def get_url_by_id(id: int):
    url = Urls.get_or_none(Urls.id == id)

    if url is None:
        return (
            jsonify({"error": f"Error: url with id {id} does not exist"}),
            400,
        )

    return jsonify(urls_model_to_dict(url)), 200


@urls_bp.put("/urls/<int:id>")
def update_url(id):
    url = Urls.get_or_none(Urls.id == id)

    if url is None:
        return (
            jsonify({"error": f"Error: url with id {id} does not exist"}),
            400,
        )

    data = request.json
    if data is None:
        return (
            jsonify({"error": f"Error: json payload is required"}),
            400,
        )

    original_url = data.get("original_url", None)
    if original_url is not None:
        url.original_url = original_url

    title = data.get("title", None)
    if title is not None:
        url.title = title

    is_active = data.get("is_active", None)
    if is_active is not None:
        url.is_active = is_active

    try:
        url.save()
    except Exception as e:
        return jsonify({"error": f"Internal Error: Failed to update url: {e}"}), 500

    return jsonify(urls_model_to_dict(url)), 200


@urls_bp.delete("/urls/<int:id>")
def delete_url_by_id(id: int):
    url = Urls.get_or_none(Urls.id == id)

    if url is None:
        return (
            jsonify({"error": f"Error: url with id {id} does not exist"}),
            400,
        )

    try:
        url.delete_instance()
    except Exception as e:
        return jsonify({"error": f"Internal Error: Failed to delete url: {e}"}), 500

    return jsonify(urls_model_to_dict(url)), 200


@urls_bp.route("/urls/<shortcode>/redirect")
@urls_bp.route("/<shortcode>")
def redirect_url(shortcode):
    if len(shortcode) != 6:
        abort(404)

    # TODO: Maybe add sorting on short_code field?
    url = Urls.get_or_none(Urls.short_code == shortcode)

    if url is None:
        abort(404)

    if not url.is_active:
        abort(404)

    return redirect(url.original_url), 302
