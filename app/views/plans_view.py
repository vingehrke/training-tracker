import flet as ft
from ..db.database import get_session
from ..services import plan_service, exercise_service
from .utils import show_snack


def build(page: ft.Page, on_start_workout=None) -> ft.Control:
    db = get_session()

    # --- state ---
    view_stack: list[ft.Control] = []
    root_column = ft.Column(expand=True)

    # ── Plan List ────────────────────────────────────────────────────────────

    def show_plan_list():
        plan_name_field = ft.TextField(label="Neuer Plan", expand=True, autofocus=False)
        plan_desc_field = ft.TextField(label="Beschreibung (optional)", expand=True)
        plan_list = ft.ListView(expand=True, spacing=4)

        def refresh():
            plan_list.controls.clear()
            for plan in plan_service.get_all(db):
                ex_count = len(plan.plan_exercises)
                plan_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(plan.name),
                        subtitle=ft.Text(f"{ex_count} Übung{'en' if ex_count != 1 else ''}"),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                        on_click=lambda e, pid=plan.id: show_plan_detail(pid),
                    )
                )
            page.update()

        def create_plan(e):
            name = plan_name_field.value.strip()
            if not name:
                show_snack(page, "Name darf nicht leer sein.", error=True)
                return
            plan_service.create(db, name=name, description=plan_desc_field.value.strip() or None)
            plan_name_field.value = ""
            plan_desc_field.value = ""
            refresh()

        refresh()

        view = ft.Column(
            expand=True,
            controls=[
                ft.Text("Trainingspläne", size=22, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row([plan_name_field, plan_desc_field]),
                ft.FilledButton("Plan erstellen", icon=ft.Icons.ADD, on_click=create_plan),
                ft.Divider(),
                plan_list,
            ],
        )
        _set_view(view)

    # ── Plan Detail ──────────────────────────────────────────────────────────

    def show_plan_detail(plan_id: int):
        plan = plan_service.get_by_id(db, plan_id)
        if not plan:
            return

        ex_list = ft.ListView(expand=False, spacing=4)

        def refresh_exercises():
            plan_db = plan_service.get_by_id(db, plan_id)
            ex_list.controls.clear()
            for pe in plan_db.plan_exercises:
                wtype = "kg" if pe.exercise.weight_type.value == "kg" else "Stufen"
                ex_list.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.FITNESS_CENTER, size=20),
                        title=ft.Text(pe.exercise.name),
                        subtitle=ft.Text(wtype),
                        trailing=ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ft.Colors.ERROR,
                            on_click=lambda e, peid=pe.id: remove_exercise(peid),
                        ),
                    )
                )
            page.update()

        def remove_exercise(pe_id: int):
            plan_service.remove_exercise(db, pe_id)
            refresh_exercises()

        def delete_plan(e):
            plan_service.delete(db, plan_id)
            show_plan_list()

        # ── Übung hinzufügen ────────────────────────────────────────────────
        all_exercises = exercise_service.get_all(db)
        ex_options = [ft.dropdown.Option(key=str(ex.id), text=ex.name) for ex in all_exercises]

        ex_dropdown = ft.Dropdown(
            label="Übung wählen",
            options=ex_options,
            expand=True,
        )
        def add_exercise(e):
            if not ex_dropdown.value:
                show_snack(page, "Bitte eine Übung wählen.", error=True)
                return
            plan_service.add_exercise(db, plan_id, int(ex_dropdown.value))
            ex_dropdown.value = None
            refresh_exercises()

        refresh_exercises()

        view = ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_plan_list()),
                        ft.Text(plan.name, size=20, weight=ft.FontWeight.BOLD, expand=True),
                    ]
                ),
                ft.Divider(),
                ft.FilledButton(
                    "Training starten",
                    icon=ft.Icons.PLAY_ARROW,
                    on_click=lambda e: on_start_workout(plan_id) if on_start_workout else None,
                ),
                ft.Divider(),
                ft.Text("Übungen im Plan", weight=ft.FontWeight.W_600),
                ex_list,
                ft.Divider(),
                ft.Text("Übung hinzufügen", weight=ft.FontWeight.W_600),
                ft.Row([ex_dropdown, ft.FilledButton("Hinzufügen", icon=ft.Icons.ADD, on_click=add_exercise)]),
                ft.Divider(),
                ft.OutlinedButton(
                    "Plan löschen",
                    icon=ft.Icons.DELETE,
                    style=ft.ButtonStyle(color=ft.Colors.ERROR),
                    on_click=delete_plan,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        _set_view(view)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _set_view(view: ft.Control):
        root_column.controls.clear()
        root_column.controls.append(view)
        page.update()

    show_plan_list()
    return root_column
