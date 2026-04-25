import flet as ft
from ..db.database import get_session
from ..db.models import WeightType
from ..services import session_service


def build(page: ft.Page) -> ft.Control:
    db = get_session()
    detail_column = ft.Column(visible=False, expand=True)
    session_list = ft.ListView(expand=False, spacing=4)

    def show_session_detail(session_id: int):
        sessions = session_service.get_recent_sessions(db, limit=50)
        session = next((s for s in sessions if s.id == session_id), None)
        if not session:
            return

        sets_by_exercise: dict[str, list] = {}
        for s in session.exercise_sets:
            name = s.exercise.name
            sets_by_exercise.setdefault(name, []).append(s)

        rows = []
        for ex_name, sets in sets_by_exercise.items():
            ex = sets[0].exercise
            unit = "kg" if ex.weight_type == WeightType.KG else "Stufe"
            set_texts = "  ".join(
                f"S{s.set_number}: {s.reps}× {s.weight_kg if ex.weight_type == WeightType.KG else s.weight_level}{unit}"
                for s in sorted(sets, key=lambda x: x.set_number)
            )
            rows.append(ft.ListTile(title=ft.Text(ex_name), subtitle=ft.Text(set_texts)))

        duration = ""
        if session.finished_at and session.started_at:
            delta = session.finished_at - session.started_at
            mins = int(delta.total_seconds() // 60)
            duration = f" · {mins} min"

        detail_column.controls.clear()
        detail_column.controls.extend([
            ft.Text(
                f"{session.plan.name} — {session.started_at.strftime('%d.%m.%Y %H:%M')}{duration}",
                size=16,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(session.notes or "", color=ft.Colors.SECONDARY),
            ft.Divider(),
            *rows,
        ])
        detail_column.visible = True
        page.update()

    def refresh_list():
        session_list.controls.clear()
        for s in session_service.get_recent_sessions(db, limit=20):
            duration = ""
            if s.finished_at and s.started_at:
                delta = s.finished_at - s.started_at
                mins = int(delta.total_seconds() // 60)
                duration = f" · {mins} min"
            session_list.controls.append(
                ft.ListTile(
                    title=ft.Text(s.plan.name),
                    subtitle=ft.Text(f"{s.started_at.strftime('%d.%m.%Y %H:%M')}{duration}"),
                    on_click=lambda e, sid=s.id: show_session_detail(sid),
                )
            )
        page.update()

    refresh_list()

    return ft.Row(
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Column(
                width=240,
                expand=False,
                controls=[
                    ft.Text("Trainings-Historie", size=22, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    session_list,
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            ft.VerticalDivider(),
            ft.Column(expand=True, controls=[detail_column], scroll=ft.ScrollMode.AUTO),
        ],
    )
