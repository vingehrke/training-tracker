import flet as ft


def show_snack(page: ft.Page, message: str, error: bool = False):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=ft.Colors.ERROR_CONTAINER if error else None,
    )
    page.snack_bar.open = True
    page.update()
