from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal, QTimer

from movrs_client.ControlPanel import ControlPanel
from movrs_client.movrs_apis import login_user, read_json_file


class LoginWorker(QObject):
    finished = pyqtSignal(bool)

    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password

    def run(self):
        result = login_user(self.email, self.password)
        self.finished.emit(result)


class GlassMorphicLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Movrs Package Login")
        self.setGeometry(100, 100, 400, 500)
        self.setStyleSheet(
            "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1E1E1E, stop:1 #3A3A3A);")

        self.layout = QVBoxLayout()

        self.title = QLabel("MOVRS")
        self.title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: white;")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Email")
        self.username.setStyleSheet(self.inputStyle())

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setStyleSheet(self.inputStyle())

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 14px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.login_btn = QPushButton("Login")
        self.login_btn.setStyleSheet(self.buttonStyle())
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.login)

        # Add all widgets to layout unconditionally
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.username)
        self.layout.addWidget(self.password)
        self.layout.addWidget(self.error_label)
        self.layout.addWidget(self.login_btn)

        self.setLayout(self.layout)

        # Try auto-login
        data = read_json_file("user_cred.json")
        if data.get("logged_user_id") and data.get("logged_user_id") != "":
            # Slight delay to allow UI to show first
            QTimer.singleShot(100, lambda: self.login_user(data.get("email"), data.get("password")))

    def inputStyle(self):
        return (
            "background: rgba(255, 255, 255, 0.1);"
            "border: none;"
            "border-radius: 10px;"
            "padding: 10px;"
            "color: white;"
            "font-size: 16px;"
        )

    def buttonStyle(self):
        return (
            "background: rgba(255, 255, 255, 0.2);"
            "border-radius: 10px;"
            "padding: 10px;"
            "color: white;"
            "font-size: 16px;"
            "border: 1px solid rgba(255, 255, 255, 0.5);"
        )

    def login(self):
        self.login_user(self.username.text(), self.password.text())

    def login_user(self, email, password):
        self.login_btn.setEnabled(False)
        self.error_label.setText("Logging in user please wait...")
        QApplication.processEvents()  # Ensure UI updates before thread starts

        self.thread = QThread()
        self.worker = LoginWorker(email, password)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_login_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_login_finished(self, success):
        self.login_btn.setEnabled(True)

        if success:
            self.error_label.setText("")
            self.hide()
            self.control_panel = ControlPanel(self)
            self.control_panel.show()
        else:
            self.error_label.setText("Invalid email or password.")
