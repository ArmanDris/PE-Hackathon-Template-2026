import os

from peewee import DatabaseProxy, Model, PostgresqlDatabase

db = DatabaseProxy()


class BaseModel(Model):
    class Meta:
        database = db


def init_db(app=None):
    database_url = os.environ.get("DATABASE_URL")
    # For integration testing, we use an isolated, ephemeral sqlite database
    if database_url and database_url.startswith("sqlite://"):
        from peewee import SqliteDatabase

        # strip the prefix
        prefix = "sqlite:///"
        if database_url.startswith(prefix):
            path = database_url[len(prefix) :]
        else:
            path = database_url[len("sqlite://") :]
        database = SqliteDatabase(path or ":memory:")
    else:
        database = PostgresqlDatabase(
            os.environ.get("DATABASE_NAME", "hackathon_db"),
            host=os.environ.get("DATABASE_HOST", "localhost"),
            port=int(os.environ.get("DATABASE_PORT", 5432)),
            user=os.environ.get("DATABASE_USER", "postgres"),
            password=os.environ.get("DATABASE_PASSWORD", "postgres"),
        )
    db.initialize(database)

    if app:

        @app.before_request
        def _db_connect():
            db.connect(reuse_if_open=True)

        @app.teardown_appcontext
        def _db_close(exc):
            if not db.is_closed():
                db.close()
