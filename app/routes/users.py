from flask import Blueprint, jsonify, request
from app.models.users import Users
from typing import Dict
from datetime import datetime
import io, csv
from peewee import fn

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
    Users.delete().execute()

    count = 0
    try:
        text_stream = io.TextIOWrapper(file_storage.stream, encoding='utf-8', newline='')
        reader = csv.DictReader(text_stream)
        for row in reader:
            if not validate_user(row):
                raise Exception(f"{row} is not a valid user object")
            user_data = {
                "id": int(row.get("id")),
                "username": row.get("username"),
                "email": row.get("email"),
                "created_at": datetime.fromisoformat(row.get("created_at"))
            }
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

@users_bp.get("/users")
def list_users():
    """
    List users, optionally paginated via ?page=<int>&per_page=<int>.
    """
    try:
        query = Users.select()

        # Handle pagination parameters
        page = request.args.get("page", None)
        per_page = request.args.get("per_page", None)
        if page is not None or per_page is not None:
            try:
                page_int = int(page) if page is not None else 1
                per_page_int = int(per_page) if per_page is not None else 10
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid pagination parameters"}), 400
            if page_int < 1 or per_page_int < 1:
                return jsonify({"error": "page and per_page must be positive integers"}), 400
            total = query.count()
            offset = (page_int - 1) * per_page_int
            users_page = query.offset(offset).limit(per_page_int)
            users_list = []
            for u in users_page:
                users_list.append({
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "created_at": u.created_at.isoformat()
                })
            total_pages = (total + per_page_int - 1) // per_page_int
            return jsonify({
                "users": users_list,
                "page": page_int,
                "per_page": per_page_int,
                "total": total,
                "total_pages": total_pages
            }), 200

        # No pagination: return all users
        users = query
        users_list = []
        for u in users:
            users_list.append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "created_at": u.created_at.isoformat()
            })
        return jsonify(users_list), 200
    except Exception as e:
        return jsonify({"error": f"Internal Error: {e}"}), 500

# GET /users/<id> endpoint
@users_bp.get("/users/<int:id>")
def get_user_by_id(id: int):
    """
    Retrieve a single user by ID.
    """
    try:
        user = Users.get_or_none(Users.id == id)
        if user is None:
            return jsonify({"error": f"Error: user with id {id} does not exist"}), 404
        result = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Internal Error: {e}"}), 500
    
# POST /users endpoint
@users_bp.post("/users")
def create_user():
    """
    Create a new user. Expects JSON with 'username' and 'email' only.
    """
    # Parse JSON body; use silent to avoid 415 on missing content-type
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Error: Json data required"}), 400

    # Disallow client-specified id or created_at
    if "id" in data:
        return jsonify({"error": "Error: 'id' is not allowed"}), 400
    if "created_at" in data:
        return jsonify({"error": "Error: 'created_at' is not allowed"}), 400

    # Required fields
    username = data.get("username")
    email = data.get("email")
    if username is None:
        return jsonify({"error": "Error: username is required"}), 400
    if email is None:
        return jsonify({"error": "Error: email is required"}), 400

    # Validate types
    if not isinstance(username, str) or not username.strip():
        return jsonify({"error": "Error: username must be a non-empty string"}), 400
    if not isinstance(email, str) or not email.strip():
        return jsonify({"error": "Error: email must be a non-empty string"}), 400

    try:
        # Generate a unique id: max existing id + 1
        max_id = Users.select(fn.MAX(Users.id)).scalar() or 0
        new_id = max_id + 1
        user = Users.create(id=new_id, username=username.strip(), email=email.strip())
        result = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        }
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": f"Internal Error: {e}"}), 500
    
# PUT /users/<id> endpoint
@users_bp.put("/users/<int:id>")
def update_user(id: int):
    """
    Update an existing user. Accepts 'username' and/or 'email'.
    """
    try:
        user = Users.get_or_none(Users.id == id)
        if user is None:
            return jsonify({"error": f"Error: user with id {id} does not exist"}), 404
        # Parse JSON body
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Error: Json data required"}), 400

        # Disallow id or created_at
        if "id" in data:
            return jsonify({"error": "Error: 'id' is not allowed"}), 400
        if "created_at" in data:
            return jsonify({"error": "Error: 'created_at' is not allowed"}), 400

        # Ensure at least one updatable field provided
        if "username" not in data and "email" not in data:
            return jsonify({"error": "Error: username or email required"}), 400

        # Validate and apply updates
        if "username" in data:
            username = data.get("username")
            if not isinstance(username, str) or not username.strip():
                return jsonify({"error": "Error: username must be a non-empty string"}), 400
            user.username = username.strip()
        if "email" in data:
            email = data.get("email")
            if not isinstance(email, str) or not email.strip():
                return jsonify({"error": "Error: email must be a non-empty string"}), 400
            user.email = email.strip()

        user.save()
        result = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Internal Error: {e}"}), 500
    
@users_bp.delete("/users/<int:id>")
def delete_user(id: int):
    """
    Delete an existing user by ID.
    """
    try:
        user = Users.get_or_none(Users.id == id)
        if user is None:
            return jsonify({"error": f"Error: user with id {id} does not exist"}), 404
        # prepare response before deletion
        result = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        }
        user.delete_instance()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Internal Error: {e}"}), 500
