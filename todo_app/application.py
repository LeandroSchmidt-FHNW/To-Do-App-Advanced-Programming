"""NiceGUI app wiring (views + controllers).

Object-oriented entrypoint: `TodoApplication` wires dependencies and runs NiceGUI.
"""

from __future__ import annotations

from typing import Optional

from nicegui import ui

from .data_access.db import Database
from .data_access.dao import TodoItemDAO, TodoListDAO
from .services.todo_list_service import TodoListService
from .services.todo_item_service import TodoItemService
from .ui.controllers import TodoController
from .ui.pages import Pages


class TodoApplication:
    """Application composition root."""

    def __init__(self, database: Optional[Database] = None) -> None:
        self.database = database or Database()
        self.database.init_schema_and_seed()
        engine = self.database.engine

        # Data access layer
        self.list_dao = TodoListDAO(engine)
        self.item_dao = TodoItemDAO(engine)

        # Service layer
        self.list_service = TodoListService(list_dao=self.list_dao, item_dao=self.item_dao)
        self.item_service = TodoItemService(item_dao=self.item_dao)

        # Controllers + Pages (UI layer)
        self.controller = TodoController(
            list_service=self.list_service,
            item_service=self.item_service,
        )
        self.pages = Pages(controller=self.controller)

    def run(self, host: str = "0.0.0.0", port: int = 8080, reload: bool = False) -> None:
        """Run the NiceGUI application."""
        self.pages.register()
        ui.run(host=host, port=port, reload=reload, title="To-Do App")
