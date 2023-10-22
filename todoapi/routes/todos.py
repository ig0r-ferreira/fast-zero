from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from todoapi.database import get_session
from todoapi.models import Todo, User
from todoapi.schemas import PartialTodo, TodoIn, TodoList, TodoOut
from todoapi.security import get_current_user

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


@router.get('/', response_model=TodoList)
def list_todos(
    session: Session,
    user: CurrentUser,
    title: str = Query(None),
    description: str = Query(None),
    state: str = Query(None),
    skip: int = 0,
    limit: int = 100,
):
    query = select(Todo).where(Todo.user_id == user.id)

    if title:
        query = query.filter(Todo.title.contains(title))

    if description:
        query = query.filter(Todo.description.contains(description))

    if state:
        query = query.filter(Todo.state == state)

    todos = session.scalars(query.offset(skip).limit(limit)).all()

    return {'todos': todos}


@router.patch('/{todo_id}', response_model=TodoOut)
def update_todo(
    todo_id: int, todo: PartialTodo, session: Session, user: CurrentUser
):
    stored_todo = session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    )

    if not stored_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Task not found.'
        )

    for field, value in todo.model_dump(exclude_unset=True).items():
        setattr(stored_todo, field, value)

    session.add(stored_todo)
    session.commit()
    session.refresh(stored_todo)

    return stored_todo


@router.delete('/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, session: Session, user: CurrentUser):
    stored_todo = session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    )

    if not stored_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Task not found.'
        )

    session.delete(stored_todo)
    session.commit()
