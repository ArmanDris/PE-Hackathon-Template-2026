from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.urls import Urls

urls_bp = Blueprint("urls", __name__)


@urls_bp.route("/urls")
def list_urls():
    return jsonify("Hello, world!")
