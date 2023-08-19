import pytest
from fastapi import status


def test_get_token_for_valid_user(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.raw_password},
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
def test_get_token_for_invalid_user_data(client, user, username, password):
    response = client.post(
        '/token',
        data={'username': username, 'password': password},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}
