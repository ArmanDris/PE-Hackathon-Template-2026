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
