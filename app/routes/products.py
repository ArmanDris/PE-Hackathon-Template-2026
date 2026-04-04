from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.product import Product

products_bp = Blueprint("products", __name__)


@products_bp.route("/products")
def list_products():
    products = Product.select()
    return jsonify([model_to_dict(p) for p in products])
