from database.orm import ToDo, User
from database.repository import ToDoRepository, UserRepository
from service.user import UserService


def test_get_todos(client, mocker):
    access_token: str = UserService().create_jwt(username="test")
    headers = {"Authorization": f"Bearer {access_token}"}

    # order = ASC 검증
    # mocking : 실제 함수를 동작하는게 아니라 함수가 동작한 것처럼 속이겠다.
    user = User(id=1, username="test", password="hashed")
    user.todos = [
        ToDo(id=1, contents="FastAPI Section 0", is_done=True),
        ToDo(id=2, contents="FastAPI Section 1", is_done=False)
    ]

    mocker.patch.object(
        UserRepository, "get_user_by_username", return_value=user
    )

    response = client.get("/todos", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
            {"id": 2, "contents": "FastAPI Section 1", "is_done": False},
        ]
    }

    # order = DSESC 검증
    response = client.get("/todos?order=DESC", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {"id": 2, "contents": "FastAPI Section 1", "is_done": False},
            {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
        ]
    }

def test_get_todo(client, mocker):
    #200
    mocker.patch.object(ToDoRepository,
        "get_todo_by_todo_id",
        return_value=ToDo(id=1, contents="todo", is_done=True),
    )

    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "contents": "todo", "is_done": True}

    #404
    mocker.patch.object(ToDoRepository, "get_todo_by_todo_id",return_value=None,)

    response = client.get("/todos/1")
    assert response.status_code == 404
    assert response.json() == {"detail" : "Todo Not Found"}

def test_create_todo(client, mocker):

    #create_todo_handler의 create 매서드의 결과를 훔쳐온다.
    create_spy = mocker.spy(ToDo, "create")
    mocker.patch.object(ToDoRepository,
        "create_todo",
        return_value=ToDo(id=1, contents="todo", is_done=True),
    )

    # CreateToDoRequest와 맞춰서
    body = {
        "contents": "test",
        "is_done": False,
    }
    response = client.post("/todos", json=body)

    assert create_spy.spy_return.id is None
    assert create_spy.spy_return.contents == "test"
    assert create_spy.spy_return.is_done is False

    assert response.status_code == 201
    assert response.json() == {"id": 1, "contents": "todo", "is_done": True}

def test_update_todo(client, mocker):
    # 200
    mocker.patch.object(ToDoRepository,
        "get_todo_by_todo_id",
        return_value=ToDo(id=1, contents="todo", is_done=True),
    )

    # update_todo_handler의 done, undone중 어떤 것이 호출되었는지 검증
    undone = mocker.patch.object(ToDo, "undone")
    mocker.patch.object(ToDoRepository,
        "update_todo",
        return_value=ToDo(id=1, contents="todo", is_done=False),
    )
    response = client.patch("/todos/1", json={"is_done": False})

    # undone이 한번이라도 호출되어야 넘어감
    undone.assert_called_once_with()

    assert response.status_code == 200
    assert response.json() == {"id": 1, "contents": "todo", "is_done": False}

    # 404
    mocker.patch.object(ToDoRepository,"get_todo_by_todo_id", return_value=None)

    response = client.patch("/todos/1", json={"is_done": True})
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo Not Found"}

def test_delete_todo(client, mocker):
    #204
    mocker.patch.object(ToDoRepository,
        "get_todo_by_todo_id",
        return_value=ToDo(id=1, contents="todo", is_done=True),
    )
    mocker.patch.object(ToDoRepository, "delete_todo")

    response = client.delete("/todos/1")
    assert response.status_code == 204

    #404
    mocker.patch.object(ToDoRepository, "get_todo_by_todo_id", return_value=None,)

    response = client.delete("/todos/1")
    assert response.status_code == 404
    assert response.json() == {"detail" : "Todo Not Found"}