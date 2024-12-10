import sys
import cx_Oracle
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox, QVBoxLayout, QScrollArea


class App(QWidget):
    def __init__(self):
        super().__init__()
        with open("style.css", "r") as file:
            sheet = file.read()
        self.setStyleSheet(sheet)
        file.close()

        self.setWindowTitle('Application')

        self.login_label = QLabel("Логин")
        self.login_enter = QLineEdit()
        self.password_label = QLabel("Пароль")
        self.password_enter = QLineEdit()
        self.password_enter.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Войти")
        self.sql_enter = QTextEdit()
        self.sql_enter.setPlaceholderText("Введите ваш SQL-запрос...")
        self.sql_ex_button = QPushButton("Выполнить")
        self.sql_ex_res = QLabel()
        self.scrolling = QScrollArea()

        self.sql_enter.hide()
        self.sql_ex_button.hide()
        self.sql_ex_res.hide()
        self.scrolling.hide()

        self.initUI()

        self.login_button.clicked.connect(self.login)
        self.sql_ex_button.clicked.connect(self.sql_ex)

    def initUI(self):
        main_layout = QVBoxLayout()
        login_layout = QVBoxLayout()
        login_layout.addWidget(self.login_label)
        login_layout.addWidget(self.login_enter)
        password_layout = QVBoxLayout()
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_enter)
        main_layout.addLayout(login_layout)
        main_layout.addLayout(password_layout)
        main_layout.addWidget(self.login_button)
        main_layout.addWidget(self.sql_enter)
        main_layout.addWidget(self.sql_ex_button)
        main_layout.addWidget(self.sql_ex_res)
        main_layout.addWidget(self.scrolling)

        self.setLayout(main_layout)
        self.resize(600, 400)
        self.center_window()

    def center_window(self):
        self.frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        self.frameGm.moveCenter(centerPoint)
        self.move(self.frameGm.topLeft())
        self.show()

    def login(self):
        user_login = str(self.login_enter.text())
        user_password = str(self.password_enter.text())
        try:
            self.connection = cx_Oracle.connect(user=user_login, password=user_password, dsn="localhost/XE")
            self.login_label.hide()
            self.password_label.hide()
            self.login_enter.hide()
            self.password_enter.hide()
            self.login_button.hide()
            self.sql_enter.show()
            self.sql_ex_button.show()

            self.resize(1280, 720)
            self.center_window()

        except cx_Oracle.DatabaseError as e:
            self.error_box("login", str(e))
        except Exception as e:
            self.error_box("error", str(e))

    def sql_ex(self):
        if str(self.sql_enter.toPlainText()).lower().startswith("create"):
            typ = "create"
        else:
            typ = "exec"
        with self.connection.cursor() as cursor:
            sql = self.sql_enter.toPlainText()
            try:
                sql_res = ""
                if typ == "exec":
                    results = cursor.execute(sql).fetchall()
                    if not results:
                        sql_res = "Нет данных для отображения."
                    else:
                        sql_res += "<table style='border-collapse: collapse; width: 100%;'>"
                        columns = [desc[0] for desc in cursor.description]
                        sql_res += "<tr>"
                        for col in columns:
                            sql_res += (f"<th style='border: 1px solid #ddd; padding: 8px; text-align: left; "
                                        f"background-color: #f4f4f9;'>{col}</th>")
                        sql_res += "</tr>"
                        for row in results:
                            sql_res += "<tr>"
                            for value in row:
                                sql_res += f"<td style='border: 1px solid #ddd; padding: 8px;'>{value}</td>"
                            sql_res += "</tr>"
                        sql_res += "</table>"

                    self.sql_ex_res.setText(sql_res)
                    self.sql_ex_res.setTextFormat(1)  # 1 - HTML

                    self.scrolling.setWidget(self.sql_ex_res)
                    self.sql_ex_res.setAlignment(Qt.AlignTop)
                    self.sql_ex_res.setTextInteractionFlags(Qt.TextBrowserInteraction)
                    # self.sql_ex_res.setMinimumHeight(1000)
                    self.scrolling.setMinimumHeight(500)
                    self.scrolling.setWidgetResizable(True)

                    self.scrolling.show()
                elif typ == "create":
                    cursor.execute(sql)
                    self.error_box("ok")

            except cx_Oracle.DatabaseError as e:
                self.error_box("sqlerror", str(e))
            except Exception as e:
                self.error_box("error", str(e))

    @staticmethod
    def error_box(typ, msg=None):
        err = QMessageBox()
        err.setWindowTitle("Ошибка")
        if typ == "login":
            err.setText(f"Неверный логин и/или пароль. Oracle: {msg}")
        elif typ == "sqlerror":
            err.setText(f"Неправильный запрос. Oracle: {msg}")
        elif typ == "ok":
            err.setText("Запрос выполнен")
            err.setWindowTitle("Успех")
        else:
            err.setText(f"Что-то пошло не так. {msg}")
        err.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
