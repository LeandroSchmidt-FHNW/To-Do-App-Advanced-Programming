"""NiceGUI pages.

This module is object-oriented: pages are registered by a `Pages` object which
holds the controller it needs.
"""

from __future__ import annotations

from datetime import timezone
from zoneinfo import ZoneInfo

from nicegui import ui

from .controllers import TodoController


def _fmt_dt(dt) -> str:
    """Format a UTC datetime in the local Zurich timezone."""
    return (
        dt.replace(tzinfo=timezone.utc)
        .astimezone(ZoneInfo("Europe/Zurich"))
        .strftime("%d.%m.%Y %H:%M")
    )


class Pages:
    """Registers all NiceGUI routes (UI boundary)."""

    def __init__(self, controller: TodoController) -> None:
        self._controller = controller

    # ----------------------------------------------------------------- #
    # Registration
    # ----------------------------------------------------------------- #

    def register(self) -> None:
        controller = self._controller

        # =========================================================== #
        # Home page: all to-do lists
        # =========================================================== #
        @ui.page("/")
        def home_page() -> None:
            ui.markdown("# To-Do App").classes("text-primary")
            ui.label("Create to-do lists and manage tasks inside each list.").classes(
                "text-grey-7"
            )

            # --- create new list -------------------------------------- #
            with ui.card().classes("w-full max-w-2xl q-mt-md"):
                ui.label("Create a new to-do list").classes("text-h6")
                with ui.row().classes("w-full items-center"):
                    name_input = ui.input(
                        label="List name", placeholder="e.g. Groceries"
                    ).classes("flex-grow")

                    def on_create() -> None:
                        try:
                            controller.create_list(name_input.value or "")
                        except ValueError as ex:
                            ui.notify(str(ex), type="warning")
                            return
                        name_input.value = ""
                        ui.notify("List created.", type="positive")
                        refresh_lists()

                    ui.button("Create", on_click=on_create).props("color=primary")

            # --- existing lists --------------------------------------- #
            ui.markdown("## Your lists").classes("q-mt-md")
            lists_container = ui.column().classes("w-full max-w-2xl gap-2")

            def refresh_lists() -> None:
                lists_container.clear()
                lists = controller.all_lists()
                with lists_container:
                    if not lists:
                        ui.label(
                            "No lists yet. Create your first one above 👆"
                        ).classes("text-grey-7")
                        return
                    for tl in lists:
                        total, done = controller.list_progress(tl.id)
                        _render_list_card(tl, total, done)

            def _render_list_card(tl, total: int, done: int) -> None:
                with ui.card().classes("w-full"):
                    with ui.row().classes("w-full items-center justify-between"):
                        with ui.column().classes("gap-0"):
                            ui.label(tl.name).classes("text-h6")
                            ui.label(
                                f"{done}/{total} done · created {_fmt_dt(tl.created_at)}"
                            ).classes("text-caption text-grey-7")
                        with ui.row().classes("gap-2"):
                            ui.button(
                                "Open",
                                on_click=lambda lid=tl.id: ui.navigate.to(
                                    f"/list/{lid}"
                                ),
                            ).props("color=primary")
                            ui.button(
                                "Rename",
                                on_click=lambda lid=tl.id, current=tl.name: _open_rename_list_dialog(
                                    lid, current
                                ),
                            ).props("outline")
                            ui.button(
                                "Delete",
                                on_click=lambda lid=tl.id, current=tl.name: _open_delete_list_dialog(
                                    lid, current
                                ),
                            ).props("outline color=negative")

            def _open_rename_list_dialog(list_id: int, current_name: str) -> None:
                with ui.dialog() as dialog, ui.card():
                    ui.label("Rename list").classes("text-h6")
                    new_name = ui.input(label="New name", value=current_name).classes(
                        "w-80"
                    )

                    def on_save() -> None:
                        try:
                            controller.rename_list(list_id, new_name.value or "")
                        except ValueError as ex:
                            ui.notify(str(ex), type="warning")
                            return
                        dialog.close()
                        ui.notify("List renamed.", type="positive")
                        refresh_lists()

                    with ui.row().classes("justify-end w-full"):
                        ui.button("Cancel", on_click=dialog.close).props("flat")
                        ui.button("Save", on_click=on_save).props("color=primary")
                dialog.open()

            def _open_delete_list_dialog(list_id: int, current_name: str) -> None:
                with ui.dialog() as dialog, ui.card():
                    ui.label(f'Delete list "{current_name}"?').classes("text-h6")
                    ui.label("All tasks inside this list will be removed.").classes(
                        "text-grey-7"
                    )

                    def on_confirm() -> None:
                        try:
                            controller.delete_list(list_id)
                        except ValueError as ex:
                            ui.notify(str(ex), type="warning")
                            return
                        dialog.close()
                        ui.notify("List deleted.", type="positive")
                        refresh_lists()

                    with ui.row().classes("justify-end w-full"):
                        ui.button("Cancel", on_click=dialog.close).props("flat")
                        ui.button("Delete", on_click=on_confirm).props(
                            "color=negative"
                        )
                dialog.open()

            refresh_lists()

        # =========================================================== #
        # Detail page: items inside a single list
        # =========================================================== #
        @ui.page("/list/{list_id}")
        def list_detail_page(list_id: int) -> None:
            try:
                todo_list = controller.get_list(list_id)
            except ValueError:
                ui.markdown("# 🚫 List not found")
                ui.link("← Back to lists", "/")
                return

            ui.link("← Back to lists", "/").classes("q-mb-sm")
            ui.markdown(f"# {todo_list.name}")

            # --- add new item ----------------------------------------- #
            with ui.card().classes("w-full max-w-2xl"):
                ui.label("Add a task").classes("text-h6")
                with ui.row().classes("w-full items-center"):
                    title_input = ui.input(
                        label="Task", placeholder="e.g. Buy milk"
                    ).classes("flex-grow")

                    def on_add() -> None:
                        try:
                            controller.add_item(list_id, title_input.value or "")
                        except ValueError as ex:
                            ui.notify(str(ex), type="warning")
                            return
                        title_input.value = ""
                        ui.notify("Task added.", type="positive")
                        refresh_items()

                    ui.button("Add", on_click=on_add).props("color=primary")

            # --- items list ------------------------------------------- #
            items_container = ui.column().classes("w-full max-w-2xl gap-2 q-mt-md")

            def refresh_items() -> None:
                items_container.clear()
                items = controller.items_of(list_id)
                with items_container:
                    if not items:
                        ui.label("No tasks yet. Add your first task above 👆").classes(
                            "text-grey-7"
                        )
                        return
                    for it in items:
                        _render_item_card(it)

            def _render_item_card(item) -> None:
                with ui.card().classes("w-full"):
                    with ui.row().classes("w-full items-center justify-between"):
                        with ui.row().classes("items-center gap-3 flex-grow"):
                            cb = ui.checkbox(value=item.done)

                            def on_toggle(_e, iid=item.id) -> None:
                                try:
                                    controller.toggle_item(iid)
                                except ValueError as ex:
                                    ui.notify(str(ex), type="warning")
                                refresh_items()

                            cb.on("update:model-value", on_toggle)

                            label_classes = "text-body1"
                            if item.done:
                                label_classes += " text-grey-6 line-through"
                            ui.label(item.title).classes(label_classes)
                        with ui.row().classes("gap-2"):
                            ui.button(
                                "Edit",
                                on_click=lambda iid=item.id, current=item.title: _open_rename_item_dialog(
                                    iid, current
                                ),
                            ).props("outline")
                            ui.button(
                                "Delete",
                                on_click=lambda iid=item.id: _delete_item(iid),
                            ).props("outline color=negative")

            def _delete_item(item_id: int) -> None:
                try:
                    controller.delete_item(item_id)
                except ValueError as ex:
                    ui.notify(str(ex), type="warning")
                    return
                ui.notify("Task deleted.", type="positive")
                refresh_items()

            def _open_rename_item_dialog(item_id: int, current_title: str) -> None:
                with ui.dialog() as dialog, ui.card():
                    ui.label("Edit task").classes("text-h6")
                    new_title = ui.input(
                        label="Task title", value=current_title
                    ).classes("w-80")

                    def on_save() -> None:
                        try:
                            controller.rename_item(item_id, new_title.value or "")
                        except ValueError as ex:
                            ui.notify(str(ex), type="warning")
                            return
                        dialog.close()
                        ui.notify("Task updated.", type="positive")
                        refresh_items()

                    with ui.row().classes("justify-end w-full"):
                        ui.button("Cancel", on_click=dialog.close).props("flat")
                        ui.button("Save", on_click=on_save).props("color=primary")
                dialog.open()

            refresh_items()
