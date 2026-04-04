import pytest
from peewee import SqliteDatabase

from app import create_app
from app.database import db
from app.models.users import Users
from app.models.urls import Urls

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

    yield app

    test_db.drop_tables(TEST_MODELS)
    test_db.close()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
