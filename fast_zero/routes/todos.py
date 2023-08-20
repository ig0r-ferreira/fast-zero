from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import Todo, User
from fast_zero.schemas import TodoIn, TodoOut
from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])
Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=TodoOut)
def create_todo(todo: TodoIn, session: Session, user: CurrentUser):
    db_todo = Todo(**todo.model_dump(), user_id=user.id)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo
