import pytest
from sqlmodel import Session, SQLModel

from todo_app.data_access.db import Database
from todo_app.data_access.dao import TodoItemDAO, TodoListDAO
from todo_app.domain.models import TodoItem, TodoList
from todo_app.services.todo_item_service import TodoItemService
from todo_app.services.todo_list_service import TodoListService
from todo_app.ui.controllers import TodoController


@pytest.fixture(scope="function")
def database():
    db = Database("sqlite:///:memory:")
    SQLModel.metadata.create_all(db.engine)
    yield db
    SQLModel.metadata.drop_all(db.engine)


@pytest.fixture(scope="function")
def db(database):
    with Session(database.engine) as session:
        yield session


@pytest.fixture
def seeded_db(db):
    """Seed an example list with two items (one done, one not)."""
    todo_list = TodoList(name="Sample")
    todo_list.items = [
        TodoItem(title="A", done=False),
        TodoItem(title="B", done=True),
    ]
    db.add(todo_list)
    db.commit()
    db.refresh(todo_list)
    return db


@pytest.fixture
def controller(database):
    list_dao = TodoListDAO(database.engine)
    item_dao = TodoItemDAO(database.engine)
    return TodoController(
        list_service=TodoListService(list_dao=list_dao, item_dao=item_dao),
        item_service=TodoItemService(item_dao=item_dao),
    )
