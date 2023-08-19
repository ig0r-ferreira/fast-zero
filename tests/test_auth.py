from fastapi import status
from freezegun import freeze_time


def test_get_token_for_existing_user(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.raw_password},
    )

    token = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_get_token_for_inexisting_user(client):
    response = client.post(
        '/token',
        data={'username': 'invalidemail@test.com', 'password': 'p@$$w0rd'},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_get_token_for_wrong_password(client, user):
    response = client.post(
        '/token',
        data={'username': 'foobar@test.com', 'password': 'wrong_password'},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_refresh_token(client, user, token):
    response = client.post(
        '/refresh_token', headers={'Authorization': f'Bearer {token}'}
    )

    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data.get('access_token')
    assert data.get('token_type') == 'bearer'


def test_token_expiry(client, user):
    with freeze_time('2023-08-19 18:00:00'):
        response = client.post(
            '/token',
            data={'username': user.email, 'password': user.raw_password},
        )

        assert response.status_code == status.HTTP_200_OK
        token = response.json().get('access_token')

    with freeze_time('2023-08-19 18:31:00'):
        response = client.post(
            '/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
