from sqlalchemy import select
from sqlalchemy.orm import Session

from todoapi.models import Todo, User


def test_create_user(session: Session):
    new_user = User(
        username='alice', password='secret', email='alice@test.com'
    )
    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.username == 'alice'))

    assert user is not None
    assert user.password == 'secret'
    assert user.email == 'alice@test.com'


def test_create_todo(session: Session, user: User):
    todo = Todo(
        title='Todo', description='description', state='draft', user_id=user.id
    )

    session.add(todo)
    session.commit()
    session.refresh(todo)

    user_db = session.scalar(select(User).where(User.id == user.id))

    assert user_db is not None
    assert todo in user.todos
