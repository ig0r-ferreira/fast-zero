from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from todoapi.models import User
from todoapi.schemas import UserIn, UserList, UserOut
from todoapi.security import get_current_user, get_password_hash, get_session

router = APIRouter(prefix='/users', tags=['users'])
Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(user: UserIn, session: Session):
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


@router.get('/', response_model=UserList)
def get_users(session: Session, skip: int = 0, limit: int = 100):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()

    return {'users': users}


@router.put('/{user_id}', response_model=UserOut)
def update_user(
    user_id: int,
    user: UserIn,
    session: Session,
    current_user: CurrentUser,
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


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Not enough permissions',
        )

    session.delete(current_user)
    session.commit()
