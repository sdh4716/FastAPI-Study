from typing import List

from fastapi import Depends, HTTPException, Body, APIRouter
from sqlalchemy.orm import Session

from database.connection import get_db
from database.orm import ToDo, User
from database.repository import ToDoRepository, UserRepository
from schema.request import CreateToDoRequest
from schema.response import ToDoListSchema, ToDoSchema
from security import get_access_token
from service.user import UserService

# uvicorn main:app

#전체 조회 api

#단일 조회 api

# java에서 update와 같음

# 삭제


# http://127.0.0.1:8000/docs
# 내가 만든 api들의 document를 자동으로 생성하여 제공, 테스트도 가능

# uvicorn main:app --reload (소스 변경이 감지되면 자동 리로드)

router = APIRouter(prefix="/todos")

@router.get("", status_code=200)
def get_todos_handler(
        access_token: str = Depends(get_access_token),
        order: str | None = None,
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends(),
        # todo_repo: ToDoRepository = Depends(ToDoRepository) 의존성을 주입받는 객체와 주입하는 객체가 같다면, Depends() 안 생략 가능
        todo_repo: ToDoRepository = Depends()
) -> ToDoListSchema:

    username: str = user_service.decode_jwt(access_token=access_token)

    user: User | None = user_repo.get_user_by_username(username=username)
    if not User:
        raise HTTPException(status_code=404, detail="User Not Found")

    todos: List[ToDo] = user.todos
    if order and order == "DESC":
        return ToDoListSchema(
        todos = [ToDoSchema.from_orm(todo) for todo in todos[::-1]]
    )
    return ToDoListSchema(
        todos = [ToDoSchema.from_orm(todo) for todo in todos]
    )


@router.get("/{todo_id}", status_code=200)
def get_todo_handler(
        todo_id: int,
        todo_repo: ToDoRepository = Depends(),
) -> ToDoSchema:
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    if todo :
        return ToDoSchema.from_orm(todo)
    raise HTTPException(status_code=404, detail="Todo Not Found")


@router.post("", status_code=201)
def create_todo_handler(
        request: CreateToDoRequest,
        todo_repo: ToDoRepository = Depends(),
) -> ToDoSchema:
    todo: ToDo = ToDo.create(request=request) # id=None, 아직 db autoIncrement로 생성 전
    todo: ToDo = todo_repo.create_todo(todo=todo) # id=DB에서 생성된 id

    return ToDoSchema.from_orm(todo)


@router.patch("/{todo_id}", status_code=200)
def update_todo_handler(
        todo_id: int,
        is_done: bool = Body(..., embed=True),
        todo_repo: ToDoRepository = Depends(),
):
    #todo_id에 해당하는 to-do가 있을 경우
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    if todo:
        #삼항연산자
        todo.done() if is_done else todo.undone()
        todo: ToDo = todo_repo.update_todo(todo=todo)
        return ToDoSchema.from_orm(todo)
        #일반 if else
        # if is_done is True:
        #     to_do.done()
        # else:
        #     to_do.undone()

    raise HTTPException(status_code=404, detail="Todo Not Found")


@router.delete("/{todo_id}", status_code=204)
def delete_todo_handler(
        todo_id: int,
        todo_repo: ToDoRepository = Depends(),
):
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    #todo_id에 해당하는 데이터가 없으면 에러 발생
    if not todo:
        raise HTTPException(status_code=404, detail="Todo Not Found")

    #있으면 삭제
    todo_repo.delete_todo(todo_id=todo_id)
