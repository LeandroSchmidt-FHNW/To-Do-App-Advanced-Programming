"""Integration tests exercising controller -> services -> DAO -> DB."""

import pytest


def test_full_crud_flow_on_list_and_items(controller):
    # Create
    todo_list = controller.create_list("Groceries")
    assert todo_list.id is not None
    assert todo_list.name == "Groceries"

    # Read
    all_lists = controller.all_lists()
    assert len(all_lists) == 1

    # Update (rename)
    renamed = controller.rename_list(todo_list.id, "Weekly groceries")
    assert renamed.name == "Weekly groceries"

    # Add items
    item1 = controller.add_item(todo_list.id, "Milk")
    item2 = controller.add_item(todo_list.id, "Bread")
    items = controller.items_of(todo_list.id)
    assert [i.title for i in items] == ["Milk", "Bread"]

    # Toggle done
    toggled = controller.toggle_item(item1.id)
    assert toggled.done is True

    # Progress
    total, done = controller.list_progress(todo_list.id)
    assert (total, done) == (2, 1)

    # Update item title
    updated = controller.rename_item(item2.id, "Whole-grain bread")
    assert updated.title == "Whole-grain bread"

    # Delete item
    controller.delete_item(item1.id)
    assert len(controller.items_of(todo_list.id)) == 1

    # Delete list (cascades remaining item)
    controller.delete_list(todo_list.id)
    assert controller.all_lists() == []


def test_renaming_nonexistent_list_raises(controller):
    with pytest.raises(ValueError):
        controller.rename_list(999, "Nope")


def test_deleting_nonexistent_item_raises(controller):
    with pytest.raises(ValueError):
        controller.delete_item(999)
