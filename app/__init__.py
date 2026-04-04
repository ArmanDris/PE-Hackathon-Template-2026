from dotenv import load_dotenv
from flask import Flask, jsonify

from app.database import db, init_db
from app.models import product
from app.models.events import Events
from app.models.urls import Urls
from app.models.users import Users
from app.routes import register_routes


def create_app():
    load_dotenv()

    app = Flask(__name__)

    init_db(app)

    from app import models  # noqa: F401 - registers models with Peewee

    db.create_tables([Users, Events, Urls], safe=True)

    register_routes(app)

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    return app
