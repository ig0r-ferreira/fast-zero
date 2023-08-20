from fastapi import status


def test_create_todo(client, token):
    response = client.post(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'test', 'description': 'test', 'state': 'draft'},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'id': 1,
        'title': 'test',
        'description': 'test',
        'state': 'draft',
    }
