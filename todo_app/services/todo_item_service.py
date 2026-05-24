"""Business logic for to-do items (CRUD + validation + done-toggle)."""

from __future__ import annotations

from typing import List

from ..data_access.dao import TodoItemDAO
from ..domain.models import TodoItem

MAX_TITLE_LENGTH = 200


class TodoItemService:
    """Application logic around `TodoItem`."""

    def __init__(self, item_dao: TodoItemDAO) -> None:
        self.item_dao = item_dao

    # ---- validation ---------------------------------------------------- #

    @staticmethod
    def _validate_title(title: str) -> str:
        if title is None:
            raise ValueError("Task title is required.")
        cleaned = title.strip()
        if not cleaned:
            raise ValueError("Task title must not be empty.")
        if len(cleaned) > MAX_TITLE_LENGTH:
            raise ValueError(
                f"Task title must be at most {MAX_TITLE_LENGTH} characters."
            )
        return cleaned

    # ---- CRUD ---------------------------------------------------------- #

    def list_for_list(self, list_id: int) -> List[TodoItem]:
        return self.item_dao.list_for_list(list_id)

    def add(self, list_id: int, title: str) -> TodoItem:
        cleaned = self._validate_title(title)
        return self.item_dao.create(list_id, cleaned)

    def rename(self, item_id: int, new_title: str) -> TodoItem:
        cleaned = self._validate_title(new_title)
        updated = self.item_dao.update_title(item_id, cleaned)
        if updated is None:
            raise ValueError(f"To-do item #{item_id} not found.")
        return updated

    def set_done(self, item_id: int, done: bool) -> TodoItem:
        updated = self.item_dao.set_done(item_id, done)
        if updated is None:
            raise ValueError(f"To-do item #{item_id} not found.")
        return updated

    def toggle(self, item_id: int) -> TodoItem:
        current = self.item_dao.get_by_id(item_id)
        if current is None:
            raise ValueError(f"To-do item #{item_id} not found.")
        return self.set_done(item_id, not current.done)

    def delete(self, item_id: int) -> None:
        if not self.item_dao.delete(item_id):
            raise ValueError(f"To-do item #{item_id} not found.")
