from fastapi import status


def test_get_root_should_return_200_and_hello_world(client):
    response = client.get('/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'Hello World!'}
