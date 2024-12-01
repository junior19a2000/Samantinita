import flet as ft
import pandas as pd
import numpy as np
import random
import gspread
import datetime
import json
import os

def main(page: ft.Page):
    activity_to_delete = None
    initialized = False
    sheets = None
    samantha = None 
    junior = None
    frases = None
    new_activities = ft.Column(spacing = 10, scroll = ft.ScrollMode.HIDDEN)
    done_activities = ft.Column(spacing = 20, scroll = ft.ScrollMode.ALWAYS)

    class Activity:
        def __init__(self, description, status):
            self.description = description
            self.status = status
        def show(self):
            activity = ft.Row(
                controls = [
                    ft.Checkbox(
                        value = self.status, 
                        label = "", 
                        on_change = change_status_activity,
                    ),
                    ft.TextField(
                        value = self.description, 
                        label = "", 
                        expand = True, 
                        disabled = True,
                    ),
                    ft.IconButton(
                        icon = ft.icons.CREATE_OUTLINED, 
                        on_click = edit_activity,
                    ),
                    ft.IconButton(
                        icon = ft.icons.DELETE_OUTLINE, 
                        on_click = show_dialog,
                    ),
                ],
                spacing = 10,
            )
            return activity

    def update_bar():
        progressbar1.value = len(done_activities.controls) / len(new_activities.controls + done_activities.controls) if len(new_activities.controls + done_activities.controls) != 0 else 0.0

    def update_sheet(e):
        date = str(datetime.datetime.now()).split(" ")[0]
        sheet = sheets.worksheet(date)
        sheet.clear()
        matrix1 = [""]
        for i in new_activities.controls:
            matrix1.append(i.controls[1].value)
        matrix1 = pd.DataFrame(matrix1)
        matrix2 = [""]
        for i in done_activities.controls:
            matrix2.append(i.controls[1].value)
        matrix2 = pd.DataFrame(matrix2)
        matrix3 = pd.concat([matrix1, matrix2], axis = 1, ignore_index = True).fillna("")
        matrix3.columns = ['Actividades pendientes', 'Actividades realizadas']
        sheet.update([matrix3.columns.values.tolist()] + matrix3.values.tolist())          

    def add_activity(e):
        if textfield1.value != "":
            new_activities.controls.append(Activity(textfield1.value, False).show())
            textfield1.value = ""
            update_bar()
            page.update()

    def change_status_activity(e):
        for activity in new_activities.controls[:]:
            if activity.controls[0].value:  
                new_activities.controls.remove(activity)
                done_activities.controls.append(activity)
                break
        for activity in done_activities.controls[:]:
            if not activity.controls[0].value:  
                done_activities.controls.remove(activity)
                new_activities.controls.append(activity)
                break
        update_bar()
        page.update()

    def edit_activity(e):
        for activity in new_activities.controls[:]:
            if e.control in activity.controls:
                if activity.controls[1].disabled:
                    activity.controls[1].disabled = False
                    activity.controls[2].icon = ft.icons.SPELLCHECK
                else:
                    activity.controls[1].disabled = True
                    activity.controls[2].icon = ft.icons.CREATE_OUTLINED
                break
        for activity in done_activities.controls[:]:
            if e.control in activity.controls:
                if activity.controls[1].disabled:
                    activity.controls[1].disabled = False
                    activity.controls[2].icon = ft.icons.SPELLCHECK
                else:
                    activity.controls[1].disabled = True
                    activity.controls[2].icon = ft.icons.CREATE_OUTLINED
                break
        page.update()

    def delete_activity(e):
        nonlocal activity_to_delete
        if activity_to_delete in new_activities.controls:
            new_activities.controls.remove(activity_to_delete)
        else:
            done_activities.controls.remove(activity_to_delete)
        page.close(alertdialog1)
        update_bar()
        page.update()

    def no_delete_activity(e):
        page.close(alertdialog1)

    def show_dialog(e):
        nonlocal activity_to_delete
        for activity in new_activities.controls + done_activities.controls:
            if e.control in activity.controls:
                activity_to_delete = activity
                break
        page.open(alertdialog1)
    
    def close_love_msg(e):
        page.close(alertdialog2)
        alertdialog2.content.content = ft.Text(
            value = random.choice(frases), 
            size = 20, 
            font_family = "RobotoSlab", 
            text_align = ft.TextAlign.CENTER,
        )

    def change_photo(e):
        photo = random.randint(1, len(os.listdir(f"assets/Photos")))
        e.control.content.content = ft.Image(
            src = f"/Photos/Photo (" + str(photo) + ").jpg",
            width = 200,
            height = 200,
            fit = ft.ImageFit.COVER,
            border_radius = ft.border_radius.all(10),
        )
        e.control.content.update()

    def user(e):
        nonlocal sheets, new_activities, done_activities
        page.controls.clear()
        new_activities.controls.clear()
        done_activities.controls.clear()
        # new_activities.alignment = ft.MainAxisAlignment.SPACE_EVENLY
        date = str(datetime.datetime.now()).split(" ")[0]
        if e.control.content.src == f"/Samantha.jpg":
            sheets = samantha
            page.appbar.title.content.value = "¡ Bonito día Samliz !"
        else:
            sheets = junior
            page.appbar.title.content.value = "¡ Bonito día Junior !"
        sheets_names = [sheet.title for sheet in sheets.worksheets()]
        if date not in sheets_names:
            sheets.add_worksheet(title = date, rows = "50", cols = "5")
        else:
            sheet = sheets.worksheet(date)
            matrix1 = pd.DataFrame(sheet.get_all_records())
            try:
                for i in matrix1["Actividades pendientes"]:
                    if i != "":
                        new_activities.controls.append(Activity(str(i), False).show())
                for i in matrix1["Actividades realizadas"]:
                    if i != "":
                        done_activities.controls.append(Activity(str(i), True).show())
            except:
                pass
        page.add(column1)
        page.update()

    def initialize_app():
        nonlocal initialized, samantha, junior, frases
        if not initialized:
            credentials_json = os.getenv("CREDENTIALS")
            credentials_dict = json.loads(credentials_json)
            gs = gspread.service_account_from_dict(credentials_dict)
            samantha = gs.open_by_key("1vyQ-aZB5mpCseR3p1oKvLX3TIBArC7h81OdxmTU2wYI")
            junior = gs.open_by_key("1hOisjm1adGuZT0gVR0dTJPBUo_Q4IA8U8fj5MgtXomQ")
            frases = pd.read_excel("https://docs.google.com/spreadsheets/d/1I4wwUy_6ykmS8tQSPGwmI2mWtBvS8hkkzYJXk8pQObM/export?format=xlsx&gid=0", sheet_name = 'Frases')["Frases"].to_list()

            gridview1 = ft.GridView(
                expand = 1,
                runs_count = 2,
                child_aspect_ratio = 1,
                spacing = 5,
                run_spacing = 5,
            )
            for i in random.sample(np.arange(1, len(os.listdir(f"assets/Photos"))).tolist(), 6):
                gridview1.controls.append(
                    ft.Container(
                        content = ft.AnimatedSwitcher(
                            content = ft.Image(
                                src = f"/Photos/Photo (" + str(i) + ").jpg",
                                width = 200,
                                height = 200,
                                fit = ft.ImageFit.COVER,
                                border_radius = ft.border_radius.all(10),
                            ),
                            transition = ft.AnimatedSwitcherTransition.FADE,
                            duration = 5000,
                            reverse_duration = 5000,
                            switch_in_curve = ft.AnimationCurve.BOUNCE_OUT,
                            switch_out_curve = ft.AnimationCurve.BOUNCE_IN,
                        ),
                        on_click = change_photo,
                    )
                )
            container1 = ft.Container(
                content = gridview1, 
                width = 300, 
                border_radius = 10,
                padding = 5,
            )
            hoy = datetime.date.today()
            if hoy.day != 1:
                ano = hoy.year if hoy.month != 12 else hoy.year + 1
                mes = hoy.month + 1 if hoy.month != 12 else 1
                msg = f'''Hoy se cumplen {(hoy - datetime.date(2024, 4, 6)).days + 1} días de haberte conocido amorsin... estos {int(((hoy - datetime.date(2024, 6, 1)).days + 1) / 30)} meses juntos han sido los mas felices y dentro de {(datetime.date(ano, mes, 1) - hoy).days} dias, iremos por uno más. Te amo !\n\nAtte. Junior'''
            else:
                msg = f'''🎉 Felices {int(((hoy - datetime.date(2024, 6, 1)).days + 1) / 30)} meses juntos bb !!!'''
            container2 = ft.Container(
                content = ft.Text(
                    value = msg, 
                    font_family = "RobotoSlab", 
                    size = 8, 
                    text_align = ft.TextAlign.CENTER,
                    ),
                width = 300, 
                alignment = ft.alignment.center,
            )
            page.add(container1, container2)
            page.update()
            initialized = True

    page.title = "Samantinita"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#050505"
    page.fonts = {
        "RobotoSlab": "https://github.com/google/fonts/raw/main/apache/robotoslab/RobotoSlab%5Bwght%5D.ttf"
    }
    page.appbar = ft.AppBar(
        leading = ft.IconButton(
            icon = ft.icons.MENU, 
            on_click = lambda e: page.open(drawer)
        ),
        leading_width = 40,
        title = ft.Container(
            content = ft.Text(
                value = "¡ Bonito día amorsin !", 
                font_family = "RobotoSlab", 
                size = 17.5
            ), 
            alignment = ft.alignment.center
        ),
        bgcolor = "#050505",
        actions = [
            ft.Container(
                content = ft.Text(
                    value = "🌻", 
                    size = 20
                ), 
                bgcolor = "#050505", 
                padding = 10, 
                alignment = ft.alignment.center, 
                on_click = lambda e: page.open(alertdialog2)
            )
        ],
    )
    initialize_app()

    alertdialog1 = ft.AlertDialog(
        modal = True,
        title = ft.Text(
            value = "😱",
        ),
        content = ft.Text(
            value = "¿Segura de que quieres eliminar esta actividad?", 
            font_family = "RobotoSlab",
        ),
        actions = [
            ft.TextButton(
                text = "Si", 
                on_click = delete_activity,
            ),
            ft.TextButton(
                text = "No", 
                on_click = no_delete_activity,
            ),
        ],
        actions_alignment = ft.MainAxisAlignment.END,
    )
    alertdialog2 = ft.AlertDialog(
        modal = True,
        title = ft.Container(
            content = ft.Text(
                value = "🧡 ➕ 🌻", 
                size = 30, 
                font_family = "RobotoSlab",
            ), 
            alignment = ft.alignment.center,
        ),
        content = ft.Container(
            content = ft.Text(
                value = random.choice(frases), 
                size = 20, 
                font_family = "RobotoSlab", 
                text_align = ft.TextAlign.CENTER,
            ), 
            alignment = ft.alignment.center,
        ),
        actions = [
            ft.TextButton("🧡", on_click = close_love_msg),
        ],
        actions_alignment = ft.MainAxisAlignment.CENTER,
    )
    textfield1 = ft.TextField(
        label = "¿Qué quieres hacer hoy bebé?", 
        expand = True,
        border_width = 1,
        border_color = "#ffffff",
        border_radius = ft.BorderRadius(
            top_left = 10,
            top_right = 10,
            bottom_left = 10,
            bottom_right = 10,
        ),
    )
    progressbar1 = ft.ProgressBar(
        value = len(done_activities.controls) / len(new_activities.controls + done_activities.controls) if len(new_activities.controls + done_activities.controls) != 0 else 0.0, 
        color = "#f58105",
        bgcolor = "#ffffff",
        # bar_height = 80, 
        height = 10,
        border_radius = ft.BorderRadius(
            top_left = 5,
            top_right = 5,
            bottom_left = 5,
            bottom_right = 5,
        ),
    )
    column1 = ft.Column(
        controls = [
            ft.Row(
                controls = [
                    textfield1, 
                    ft.FloatingActionButton(
                        icon = ft.icons.ADD, 
                        on_click = add_activity,
                        bgcolor = "#000000",
                    )
                ],
                spacing = 10,
                expand = True,
            ),
            progressbar1,
            ft.Tabs(
                selected_index = 0,
                animation_duration = 250,
                tabs = [
                    ft.Tab(
                        text = "Actividades por hacer",
                        content = new_activities,
                    ),
                    ft.Tab(
                        text = "Actividades ya realizadas",
                        content = done_activities,
                    ),
                ],
                expand = True,
            ),
        ],
    )
    column2 = ft.Column(
        controls = [
            ft.Container(
                content = ft.Text(
                    value = "Samantinita App v1.0.0 \nDesarrollada con mucho amor para mi Samliz", 
                    size = 10, 
                    font_family = "RobotoSlab", 
                    text_align = ft.TextAlign.CENTER,
                ),
                alignment = ft.alignment.center,
                margin = ft.margin.symmetric(vertical = 20),
            ),
            ft.Container(
                content = ft.Row(
                    controls = [
                        ft.Container(
                            content = ft.Image(
                                src = f"/Junior.jpg",
                                height = 300,
                                fit = ft.ImageFit.FIT_WIDTH,
                                border_radius = ft.BorderRadius(
                                    top_left = 30,
                                    top_right = 0,
                                    bottom_left = 30,
                                    bottom_right = 0,
                                ),
                            ),
                            ink = True,
                            on_click = user,
                        ),
                        ft.Container(
                            content = ft.Image(
                                src = f"/Samantha.jpg",
                                height = 300,
                                fit = ft.ImageFit.FIT_WIDTH,
                                border_radius = ft.BorderRadius(
                                    top_left = 0,
                                    top_right = 30,
                                    bottom_left = 0,
                                    bottom_right = 30,
                                ),
                            ),
                            ink = True,
                            on_click = user,
                        ),
                    ],
                    spacing = 0,
                    alignment = ft.MainAxisAlignment.CENTER,
                ),
                alignment = ft.alignment.center,
                margin = ft.margin.symmetric(vertical = 40),
            )
            # ft.Container(
            #     content = ft.Column(
            #         controls = [
            #             users,
            #             ft.FilledButton("Registrar actividades .l.", icon = ft.icons.CLOUD_UPLOAD_OUTLINED, on_click = update_sheet, style = ft.ButtonStyle(bgcolor = "#050505", color = "#f58105", padding = ft.padding.all(20.5),))
            #             ],
            #         horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            #         spacing = 10,
            #         ),
            #     width = 225,
            #     alignment = ft.alignment.center,
            # ),
        ],
        alignment = ft.MainAxisAlignment.SPACE_AROUND,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        spacing = 20,
    )
    drawer = ft.NavigationDrawer(
        controls = [column2],
        bgcolor = "#f58105",
    )

ft.app(main, assets_dir = f"assets")