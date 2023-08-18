from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Token, UserIn, UserList, UserOut
from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI()


@app.get('/')
def get_root():
    return {'message': 'Hello World!'}


@app.post(
    '/users/', status_code=status.HTTP_201_CREATED, response_model=UserOut
)
def create_user(user: UserIn, session: Session = Depends(get_session)):
    db_user = session.scalar(select(User.username == user.username))

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username already registered',
        )

    db_user = User(
        **user.model_dump(exclude={'password'}),
        password=get_password_hash(user.password)
    )

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
    user_id: int,
    user: UserIn,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Not enough permissions',
        )

    for field, value in user.model_dump().items():
        setattr(current_user, field, value)

    session.commit()
    session.refresh(current_user)

    return current_user


@app.delete('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Not enough permissions',
        )

    session.delete(current_user)
    session.commit()


@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
