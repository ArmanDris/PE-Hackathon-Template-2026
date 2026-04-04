import pytest
from peewee import SqliteDatabase

from app import create_app
from app.database import db
from app.models.urls import Urls
from app.models.users import Users

TEST_MODELS = [Users, Urls]


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(TESTING=True)

    # Replace Postgres with in-memory SQLite for tests
    # NOTE: This will not work with Events cause sqlite doesn't support JSONField
    test_db = SqliteDatabase(":memory:")
    db.initialize(test_db)

    test_db.bind(TEST_MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables(TEST_MODELS)

    # Remove the teardown_appcontext handler that closes the DB during tests
    # (closing in-memory SQLite destroys the database)
    app.teardown_appcontext_funcs = []

    yield app

    print("dropped stuff")
    test_db.drop_tables(TEST_MODELS)
    test_db.close()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def user(app):
    user = Users.create(
        username="Test", email="test@example.com", created_at="2026-04-04T16:55:31.744Z"
    )
    return user
