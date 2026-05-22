"""DAO classes for persistence.

The rest of the application should not know about raw SQL/ORM sessions.
DAOs encapsulate CRUD operations and queries behind class-based interfaces.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from ..domain.models import TodoItem, TodoList


class BaseDAO:
    """Base class holding the SQLAlchemy/SQLModel engine."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def session(self) -> Session:
        """Create a new database session."""
        return Session(self.engine)


class TodoListDAO(BaseDAO):
    """DAO for CRUD on to-do lists."""

    def list_all(self) -> List[TodoList]:
        """Return all to-do lists sorted by creation time (newest first)."""
        with self.session() as session:
            stmt = select(TodoList).order_by(TodoList.created_at.desc())
            return list(session.exec(stmt).all())

    def get_by_id(self, list_id: int) -> Optional[TodoList]:
        """Get a single to-do list by id."""
        with self.session() as session:
            return session.get(TodoList, list_id)

    def create(self, name: str) -> TodoList:
        """Create and persist a new to-do list."""
        todo_list = TodoList(name=name)
        with self.session() as session:
            session.add(todo_list)
            session.commit()
            session.refresh(todo_list)
        return todo_list

    def rename(self, list_id: int, new_name: str) -> Optional[TodoList]:
        """Rename an existing to-do list."""
        with self.session() as session:
            todo_list = session.get(TodoList, list_id)
            if todo_list is None:
                return None
            todo_list.name = new_name
            session.add(todo_list)
            session.commit()
            session.refresh(todo_list)
            return todo_list

    def delete(self, list_id: int) -> bool:
        """Delete a to-do list (and cascade its items). Returns True if deleted."""
        with self.session() as session:
            todo_list = session.get(TodoList, list_id)
            if todo_list is None:
                return False
            session.delete(todo_list)
            session.commit()
            return True


class TodoItemDAO(BaseDAO):
    """DAO for CRUD on to-do items."""

    def list_for_list(self, list_id: int) -> List[TodoItem]:
        """Return all items of a given list (oldest first)."""
        with self.session() as session:
            stmt = (
                select(TodoItem)
                .where(TodoItem.list_id == list_id)
                .order_by(TodoItem.created_at.asc())
            )
            return list(session.exec(stmt).all())

    def get_by_id(self, item_id: int) -> Optional[TodoItem]:
        with self.session() as session:
            return session.get(TodoItem, item_id)

    def create(self, list_id: int, title: str) -> TodoItem:
        item = TodoItem(list_id=list_id, title=title, done=False)
        with self.session() as session:
            session.add(item)
            session.commit()
            session.refresh(item)
        return item

    def update_title(self, item_id: int, new_title: str) -> Optional[TodoItem]:
        with self.session() as session:
            item = session.get(TodoItem, item_id)
            if item is None:
                return None
            item.title = new_title
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    def set_done(self, item_id: int, done: bool) -> Optional[TodoItem]:
        with self.session() as session:
            item = session.get(TodoItem, item_id)
            if item is None:
                return None
            item.done = done
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    def delete(self, item_id: int) -> bool:
        with self.session() as session:
            item = session.get(TodoItem, item_id)
            if item is None:
                return False
            session.delete(item)
            session.commit()
            return True

    def count_for_list(self, list_id: int) -> tuple[int, int]:
        """Return (total_items, done_items) for a given list."""
        with self.session() as session:
            stmt = select(TodoItem).where(TodoItem.list_id == list_id)
            items = list(session.exec(stmt).all())
            return len(items), sum(1 for i in items if i.done)
