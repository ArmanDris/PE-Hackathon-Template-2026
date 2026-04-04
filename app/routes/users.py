from flask import Blueprint, jsonify, request
from app.database import db
from app.models.users import Users
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
    count = 0
    try:
        text_stream = io.TextIOWrapper(file_storage.stream, encoding='utf-8', newline='')
        reader = csv.DictReader(text_stream)
        for row in reader:
            print(row)
            count += 1
    except Exception as e:
        return jsonify({"error": f"Failed to parse CSV: {e}"}), 400
    return jsonify({"count": count}), 200
