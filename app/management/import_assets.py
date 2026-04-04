import csv

from peewee import chunked

from app.database import db
from app.models.events import Events
from app.models.urls import Urls
from app.models.users import Users


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


load_csv_users("app/assets/events.csv")
load_csv_urls("app/assets/urls.csv")
load_csv_users("app/assets/users.csv")
