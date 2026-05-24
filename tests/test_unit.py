"""Unit tests for service-layer validation and pure business logic."""

import pytest

from todo_app.data_access.dao import TodoItemDAO, TodoListDAO
from todo_app.services.todo_item_service import TodoItemService
from todo_app.services.todo_list_service import TodoListService


def test_list_name_must_not_be_empty(database):
    service = TodoListService(
        list_dao=TodoListDAO(database.engine),
        item_dao=TodoItemDAO(database.engine),
    )
    with pytest.raises(ValueError):
        service.create("   ")


def test_list_name_too_long_is_rejected(database):
    service = TodoListService(
        list_dao=TodoListDAO(database.engine),
        item_dao=TodoItemDAO(database.engine),
    )
    with pytest.raises(ValueError):
        service.create("x" * 81)


def test_list_name_is_trimmed(database):
    service = TodoListService(
        list_dao=TodoListDAO(database.engine),
        item_dao=TodoItemDAO(database.engine),
    )
    todo_list = service.create("  Groceries  ")
    assert todo_list.name == "Groceries"


def test_item_title_must_not_be_empty(database):
    item_service = TodoItemService(item_dao=TodoItemDAO(database.engine))
    list_service = TodoListService(
        list_dao=TodoListDAO(database.engine),
        item_dao=TodoItemDAO(database.engine),
    )
    todo_list = list_service.create("L")
    with pytest.raises(ValueError):
        item_service.add(todo_list.id, "")


def test_item_title_too_long_is_rejected(database):
    item_service = TodoItemService(item_dao=TodoItemDAO(database.engine))
    list_service = TodoListService(
        list_dao=TodoListDAO(database.engine),
        item_dao=TodoItemDAO(database.engine),
    )
    todo_list = list_service.create("L")
    with pytest.raises(ValueError):
        item_service.add(todo_list.id, "x" * 201)


def test_toggle_inverts_done_flag(database):
    item_service = TodoItemService(item_dao=TodoItemDAO(database.engine))
    list_service = TodoListService(
        list_dao=TodoListDAO(database.engine),
        item_dao=TodoItemDAO(database.engine),
    )
    todo_list = list_service.create("L")
    item = item_service.add(todo_list.id, "Buy milk")

    assert item.done is False
    toggled = item_service.toggle(item.id)
    assert toggled.done is True
    toggled_again = item_service.toggle(item.id)
    assert toggled_again.done is False
