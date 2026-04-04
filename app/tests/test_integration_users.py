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
