from flet import *
import datetime
from service.auth2 import *

# DB 연결 및 DB 객체 생성
DB.connect_db()
db = DB()

class Task(UserControl):

    def __init__(self, task_name, task_completed, task_date, task_status_change, task_delete, task_id = None):
        self.task_name = task_name
        self.task_completed = task_completed
        self.task_date = task_date
        self.task_status_change = task_status_change
        self.task_delete = task_delete
        self.task_id = task_id
        super().__init__()

    def build(self):

        self.display_task = Checkbox(
            value=self.task_completed,
            label=self.task_name,
            on_change=self.status_changed,
        )
        self.edit_name = TextField(expand=1)

        self.display_view = Row(
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                Column(
                    controls=[
                        self.display_task,
                        Text(
                            str(self.task_date)[:16],
                        )
                    ]),
                Row(
                    spacing=0,
                    controls=[
                        IconButton(
                            icon=icons.CREATE_OUTLINED,
                            tooltip="Edit To-Do",
                            on_click=self.edit_clicked,
                        ),
                        IconButton(
                            icons.DELETE_OUTLINE,
                            tooltip="Delete To-Do",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = Row(
            visible=False,
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                self.edit_name,
                IconButton(
                    icon=icons.DONE_OUTLINE_OUTLINED,
                    icon_color=colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return Column(controls=[self.display_view, self.edit_view])

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False

        self.task_name = self.edit_name.value
        db.update_db( self.task_id, {'task': self.task_name})
        self.update()

    def status_changed(self, e):
        self.task_completed = self.display_task.value
        self.task_status_change(self)
        self.update()

    def delete_clicked(self, e):
        db.delete_db(self.task_id)
        self.task_delete(self)
        self.update()


class TodoApp(Container):

    def __init__(self, page: Page):
        super().__init__()
        page.padding = 0
        page.window_width = 500

        self.task_list = db.read_db()
        self.new_task = TextField(hint_text="Whats needs to be done?", expand=True)
        self.tasks = Column()

        if self.task_list is not None:

            for id, t in self.task_list.items():
                task = Task(t['task'], t['completed'], t['reg_date'], self.task_status_change, self.task_delete, id)
                self.tasks.controls.insert(0, task)

        self.filter = Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[Tab(text="all"), Tab(text="active"), Tab(text="completed")],
        )

        # application's root control (i.e. "view") containing all other controls
        self.content = Column(
            width=600,
            height=700,
            controls=[
                Row(
                    alignment=alignment.center_right,
                    controls=[
                        IconButton(
                            icon = icons.EXIT_TO_APP,
                            icon_size=20,
                            tooltip='Logout',
                            on_click=lambda _: (revoke_token(load_token()), self.page.go('/login'))
                        ),
                        IconButton(
                            icon=icons.DASHBOARD,
                            icon_size=20,
                            tooltip='Dashboard',
                            on_click=lambda _: self.page.go('/dashboard')
                        )
                    ]

                ),
                Row(
                    controls=[
                        self.new_task,
                        FloatingActionButton(icon=icons.ADD, on_click=self.add_clicked),
                    ],
                ),
                Column(
                    spacing=25,
                    height=500,
                    controls=[
                        self.filter,
                        self.tasks,
                    ],
                    scroll=ScrollMode.AUTO
                ),
            ],
        )

    def add_clicked(self, e):
        t = datetime.datetime.now()
        id = db.insert_db({
            'task': self.new_task.value,
            'completed': False,
            'reg_date': str(t)
        })
        task = Task(self.new_task.value, False, t, self.task_status_change, self.task_delete, id)
        self.tasks.controls.insert(0, task)
        self.new_task.value = ""
        self.update()

    def task_status_change(self, task):
        # task 상태 업데이트
        db.update_task_state(task.task_id, {'completed': task.task_completed})
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()

    def update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        for task in self.tasks.controls:
            task.visible = (
                    status == "all"
                    or (status == "active" and task.task_completed == False)
                    or (status == "completed" and task.task_completed)
            )
        super().update()

    def tabs_changed(self, e):
        self.update()
