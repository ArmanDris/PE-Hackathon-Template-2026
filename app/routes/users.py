from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.users import Users

users_bp = Blueprint("users", __name__)

@users_bp.route("/users")
def list_users():
    users = Users.select()
    return jsonify([model_to_dict(x) for x in users])
