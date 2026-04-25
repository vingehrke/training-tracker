import flet as ft
from ..db.database import get_session
from ..db.models import WeightType
from ..services import exercise_service
from .utils import show_snack


def build(page: ft.Page) -> ft.Control:
    db = get_session()

    name_field = ft.TextField(label="Name", expand=True)
    muscle_field = ft.TextField(label="Muskelgruppe (optional)", expand=True)
    weight_type_radio = ft.RadioGroup(
        value="kg",
        content=ft.Row([
            ft.Radio(value="kg", label="Hantel / Scheiben (kg)"),
            ft.Radio(value="level", label="Maschine (Stufen)"),
        ]),
    )

    exercise_list = ft.ListView(expand=True, spacing=4)

    def refresh_list():
        exercise_list.controls.clear()
        for ex in exercise_service.get_all(db):
            weight_label = "kg" if ex.weight_type == WeightType.KG else "Stufen"
            muscle = f" · {ex.muscle_group}" if ex.muscle_group else ""
            exercise_list.controls.append(
                ft.ListTile(
                    title=ft.Text(ex.name),
                    subtitle=ft.Text(f"{weight_label}{muscle}"),
                    trailing=ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.ERROR,
                        on_click=lambda e, eid=ex.id: delete_exercise(eid),
                    ),
                )
            )
        page.update()

    def add_exercise(e):
        name = name_field.value.strip()
        if not name:
            show_snack(page, "Name darf nicht leer sein.", error=True)
            return
        wtype = WeightType.KG if weight_type_radio.value == "kg" else WeightType.LEVEL
        exercise_service.create(db, name=name, weight_type=wtype, muscle_group=muscle_field.value.strip() or None)
        name_field.value = ""
        muscle_field.value = ""
        refresh_list()

    def delete_exercise(exercise_id: int):
        exercise_service.delete(db, exercise_id)
        refresh_list()

    refresh_list()

    return ft.Column(
        expand=True,
        controls=[
            ft.Text("Übungen", size=22, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([name_field, muscle_field]),
            weight_type_radio,
            ft.FilledButton("Übung hinzufügen", icon=ft.Icons.ADD, on_click=add_exercise),
            ft.Divider(),
            exercise_list,
        ],
        scroll=ft.ScrollMode.AUTO,
    )
