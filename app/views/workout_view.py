import flet as ft
from ..db.database import get_session
from ..db.models import WeightType
from ..services import plan_service, session_service
from .utils import show_snack


def build(page: ft.Page, plan_id: int, on_finish=None) -> ft.Control:
    db = get_session()
    plan = plan_service.get_by_id(db, plan_id)
    if not plan:
        return ft.Text("Plan nicht gefunden.")

    workout_session = session_service.start_session(db, plan_id)

    exercises_column = ft.Column(spacing=10, expand=True)

    def build_exercise_card(pe) -> ft.Card:
        exercise = pe.exercise
        is_kg = exercise.weight_type == WeightType.KG
        unit = "kg" if is_kg else "Stufe"

        last_sets = session_service.get_last_sets(db, exercise.id)

        def last_weight() -> str:
            if not last_sets:
                return ""
            val = last_sets[-1].weight_kg if is_kg else last_sets[-1].weight_level
            return str(val) if val is not None else ""

        logged_column = ft.Column(spacing=4)
        input_rows = ft.Column(spacing=6)

        card_content = ft.Column(spacing=8)
        card = ft.Card(content=ft.Container(content=card_content, padding=ft.padding.all(14)))

        def rebuild():
            logged = session_service.get_sets_for_session(db, workout_session.id, exercise.id)

            logged_column.controls.clear()
            for s in logged:
                w = s.weight_kg if is_kg else s.weight_level
                w_str = f"{w} {unit}" if w is not None else "—"
                logged_column.controls.append(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREEN, size=16),
                            ft.Text(f"Satz {s.set_number}", width=55, color=ft.Colors.SECONDARY, size=13),
                            ft.Text(f"{s.reps} Wdh.", width=60, size=13),
                            ft.Text(w_str, size=13, color=ft.Colors.SECONDARY),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                )

        def add_set_row(e=None):
            logged = session_service.get_sets_for_session(db, workout_session.id, exercise.id)
            set_num = len(logged) + len(input_rows.controls) + 1

            reps_field = ft.TextField(
                label="Wdh.",
                width=75,
                keyboard_type=ft.KeyboardType.NUMBER,
                text_size=14,
                content_padding=ft.padding.symmetric(horizontal=8, vertical=8),
                autofocus=True,
            )
            weight_field = ft.TextField(
                label=unit,
                value=last_weight(),
                width=85,
                keyboard_type=ft.KeyboardType.NUMBER,
                text_size=14,
                content_padding=ft.padding.symmetric(horizontal=8, vertical=8),
            )

            row_ref: list[ft.Control] = []

            def confirm(e, sn=set_num, rf=reps_field, wf=weight_field):
                try:
                    reps = int(rf.value)
                except ValueError:
                    show_snack(page, "Wdh. muss eine Zahl sein.", error=True)
                    return

                wkg = wlevel = None
                raw = wf.value.strip()
                if is_kg:
                    try:
                        wkg = float(raw) if raw else None
                    except ValueError:
                        show_snack(page, "Ungültiges Gewicht.", error=True)
                        return
                else:
                    try:
                        wlevel = int(raw) if raw else None
                    except ValueError:
                        show_snack(page, "Ungültige Stufe.", error=True)
                        return

                session_service.log_set(db, workout_session.id, exercise.id, sn, reps, wkg, wlevel)
                if row_ref:
                    input_rows.controls.remove(row_ref[0])
                rebuild()
                page.update()

            row = ft.Row(
                controls=[
                    ft.Text(f"Satz {set_num}", width=55, size=13),
                    reps_field,
                    weight_field,
                    ft.IconButton(
                        icon=ft.Icons.CHECK_CIRCLE,
                        icon_color=ft.Colors.PRIMARY,
                        icon_size=28,
                        on_click=confirm,
                        tooltip="Bestätigen",
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color=ft.Colors.ERROR,
                        icon_size=20,
                        on_click=lambda e: (input_rows.controls.remove(row_ref[0]), page.update()),
                        tooltip="Abbrechen",
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            row_ref.append(row)
            input_rows.controls.append(row)
            page.update()

        # reference from last session
        ref_parts = []
        for s in last_sets:
            w = s.weight_kg if is_kg else s.weight_level
            ref_parts.append(f"S{s.set_number}: {s.reps}×{w}{unit}")
        ref_text = "Letztes Mal: " + "  ".join(ref_parts) if ref_parts else ""

        type_badge = ft.Container(
            content=ft.Text(
                "Maschine" if not is_kg else "Hantel/kg",
                size=11,
                color=ft.Colors.ON_SECONDARY_CONTAINER,
            ),
            bgcolor=ft.Colors.SECONDARY_CONTAINER,
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
        )

        rebuild()

        card_content.controls.clear()
        card_content.controls.extend([
            ft.Row(
                controls=[
                    ft.Text(exercise.name, size=16, weight=ft.FontWeight.W_600, expand=True),
                    type_badge,
                ],
            ),
            ft.Text(ref_text, size=11, color=ft.Colors.TERTIARY) if ref_text else ft.Container(height=0),
            logged_column,
            input_rows,
            ft.Row(
                controls=[
                    ft.TextButton(
                        "Satz hinzufügen",
                        icon=ft.Icons.ADD,
                        on_click=add_set_row,
                    )
                ],
            ),
        ])

        return card

    def render_all():
        exercises_column.controls.clear()
        for pe in plan.plan_exercises:
            exercises_column.controls.append(build_exercise_card(pe))
        page.update()

    def finish_workout(e):
        session_service.finish_session(db, workout_session.id)
        if on_finish:
            on_finish()

    render_all()

    return ft.Column(
        expand=True,
        controls=[
            ft.Row(
                controls=[
                    ft.Text(plan.name, size=20, weight=ft.FontWeight.BOLD, expand=True),
                    ft.FilledTonalButton(
                        "Beenden",
                        icon=ft.Icons.DONE_ALL,
                        on_click=finish_workout,
                    ),
                ],
            ),
            ft.Divider(),
            ft.Column(
                controls=[exercises_column],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
        ],
    )
