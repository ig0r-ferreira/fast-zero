from fastapi import FastAPI, HTTPException, status

from fast_zero.schemas import User, UserDB, UserList, UserPublic

app = FastAPI()
database = []


@app.get('/')
def get_root():
    return {'message': 'Hello World!'}


@app.post(
    '/users/', status_code=status.HTTP_201_CREATED, response_model=UserPublic
)
def create_user(user: User):
    user_with_id = UserDB(id=len(database) + 1, **user.model_dump())
    database.append(user_with_id)
    return user_with_id


@app.get('/users/', response_model=UserList)
def get_users():
    return {'users': database}


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: User):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    user_with_id = UserDB(id=user_id, **user.model_dump())
    database[user_id - 1] = user_with_id

    return user_with_id


@app.delete('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    del database[user_id - 1]
