from flask import Blueprint, jsonify, request
from app.models.users import Users
from typing import Dict
from datetime import datetime
import io, csv

users_bp = Blueprint("users", __name__)

@users_bp.route("/users/bulk", methods=["POST"])
def users_bulk():
    """
    Bulk upload users via a CSV file sent as multipart/form-data.
    Parses each row in the CSV and prints it. Returns status OK on success.
    """
    print(f"got files: {request.files}")
    if not request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file_storage = next(iter(request.files.values()))
    if not file_storage.filename:
        return jsonify({"error": "No selected file"}), 400
    # (Optionally) drop all existing users to avoid duplicates
    Users.delete().execute()

    count = 0
    try:
        text_stream = io.TextIOWrapper(file_storage.stream, encoding='utf-8', newline='')
        reader = csv.DictReader(text_stream)
        for row in reader:
            if not validate_user(row):
                raise Exception(f"{row} is not a valid user object")
            # Prepare data for insertion, converting types
            user_data = {
                "id": int(row.get("id")),
                "username": row.get("username"),
                "email": row.get("email"),
                "created_at": datetime.fromisoformat(row.get("created_at"))
            }
            # Insert new user record with provided ID
            Users.create(**user_data)
            count += 1
    except Exception as e:
        return jsonify({"error": f"Failed to parse CSV: {e}"}), 400
    return jsonify({"count": count}), 200

def validate_user(user: Dict) -> bool:
    """
    Given a plain dict (e.g. from csv.DictReader), validate that it has
    the required keys and correct types/formats for a Users record.
    Required: username and email are non-empty strings;
    created_at is a datetime or an ISO-format datetime string.
    """

    # Check presence and type of username
    username = user.get("username")
    if not isinstance(username, str) or not username.strip():
        return False

    # Check presence and type of email
    email = user.get("email")
    if not isinstance(email, str) or not email.strip():
        return False

    # Check created_at
    created_at = user.get("created_at")
    if isinstance(created_at, str):
        try:
            datetime.fromisoformat(created_at)
        except ValueError:
            return False
    elif not isinstance(created_at, datetime):
        return False

    return True
