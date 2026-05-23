"""UI controllers.

Controllers coordinate between the UI layer (NiceGUI pages) and the services.
They do *not* import NiceGUI so they remain easy to unit-test.
"""

from __future__ import annotations

from typing import List

from ..domain.models import TodoItem, TodoList
from ..services.todo_item_service import TodoItemService
from ..services.todo_list_service import TodoListService


class TodoController:
    """Single controller for the to-do app (lists + items)."""

    def __init__(
        self,
        list_service: TodoListService,
        item_service: TodoItemService,
    ) -> None:
        self.list_service = list_service
        self.item_service = item_service

    # ---- Lists --------------------------------------------------------- #

    def all_lists(self) -> List[TodoList]:
        return self.list_service.list_all()

    def get_list(self, list_id: int) -> TodoList:
        todo_list = self.list_service.get(list_id)
        if todo_list is None:
            raise ValueError(f"To-do list #{list_id} not found.")
        return todo_list

    def create_list(self, name: str) -> TodoList:
        return self.list_service.create(name)

    def rename_list(self, list_id: int, new_name: str) -> TodoList:
        return self.list_service.rename(list_id, new_name)

    def delete_list(self, list_id: int) -> None:
        self.list_service.delete(list_id)

    def list_progress(self, list_id: int) -> tuple[int, int]:
        return self.list_service.progress(list_id)

    # ---- Items --------------------------------------------------------- #

    def items_of(self, list_id: int) -> List[TodoItem]:
        return self.item_service.list_for_list(list_id)

    def add_item(self, list_id: int, title: str) -> TodoItem:
        return self.item_service.add(list_id, title)

    def rename_item(self, item_id: int, new_title: str) -> TodoItem:
        return self.item_service.rename(item_id, new_title)

    def toggle_item(self, item_id: int) -> TodoItem:
        return self.item_service.toggle(item_id)

    def set_item_done(self, item_id: int, done: bool) -> TodoItem:
        return self.item_service.set_done(item_id, done)

    def delete_item(self, item_id: int) -> None:
        self.item_service.delete(item_id)
