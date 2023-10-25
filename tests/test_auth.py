from fastapi import status
from freezegun import freeze_time


def test_get_token_for_existing_user(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.plain_password},
    )

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result.get('access_token')
    assert result.get('token_type', '') == 'bearer'


def test_get_token_for_inexisting_user(client):
    response = client.post(
        '/auth/token',
        data={'username': 'invalidemail@test.com', 'password': 'p@$$w0rd'},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_get_token_for_wrong_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': 'foobar@test.com', 'password': 'wrong_password'},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_refresh_token_when_the_token_is_still_valid(client, user, token):
    response = client.post(
        '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
    )

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result.get('access_token')
    assert result.get('token_type', '') == 'bearer'


def test_refresh_token_when_the_token_has_expired(client, user):
    with freeze_time('2023-08-19 18:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.plain_password},
        )

        assert response.status_code == status.HTTP_200_OK
        token = response.json().get('access_token')

    with freeze_time('2023-08-19 18:31:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
