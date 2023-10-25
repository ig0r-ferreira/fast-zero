from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from todoapi.models import User
from todoapi.schemas import Token
from todoapi.security import (
    create_access_token,
    get_current_user,
    get_session,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def create_token_response(data):
    access_token = create_access_token(data=data)
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/token', response_model=Token)
def login_for_access_token(form_data: OAuth2Form, session: Session):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect email or password',
        )

    return create_token_response({'sub': user.email})


@router.post('/refresh_token', response_model=Token)
def refresh_access_token(user: CurrentUser):
    return create_token_response({'sub': user.email})
