"""Database seeding helpers.

Inserts one example to-do list with a couple of items on first start
so the UI is never empty for a brand-new user.
"""

from __future__ import annotations

from sqlmodel import Session

from ..domain.models import TodoItem, TodoList


class DefaultSeeder:
    """Seeds the database with an example to-do list."""

    def seed(self, session: Session) -> None:
        example = TodoList(name="Getting started")
        example.items = [
            TodoItem(title="Read the README", done=True),
            TodoItem(title="Create your first to-do list", done=False),
            TodoItem(title="Add tasks and mark them done", done=False),
        ]
        session.add(example)
