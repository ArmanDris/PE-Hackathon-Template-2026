from datetime import datetime
from app.routes.users import validate_user

def test_validate_user():
    # Valid row: all required fields as strings
    row = {
        'id': '1',
        'username': 'john',
        'email': 'john@example.com',
        'created_at': '2024-01-01 00:00:00'
    }
    assert validate_user(row) is True

    # Missing created_at should be invalid
    row2 = {
        'username': 'jane',
        'email': 'jane@example.com'
    }
    assert validate_user(row2) is False

    # Bad timestamp format should be invalid
    row3 = {
        'username': 'jane',
        'email': 'jane@example.com',
        'created_at': 'not-a-date'
    }
    assert validate_user(row3) is False

    # Extra fields beyond the model are ignored, but required fields valid
    row4 = {
        'foo': 'bar',
        'username': 'x',
        'email': 'x@x.com',
        'created_at': '2024-01-01 00:00:00'
    }
    assert validate_user(row4) is True

    # Accept datetime object for created_at
    row5 = {
        'username': 'alice',
        'email': 'alice@example.com',
        'created_at': datetime(2024, 2, 2, 2, 2, 2)
    }
    assert validate_user(row5) is True

def test_integration_users_bulk_endpoint():
    import os
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    import io
    from app import create_app
    from app.models.users import Users

    app = create_app()
    client = app.test_client()
    with app.app_context():
        from app.database import db
        db.create_tables([Users])
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
