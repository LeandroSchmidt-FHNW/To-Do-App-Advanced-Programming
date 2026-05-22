"""Domain and ORM models.

We use SQLModel (SQLAlchemy + Pydantic) to map domain objects to a SQLite database.

Tables:
- TodoList: a named to-do list (a "to-do file")
- TodoItem: a single task belonging to a TodoList
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


class TodoList(SQLModel, table=True):
    """A named to-do list owning many items."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=1, max_length=80)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), index=True
    )

    items: List["TodoItem"] = Relationship(
        back_populates="todo_list",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class TodoItem(SQLModel, table=True):
    """A single to-do task within a TodoList."""

    id: Optional[int] = Field(default=None, primary_key=True)
    list_id: int = Field(foreign_key="todolist.id", index=True)

    title: str = Field(min_length=1, max_length=200)
    done: bool = Field(default=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), index=True
    )

    todo_list: "TodoList" = Relationship(back_populates="items")
