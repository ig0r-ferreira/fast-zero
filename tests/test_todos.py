from fastapi import status

from fast_zero.models import TodoState
from tests.conftest import TodoFactory


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


def test_list_todos(session, client, user, token):
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json().get('todos', [])) == 5


def test_list_todos_by_pagination(session, client, user, token):
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json().get('todos', [])) == 2


def test_list_todos_filtering_by_title(session, client, user, token):
    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=user.id, title='Cycling')
    )
    session.commit()

    response = client.get(
        '/todos/?title=Cycling',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json().get('todos', [])) == 5


def test_list_todos_filtering_by_description(session, client, user, token):
    session.bulk_save_objects(
        TodoFactory.create_batch(3, user_id=user.id, description='description')
    )
    session.commit()

    response = client.get(
        '/todos/?description=description',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json().get('todos', [])) == 3


def test_list_todos_filtering_by_state(session, client, user, token):
    session.bulk_save_objects(
        TodoFactory.create_batch(10, user_id=user.id, state=TodoState.todo)
    )
    session.commit()

    response = client.get(
        '/todos/?state=todo',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json().get('todos', [])) == 10


def test_list_todos_using_combined_filters(session, user, client, token):
    session.bulk_save_objects(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Title 1',
            description='example',
            state=TodoState.done,
        )
    )

    session.bulk_save_objects(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Title 2',
            description='example',
            state=TodoState.todo,
        )
    )
    session.commit()

    response = client.get(
        '/todos/?title=Title&description=example&state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == 5
