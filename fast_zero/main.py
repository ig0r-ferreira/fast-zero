from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import UserIn, UserList, UserOut

app = FastAPI()


@app.get('/')
def get_root():
    return {'message': 'Hello World!'}


@app.post(
    '/users/', status_code=status.HTTP_201_CREATED, response_model=UserOut
)
def create_user(user: UserIn, session: Session = Depends(get_session)):
    db_user = session.scalar(select(User.name == user.name))

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username already registered',
        )

    db_user = User(name=user.name, password=user.password, email=user.email)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', response_model=UserList)
def get_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()

    return {'users': users}


@app.put('/users/{user_id}', response_model=UserOut)
def update_user(
    user_id: int, user: UserIn, session: Session = Depends(get_session)
):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    db_user.name = user.name
    db_user.password = user.password
    db_user.email = user.email

    session.commit()
    session.refresh(db_user)

    return db_user


@app.delete('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    session.delete(db_user)
    session.commit()
