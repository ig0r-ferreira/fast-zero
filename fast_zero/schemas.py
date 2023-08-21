from pydantic import BaseModel, ConfigDict, EmailStr

from fast_zero.models import TodoState


class UserIn(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserOut]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class TodoIn(BaseModel):
    title: str
    description: str
    state: TodoState


class TodoOut(BaseModel):
    id: int
    title: str
    description: str
    state: TodoState


class TodoList(BaseModel):
    todos: list[TodoOut]


class PartialTodo(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
