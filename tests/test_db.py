from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.models import User


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
