import flet as ft
from app.db.database import init_db
from app.views import exercises_view, plans_view, workout_view, history_view


def main(page: ft.Page):
    page.title = "Training Tracker"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 16

    init_db()

    content = ft.Column(expand=True)
    active_workout_plan_id: list[int | None] = [None]

    def navigate(index: int):
        content.controls.clear()
        if active_workout_plan_id[0] is not None and index != 1:
            active_workout_plan_id[0] = None

        if index == 0:
            content.controls.append(
                plans_view.build(page, on_start_workout=start_workout)
            )
        elif index == 1:
            if active_workout_plan_id[0] is not None:
                content.controls.append(
                    workout_view.build(
                        page,
                        plan_id=active_workout_plan_id[0],
                        on_finish=finish_workout,
                    )
                )
            else:
                content.controls.append(
                    ft.Column(
                        expand=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.FITNESS_CENTER, size=64, color=ft.Colors.SECONDARY),
                            ft.Text("Kein aktives Training.", size=16, color=ft.Colors.SECONDARY),
                            ft.Text("Starte ein Training über die Pläne-Ansicht.", color=ft.Colors.TERTIARY),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                )
        elif index == 2:
            content.controls.append(exercises_view.build(page))
        elif index == 3:
            content.controls.append(history_view.build(page))

        page.update()

    def start_workout(plan_id: int):
        active_workout_plan_id[0] = plan_id
        nav.selected_index = 1
        navigate(1)

    def finish_workout():
        active_workout_plan_id[0] = None
        nav.selected_index = 0
        navigate(0)

    nav = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.LIST_ALT, label="Pläne"),
            ft.NavigationBarDestination(icon=ft.Icons.FITNESS_CENTER, label="Training"),
            ft.NavigationBarDestination(icon=ft.Icons.SPORTS_GYMNASTICS, label="Übungen"),
            ft.NavigationBarDestination(icon=ft.Icons.HISTORY, label="Historie"),
        ],
        on_change=lambda e: navigate(e.control.selected_index),
    )

    page.add(
        ft.Column(
            expand=True,
            controls=[content, nav],
        )
    )

    navigate(0)


ft.run(main)
