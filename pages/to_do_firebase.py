from flet import *
import datetime

# pip install firebase-admin
# firebase console에 로그인
# 프로젝트 생성
# 프로젝트 설정 > 서비스 계정 메뉴로 가서
# 파이선 코드 복사해서 가져오고 private key 생성 후 프로젝트 폴더로 복사

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://flet-course-default-rtdb.firebaseio.com/'
})


# DB 관리 클래스
class DB:

    ref = None

    @staticmethod
    def connect_db():

        try:
            DB.ref = db.reference('/todos')
        except Exception as e:
            print(e)

    def read_db(self):
        return DB.ref.get()

    def insert_db(self, values):
        new_ref = DB.ref.push()
        new_key = new_ref.key
        new_ref.set(values)
        return new_key

    def delete_db(self, key):
        DB.ref.child(key).set({})

    def update_db(self, key, values):
        DB.ref.child(key).update(values)

    def update_task_state(self, key, value):
        DB.ref.child(key).update(value)

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


class TodoApp(UserControl):

    def build(self):

        task_list = db.read_db()

        self.new_task = TextField(hint_text="Whats needs to be done?", expand=True)
        self.tasks = Column()

        if task_list is not None:

            for id, t in task_list.items():
                task = Task(t['task'], t['completed'], t['reg_date'], self.task_status_change, self.task_delete, id)
                self.tasks.controls.insert(0, task)

        self.filter = Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[Tab(text="all"), Tab(text="active"), Tab(text="completed")],
        )

        # application's root control (i.e. "view") containing all other controls
        return Column(
            width=600,
            height=500,
            controls=[
                Row(
                    controls=[
                        self.new_task,
                        FloatingActionButton(icon=icons.ADD, on_click=self.add_clicked),
                    ],
                ),
                Column(
                    spacing=25,
                    controls=[
                        self.filter,
                        self.tasks,
                    ],
                ),
            ],

            scroll=True
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


def main(page: Page):
    page.title = "ToDo App"
    page.horizontal_alignment = "center"
    page.window_width = 500
    page.window_height = 600
    page.window_maximizable = False
    page.window_minimizable = False
    page.update()

    # create application instance
    app = TodoApp(db)

    # add application's root control to the page
    page.add(app)


flet.app(target=main)