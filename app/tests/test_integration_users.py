from app.models.users import Users
import io

def test_integration_users_bulk_endpoint(client):
    """
    Insert specific records using the bulk endpoint and ensure they
    are properly inserted into the database
    """
    csv_content = (
        "id,username,email,created_at\n"
        "1,foo,foo@example.com,2024-01-01 00:00:00\n"
        "2343,bar,bar@example.com,2024-02-02 01:02:03"
    )
    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'users.csv')
    }
    resp = client.post(
        '/users/bulk',
        data=data,
        content_type='multipart/form-data'
    )

    assert resp.status_code == 200
    json_data = resp.get_json()
    assert isinstance(json_data, dict)
    assert json_data.get('count') == 2

    users = list(Users.select().order_by(Users.id).dicts())
    assert len(users) == 2
    assert users[0]['id'] == 1
    assert users[0]['username'] == 'foo'
    assert users[0]['email'] == 'foo@example.com'
    from datetime import datetime as _dt
    assert isinstance(users[0]['created_at'], _dt)
    assert users[1]['id'] == 2343
    assert users[1]['username'] == 'bar'
    assert users[1]['email'] == 'bar@example.com'


def test_integeation_users_full_csv(client):
    """
    Upload the fill users.csv file and ensure
    that all records are uploaded to the database.
    """
    csv_file = open("app/assets/users.csv", "r")
    csv_content = csv_file.read()
    data = {
        "file": (io.BytesIO(csv_content.encode('utf-8')), 'users.csv')
    }

    resp = client.post(
        '/users/bulk',
        data=data,
        content_type='multipart/form-data'
    )

    json_data = resp.get_json()
    assert json_data.get("count") == 400

    database_count = Users.select().count()
    assert database_count == 400

def test_list_users_no_pagination(client):
    # Seed some users
    from datetime import datetime as _dt
    Users.create(username="user1", email="u1@example.com", created_at=_dt.fromisoformat("2025-01-01T00:00:00"))
    Users.create(username="user2", email="u2@example.com", created_at=_dt.fromisoformat("2025-01-02T00:00:00"))
    Users.create(username="user3", email="u3@example.com", created_at=_dt.fromisoformat("2025-01-03T00:00:00"))

    resp = client.get("/users")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 3
    # Check first user fields
    first = data[0]
    assert first["username"] == "user1"
    assert first["email"] == "u1@example.com"
    # created_at should be ISO format
    _ = _dt.fromisoformat(first["created_at"])

def test_list_users_with_pagination(client):
    # Seed 5 users
    from datetime import datetime as _dt
    for i in range(1, 6):
        # Day part padded for two digits
        day = f"0{i}" if i < 10 else str(i)
        ts = _dt.fromisoformat(f"2025-01-{day}T00:00:00")
        Users.create(username=f"user{i}", email=f"u{i}@example.com", created_at=ts)

    # Page 1, 2 per page
    resp = client.get("/users?page=1&per_page=2")
    assert resp.status_code == 200
    paged = resp.get_json()
    assert isinstance(paged, dict)
    assert paged["page"] == 1
    assert paged["per_page"] == 2
    assert paged["total"] == 5
    assert paged["total_pages"] == 3
    assert len(paged["users"]) == 2
    assert paged["users"][0]["username"] == "user1"
    assert paged["users"][1]["username"] == "user2"

    # Page 3, 2 per page (should have one entry)
    resp = client.get("/users?page=3&per_page=2")
    assert resp.status_code == 200
    paged = resp.get_json()
    assert paged["page"] == 3
    assert len(paged["users"]) == 1
    assert paged["users"][0]["username"] == "user5"

def test_list_users_page_only(client):
    # Seed 4 users
    from datetime import datetime as _dt
    for i in range(1, 5):
        day = f"0{i}"
        ts = _dt.fromisoformat(f"2025-01-{day}T00:00:00")
        Users.create(username=f"user{i}", email=f"u{i}@example.com", created_at=ts)

    # Page specified, per_page defaults to 10
    resp = client.get("/users?page=2")
    assert resp.status_code == 200
    paged = resp.get_json()
    assert isinstance(paged, dict)
    assert paged["page"] == 2
    assert paged["per_page"] == 10
    assert paged["total"] == 4
    assert paged["total_pages"] == 1
    # No users on page 2
    assert paged["users"] == []

def test_list_users_invalid_pagination(client):
    # Non-integer values
    resp = client.get("/users?page=abc&per_page=2")
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Invalid pagination parameters"}

    resp = client.get("/users?page=1&per_page=xyz")
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Invalid pagination parameters"}

    # Zero or negative values
    resp = client.get("/users?page=0&per_page=5")
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "page and per_page must be positive integers"}

    resp = client.get("/users?page=1&per_page=0")
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "page and per_page must be positive integers"}
    
def test_get_user_by_id_success(client):
    # Create a user and retrieve it
    from datetime import datetime as _dt
    created = _dt(2025, 1, 10, 12, 30, 45)
    user = Users.create(username="alice", email="alice@example.com", created_at=created)
    resp = client.get(f"/users/{user.id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data["id"] == user.id
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert data["created_at"] == created.isoformat()

def test_get_user_by_id_not_found(client):
    # Request a non-existent user id
    resp = client.get("/users/9999")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data == {"error": "Error: user with id 9999 does not exist"}
    
def test_create_user_success(client):
    # Valid creation
    resp = client.post(
        "/users",
        json={"username": "bob", "email": "bob@example.com"}
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data["username"] == "bob"
    assert data["email"] == "bob@example.com"
    # id assigned and created_at parseable
    uid = data.get("id")
    assert isinstance(uid, int) and uid > 0
    from datetime import datetime as _dt
    _ = _dt.fromisoformat(data["created_at"])
    # Record exists in DB
    user = Users.get_or_none(Users.id == uid)
    assert user is not None

def test_create_user_missing_json(client):
    # No JSON payload
    resp = client.post("/users")
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: Json data required"}

def test_create_user_disallowed_fields(client):
    # 'id' not allowed
    resp = client.post(
        "/users",
        json={"id": 5, "username": "u", "email": "e@example.com"}
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: 'id' is not allowed"}
    # 'created_at' not allowed
    resp = client.post(
        "/users",
        json={"username": "u", "email": "e@example.com", "created_at": "2020-01-01T00:00:00"}
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: 'created_at' is not allowed"}

def test_create_user_missing_fields(client):
    # Missing username
    resp = client.post(
        "/users",
        json={"email": "e@example.com"}
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: username is required"}
    # Missing email
    resp = client.post(
        "/users",
        json={"username": "u"}
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: email is required"}

def test_create_user_invalid_types(client):
    # username wrong type
    resp = client.post(
        "/users",
        json={"username": 123, "email": "e@example.com"}
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: username must be a non-empty string"}
    # email wrong type
    resp = client.post(
        "/users",
        json={"username": "u", "email": 456}
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: email must be a non-empty string"}
    
def test_update_user_username_only(client):
    from datetime import datetime as _dt
    created = _dt(2025, 1, 1, 0, 0, 0)
    user = Users.create(username="old", email="old@example.com", created_at=created)
    resp = client.put(f"/users/{user.id}", json={"username": "new"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == user.id
    assert data["username"] == "new"
    assert data["email"] == "old@example.com"
    assert data["created_at"] == created.isoformat()
    # Verify DB
    u = Users.get_by_id(user.id)
    assert u.username == "new"
    assert u.email == "old@example.com"

def test_update_user_email_only(client):
    from datetime import datetime as _dt
    created = _dt(2025, 2, 2, 0, 0, 0)
    user = Users.create(username="old", email="old@example.com", created_at=created)
    resp = client.put(f"/users/{user.id}", json={"email": "new@example.com"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == user.id
    assert data["username"] == "old"
    assert data["email"] == "new@example.com"
    assert data["created_at"] == created.isoformat()

def test_update_user_both_fields(client):
    from datetime import datetime as _dt
    created = _dt(2025, 3, 3, 0, 0, 0)
    user = Users.create(username="old", email="old@example.com", created_at=created)
    resp = client.put(
        f"/users/{user.id}",
        json={"username": "nw", "email": "nw@example.com"}
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["username"] == "nw"
    assert data["email"] == "nw@example.com"
    assert data["created_at"] == created.isoformat()

def test_update_user_not_found(client):
    resp = client.put("/users/9999", json={"username": "x"})
    assert resp.status_code == 404
    assert resp.get_json() == {"error": "Error: user with id 9999 does not exist"}

def test_update_user_missing_json(client):
    from datetime import datetime as _dt
    # Create user to get valid id
    user = Users.create(username="old", email="old@example.com", created_at=_dt.now())
    resp = client.put(f"/users/{user.id}")
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: Json data required"}

def test_update_user_disallowed_fields(client):
    from datetime import datetime as _dt
    user = Users.create(username="old", email="old@example.com", created_at=_dt.now())
    # id not allowed
    resp = client.put(
        f"/users/{user.id}",
        json={"id": 5}
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: 'id' is not allowed"}
    # created_at not allowed
    resp = client.put(
        f"/users/{user.id}",
        json={"created_at": "2020-01-01T00:00:00"}
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: 'created_at' is not allowed"}

def test_update_user_invalid_types_and_blank(client):
    from datetime import datetime as _dt
    created = _dt(2025, 4, 4, 0, 0, 0)
    user = Users.create(username="old", email="old@example.com", created_at=created)
    # username wrong type
    resp = client.put(
        f"/users/{user.id}",
        json={"username": 123}
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: username must be a non-empty string"}
    # username blank
    resp = client.put(
        f"/users/{user.id}",
        json={"username": ""}
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: username must be a non-empty string"}
    # email wrong type
    resp = client.put(
        f"/users/{user.id}",
        json={"email": 456}
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: email must be a non-empty string"}
    # email blank
    resp = client.put(
        f"/users/{user.id}",
        json={"email": ""}
    )
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: email must be a non-empty string"}

def test_update_user_no_fields(client):
    from datetime import datetime as _dt
    user = Users.create(username="old", email="old@example.com", created_at=_dt.now())
    resp = client.put(f"/users/{user.id}", json={})
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Error: username or email required"}
    
def test_delete_user_success(client):
    # Create and then delete a user
    from datetime import datetime as _dt
    created = _dt(2025, 5, 5, 12, 34, 56)
    user = Users.create(username="deluser", email="del@example.com", created_at=created)
    resp = client.delete(f"/users/{user.id}")
    assert resp.status_code == 200
    data = resp.get_json()
    # Response should match deleted user
    assert data == {
        "id": user.id,
        "username": "deluser",
        "email": "del@example.com",
        "created_at": created.isoformat()
    }
    # Ensure user is removed from DB
    assert Users.get_or_none(Users.id == user.id) is None

def test_delete_user_not_found(client):
    # Attempt to delete non-existent user
    resp = client.delete("/users/9999")
    assert resp.status_code == 404
    assert resp.get_json() == {"error": "Error: user with id 9999 does not exist"}

def test_create_user_after_bulk_import_unique_id(client):
    # Bulk-import users with high IDs, then create a new user and ensure the ID is max+1
    csv_content = (
        "id,username,email,created_at\n"
        "100,u100,u100@example.com,2025-01-01 00:00:00\n"
        "200,u200,u200@example.com,2025-02-02 00:00:00"
    )
    data = {'file': (io.BytesIO(csv_content.encode('utf-8')), 'users.csv')}
    resp = client.post(
        '/users/bulk', data=data,
        content_type='multipart/form-data'
    )
    assert resp.status_code == 200
    assert resp.get_json().get('count') == 2
    # Two users in DB
    assert Users.select().count() == 2

    # Create a new user; expect ID = 200 + 1 = 201
    resp2 = client.post(
        "/users",
        json={"username": "newu", "email": "newu@example.com"}
    )
    assert resp2.status_code == 201
    data2 = resp2.get_json()
    assert data2['id'] == 201
    assert data2['username'] == 'newu'
    assert data2['email'] == 'newu@example.com'
    # created_at is valid ISO datetime
    from datetime import datetime as _dt
    _ = _dt.fromisoformat(data2['created_at'])
    # DB now has 3 users, including the new one
    assert Users.select().count() == 3
    u = Users.get_by_id(201)
    assert u.username == 'newu'
    assert u.email == 'newu@example.com'
