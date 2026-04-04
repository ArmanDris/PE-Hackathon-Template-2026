from datetime import datetime, timezone

import pytest

from app.models.urls import Urls
from app.models.users import Users


def test_list_all(client):
    urls = [
        {
            "user_id": 1,
            "short_code": "abc123",
            "original_url": "https://fun.co",
            "title": "A Link",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
        {
            "user_id": 2,
            "short_code": "def456",
            "original_url": "https://fun.co",
            "title": "A Link",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
    ]
    for url in urls:
        Urls.create(**url)

    response = client.get("/urls")

    assert response.status_code == 200
    assert response.json is not None
    assert len(response.json) == len(urls)

    count = 0
    for res in response.json:
        for key in res:
            # Don't worry about id
            if key == "id":
                continue

            if isinstance(urls[count][key], datetime):
                assert res[key] == datetime.isoformat(urls[count][key])
            else:
                assert res[key] == urls[count][key]

        count += 1


def test_list_filter(client):
    urls = [
        {
            "user_id": 1,
            "short_code": "abc123",
            "original_url": "https://fun.co",
            "title": "A Link",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
        {
            "user_id": 2,
            "short_code": "def456",
            "original_url": "https://fun.co",
            "title": "A Link",
            "is_active": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
    ]
    for url in urls:
        Urls.create(**url)

    response = client.get("/urls?is_active=1")

    assert response.status_code == 200
    assert response.json is not None
    assert len(response.json) == 1

    count = 0
    for res in response.json:
        for key in res:
            # Don't worry about id
            if key == "id":
                continue

            if isinstance(urls[count][key], datetime):
                assert res[key] == datetime.isoformat(urls[count][key])
            else:
                assert res[key] == urls[count][key]

        count += 1


def test_list_filter_bad(client):
    urls = [
        {
            "user_id": 1,
            "short_code": "abc123",
            "original_url": "https://fun.co",
            "title": "A Link",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
        {
            "user_id": 2,
            "short_code": "def456",
            "original_url": "https://fun.co",
            "title": "A Link",
            "is_active": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
    ]
    for url in urls:
        Urls.create(**url)

    response = client.get("/urls?user_id=tom")

    assert response.status_code == 400


def test_create_positive_path(client, user):
    payload = {
        "user_id": user.id,
        "original_url": "https://fun.co",
        "title": "A Link",
    }

    response = client.post("/urls", json=payload)
    assert response.status_code == 201
    assert response.json is not None
    data = response.json

    assert data["user_id"] == payload["user_id"]
    assert data["original_url"] == payload["original_url"]
    assert data["title"] == payload["title"]
    assert len(data["short_code"]) == 6

    url = Urls.get_or_none(Urls.short_code == data["short_code"])
    assert url is not None

    assert url.user_id == payload["user_id"]
    assert url.original_url == payload["original_url"]
    assert url.title == payload["title"]


def test_create_negative_path(client, user):
    # no json data
    response = client.post("/urls")
    assert response.status_code != 201

    # user_id that doesn't exist
    payload = {
        "user_id": 99999,
        "original_url": "https://fun.co",
        "title": "A Link",
    }
    response = client.post("/urls", json=payload)
    assert response.status_code != 201

    # invalid url
    payload = {
        "user_id": user.id,
        "original_url": "not-a-valid-url",
        "title": "A Link",
    }
    response = client.post("/urls", json=payload)
    assert response.status_code != 201

    # no title
    payload = {
        "user_id": user.id,
        "original_url": "https://fun.co",
    }
    response = client.post("/urls", json=payload)
    assert response.status_code != 201


def test_get_url_by_id_positive_path(client):
    urls = [
        {
            "user_id": 1,
            "short_code": "abc123",
            "original_url": "https://fun.co",
            "title": "A Link",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
        {
            "user_id": 2,
            "short_code": "def456",
            "original_url": "https://fun.co",
            "title": "A Link",
            "is_active": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
    ]
    ids = []
    for url in urls:
        new_url = Urls.create(**url)
        ids.append(new_url.id)

    response = client.get(f"/urls/{ids[1]}")

    assert response.status_code == 200
    assert response.json is not None
    res = response.json

    for key in res:
        # Don't worry about id
        if key == "id":
            continue

        if isinstance(urls[1][key], datetime):
            assert res[key] == datetime.isoformat(urls[1][key])
        else:
            assert res[key] == urls[1][key]


def test_get_url_by_id_negative_path(client):
    urls = [
        {
            "user_id": 1,
            "short_code": "abc123",
            "original_url": "https://fun.co",
            "title": "A Link",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
        {
            "user_id": 2,
            "short_code": "def456",
            "original_url": "https://fun.co",
            "title": "A Link",
            "is_active": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
    ]
    ids = []
    for url in urls:
        new_url = Urls.create(**url)
        ids.append(new_url.id)

    response = client.get("/urls/1234")

    assert response.status_code == 400


def test_update_url_positive_path(client):
    now = datetime.now(timezone.utc)
    url = Urls.create(
        user_id=1,
        short_code="abc123",
        original_url="https://fun.co",
        title="A Link",
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    payload = {
        "original_url": "https://example.com",
        "title": "Updated Title",
        "is_active": False,
    }
    response = client.put(f"/urls/{url.id}", json=payload)

    assert response.status_code == 200
    assert response.json is not None
    data = response.json

    assert data["id"] == url.id
    assert data["original_url"] == "https://example.com"
    assert data["title"] == "Updated Title"
    assert data["is_active"] is False

    updated_url = Urls.get_or_none(Urls.id == url.id)
    assert updated_url is not None
    assert updated_url.original_url == "https://example.com"
    assert updated_url.title == "Updated Title"
    assert updated_url.is_active is False


def test_update_url_negative_path(client):
    now = datetime.now(timezone.utc)
    url = Urls.create(
        user_id=1,
        short_code="abc123",
        original_url="https://fun.co",
        title="A Link",
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    # id does not exist
    payload = {"title": "Updated Title"}
    response = client.put("/urls/1234", json=payload)
    assert response.status_code == 400

    # No payload
    response = client.put("/urls/1234")
    assert response.status_code == 400


def test_delete_url_by_id_positive_path(client):
    urls = [
        {
            "user_id": 1,
            "short_code": "abc123",
            "original_url": "https://fun.co",
            "title": "A Link",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
        {
            "user_id": 2,
            "short_code": "def456",
            "original_url": "https://fun.co",
            "title": "A Link",
            "is_active": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
    ]
    ids = []
    for url in urls:
        new_url = Urls.create(**url)
        ids.append(new_url.id)

    response = client.delete(f"/urls/{ids[1]}")

    assert response.status_code == 200

    url = Urls.get_or_none(id=ids[1])
    assert url is None


def test_delete_url_by_id_negative_path(client):
    urls = [
        {
            "user_id": 1,
            "short_code": "abc123",
            "original_url": "https://fun.co",
            "title": "A Link",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
        {
            "user_id": 2,
            "short_code": "def456",
            "original_url": "https://fun.co",
            "title": "A Link",
            "is_active": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
    ]
    ids = []
    for url in urls:
        new_url = Urls.create(**url)
        ids.append(new_url.id)

    response = client.delete("/urls/1234")

    assert response.status_code == 400
