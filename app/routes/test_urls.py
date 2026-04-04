from datetime import datetime, timezone

import pytest

from app.models.urls import Urls


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
