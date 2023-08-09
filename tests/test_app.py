from fastapi import status


def test_get_root_should_return_200_and_hello_world(client):
    response = client.get('/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'Hello World!'}


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'name': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'id': 1,
        'name': 'alice',
        'email': 'alice@example.com',
    }


def test_get_users(client):
    response = client.get('/users/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'name': 'alice',
                'email': 'alice@example.com',
            }
        ]
    }


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'name': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id': 1,
        'name': 'bob',
        'email': 'bob@example.com',
    }


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == status.HTTP_204_NO_CONTENT
