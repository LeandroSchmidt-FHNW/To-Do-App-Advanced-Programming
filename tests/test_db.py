"""Database tests: schema + DAO + cascade behavior."""

from sqlmodel import select

from todo_app.data_access.dao import TodoItemDAO, TodoListDAO
from todo_app.domain.models import TodoItem, TodoList


def test_query_returns_seeded_list(seeded_db):
    lists = seeded_db.exec(select(TodoList)).all()
    assert len(lists) == 1
    assert lists[0].name == "Sample"


def test_dao_create_and_get_list(database):
    dao = TodoListDAO(database.engine)
    created = dao.create("My List")

    assert created.id is not None
    fetched = dao.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "My List"


def test_dao_create_item_and_list_for_list(database):
    list_dao = TodoListDAO(database.engine)
    item_dao = TodoItemDAO(database.engine)
    tl = list_dao.create("L")

    item_dao.create(tl.id, "Task 1")
    item_dao.create(tl.id, "Task 2")

    items = item_dao.list_for_list(tl.id)
    assert [i.title for i in items] == ["Task 1", "Task 2"]


def test_deleting_list_cascades_to_items(database):
    list_dao = TodoListDAO(database.engine)
    item_dao = TodoItemDAO(database.engine)
    tl = list_dao.create("To be deleted")
    item_dao.create(tl.id, "leftover")

    assert list_dao.delete(tl.id) is True

    # No items should remain orphaned in the database
    with item_dao.session() as session:
        remaining = list(session.exec(select(TodoItem)).all())
    assert remaining == []
