"""Business logic for to-do lists (CRUD + validation)."""

from __future__ import annotations

from typing import List, Optional

from ..data_access.dao import TodoItemDAO, TodoListDAO
from ..domain.models import TodoList

MAX_NAME_LENGTH = 80


class TodoListService:
    """Application logic around `TodoList`."""

    def __init__(self, list_dao: TodoListDAO, item_dao: TodoItemDAO) -> None:
        self.list_dao = list_dao
        self.item_dao = item_dao

    # ---- validation ---------------------------------------------------- #

    @staticmethod
    def _validate_name(name: str) -> str:
        if name is None:
            raise ValueError("List name is required.")
        cleaned = name.strip()
        if not cleaned:
            raise ValueError("List name must not be empty.")
        if len(cleaned) > MAX_NAME_LENGTH:
            raise ValueError(f"List name must be at most {MAX_NAME_LENGTH} characters.")
        return cleaned

    # ---- CRUD ---------------------------------------------------------- #

    def list_all(self) -> List[TodoList]:
        return self.list_dao.list_all()

    def get(self, list_id: int) -> Optional[TodoList]:
        return self.list_dao.get_by_id(list_id)

    def create(self, name: str) -> TodoList:
        cleaned = self._validate_name(name)
        return self.list_dao.create(cleaned)

    def rename(self, list_id: int, new_name: str) -> TodoList:
        cleaned = self._validate_name(new_name)
        updated = self.list_dao.rename(list_id, cleaned)
        if updated is None:
            raise ValueError(f"To-do list #{list_id} not found.")
        return updated

    def delete(self, list_id: int) -> None:
        if not self.list_dao.delete(list_id):
            raise ValueError(f"To-do list #{list_id} not found.")

    # ---- summary ------------------------------------------------------- #

    def progress(self, list_id: int) -> tuple[int, int]:
        """Return (total_items, done_items) for a given list."""
        return self.item_dao.count_for_list(list_id)
