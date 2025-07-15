from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QProgressBar, QComboBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer
from movrs_client.movrs_apis import get_user_info, read_json_file, update_json_fields, run_docker_compose,stop_docker_compose
from movrs_client.service_manager import create_service_file, enable_service, start_service, stop_service, disable_service
import os

# Determine the base directory of the installed package
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print("BASE DIR", BASE_DIR)

class ControlPanel(QWidget):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.initUI()

    def initUI(self):
        try:
            print(get_user_info())
            user_data = get_user_info()[0]
            self.docker_process = ''

            self.setWindowTitle("Movrs Client")
            self.setGeometry(150, 150, 300, 250)
            self.setStyleSheet("background: #2E2E2E; color: white;")

            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

            layout = QVBoxLayout()

            self.welcome_label = QLabel("Welcome : " + self.get_user_display_name(user_data))
            self.welcome_label.setFont(QFont("Arial", 14))
            self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.version_label = QLabel("Select Version: " + user_data.get('version_id'))
            self.version_label.setFont(QFont("Arial", 14))
            self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.process_button = QPushButton("Start Process")
            self.process_button.setStyleSheet(self.buttonStyle())
            self.process_button.clicked.connect(self.toggleProcess)

            self.logout_button = QPushButton("Logout")
            self.logout_button.setStyleSheet(self.buttonStyle())
            self.logout_button.clicked.connect(self.logout)

            layout.addWidget(self.welcome_label)
            layout.addWidget(self.version_label)
            layout.addWidget(self.process_button)
            layout.addWidget(self.logout_button)
            self.setLayout(layout)

            self.process_running = False
        except: 
            print("something went wrong")
    def toggleProcess(self):
        data = read_json_file()
        state = data.get("state")
        if state == "":
            self.process_button.setText("Stop Process")
            update_json_fields([['state', 'running']])
            self.docker_process = run_docker_compose()
            create_service_file()
            enable_service()
            self.process_running = False
        else:
            stop_service()
            update_json_fields([['state', '']])
            self.process_button.setText("Start Process")
            self.process_running = True

    def get_user_display_name(self, user_data):
        """
        Returns the display name for a user, falling back to email if displayName is missing or None.
        """
        return user_data.get("displayName") or user_data.get("email")

    def logout(self):
        update_json_fields([['state', '']])
        update_json_fields([['logged_user_id', ''], ['email', ''], ['password', '']], os.path.join(BASE_DIR, "user_cred.json"))
        if self.docker_process:
            self.docker_process.terminate()
        self.docker_process = ''
        self.close()
        self.login_window.show()

    def buttonStyle(self):
        return (
            "background: rgba(255, 255, 255, 0.2);"
            "border-radius: 10px;"
            "padding: 10px;"
            "color: white;"
            "font-size: 16px;"
            "border: 1px solid rgba(255, 255, 255, 0.5);"
        )

