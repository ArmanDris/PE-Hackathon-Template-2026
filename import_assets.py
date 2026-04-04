import csv

from peewee import chunked

from app.database import db, init_db
from app.models.events import Events
from app.models.urls import Urls
from app.models.users import Users


def reset_pk_sequence(table_name, pk_column="id"):
    # Keep SERIAL/identity sequence aligned with imported explicit IDs.
    db.execute_sql(
        f"""
        SELECT setval(
            pg_get_serial_sequence('{table_name}', '{pk_column}'),
            COALESCE((SELECT MAX({pk_column}) FROM {table_name}), 1),
            true
        )
        """
    )


def load_csv_events(filepath):
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with db.atomic():
        for batch in chunked(rows, 100):
            Events.insert_many(batch).execute()


def load_csv_urls(filepath):
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with db.atomic():
        for batch in chunked(rows, 100):
            Urls.insert_many(batch).execute()


def load_csv_users(filepath):
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with db.atomic():
        for batch in chunked(rows, 100):
            Users.insert_many(batch).execute()


init_db(None)

db.create_tables([Events, Urls, Users])

load_csv_users("app/assets/users.csv")
load_csv_urls("app/assets/urls.csv")
load_csv_events("app/assets/events.csv")

reset_pk_sequence("users")
reset_pk_sequence("urls")
reset_pk_sequence("events")

db.close()
