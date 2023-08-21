import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from fast_zero.database import get_session
from fast_zero.main import app
from fast_zero.models import Base, Todo, TodoState, User
from fast_zero.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id: int = factory.Sequence(lambda n: n)
    username: str = factory.LazyAttribute(lambda obj: f'test{obj.id}')
    email: str = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password: str = factory.LazyAttribute(lambda obj: obj.username)


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    id: int = factory.Sequence(lambda n: n)
    title: str = factory.Faker('text')
    description: str = factory.Faker('text')
    state: TodoState = factory.fuzzy.FuzzyChoice(TodoState)
    user_id: int = 1


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    yield Session()

    Base.metadata.drop_all(engine)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def user(session):
    password = 'f00b@r'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    session.commit()
    session.refresh(user)

    setattr(user, 'raw_password', password)

    return user


@pytest.fixture
def other_user(session):
    password = 'f00b@r'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    session.commit()
    session.refresh(user)

    setattr(user, 'raw_password', password)

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.raw_password},
    )

    return response.json().get('access_token')


@pytest.fixture
def todo(session, user):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    session.commit()
    session.refresh(todo)

    return todo
