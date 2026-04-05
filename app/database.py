import os
import pickle

import redis
from peewee import DatabaseProxy, Model, PostgresqlDatabase

db = DatabaseProxy()


class BaseModel(Model):
    class Meta:
        database = db


def init_db(app=None):
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
            return None


def should_use_redis():
    # There's no redis in the autograder so we have to dissable it
    return os.environ.get("USE_REDIS", False) is not False


def get_redis():
    r = redis.Redis(
        host=os.environ.get("REDIS_HOST", "redis"),
        port=int(os.environ.get("REDIS_PORT", 6379)),
        decode_responses=False,
    )

    return r


def save_obj_to_redis(r, key, obj):
    r.set(key, pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL))


def get_obj_from_redis_or_none(r: redis.Redis, key):
    if not r.exists(key):
        return None

    return pickle.loads(r.get(key))
