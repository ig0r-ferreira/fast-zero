import pytest
from fastapi import status

from fast_zero.schemas import UserOut


def test_get_root_should_return_200_and_hello_world(client):
    response = client.get('/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'Hello World!'}


def test_create_new_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
    }


def test_create_user_that_already_exists(client, new_user):
    response = client.post(
        '/users/',
        json={
            'username': new_user.username,
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Username already registered'}


def test_get_users_when_database_is_empty(client):
    response = client.get('/users/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'users': []}


def test_get_users_when_database_is_not_empty(client, new_user):
    user = UserOut.model_validate(new_user).model_dump()

    response = client.get('/users/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'users': [user]}


def test_update_existing_user(client, new_user, token):
    response = client.put(
        f'/users/{new_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id': 1,
        'username': 'bob',
        'email': 'bob@example.com',
    }


def test_update_another_user(client, token):
    response = client.put(
        '/users/2',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_existing_user(client, new_user, token):
    response = client.delete(
        f'/users/{new_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_another_user(client, token):
    response = client.delete(
        '/users/2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Not enough permissions'}


def test_get_token_for_valid_user(client, new_user):
    response = client.post(
        '/token',
        data={'username': new_user.email, 'password': new_user.raw_password},
    )

    token = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert 'access_token' in token
    assert 'token_type' in token


@pytest.mark.parametrize(
    'username, password',
    [
        ('invalidemail@test.com', 'p@$$w0rd'),
        ('foobar@test.com', 'incorrectpassword'),
    ],
)
def test_get_token_for_invalid_user_data(client, new_user, username, password):
    response = client.post(
        '/token',
        data={'username': username, 'password': password},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}
