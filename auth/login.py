# auth/login.py

from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

from auth.auth_utils import authenticate_user
from user_panel.dashboard import UserDashboard
from staff_panel.dashboard import StaffDashboard
from manager_panel.dashboard import ManagerDashboard


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart Archive Login")
        self.setFixedSize(420, 520)

        self.dashboard = None  # جلوگیری از بسته شدن پنجره داشبورد

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):

        self.lbl_title = QLabel("SMART ARCHIVE", self)
        self.lbl_title.setGeometry(110, 60, 250, 50)
        self.lbl_title.setAlignment(Qt.AlignCenter)

        self.lbl_sub = QLabel("خوش آمدید، لطفاً وارد شوید", self)
        self.lbl_sub.setGeometry(110, 110, 250, 30)
        self.lbl_sub.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit(self)
        self.username_input.setGeometry(50, 180, 320, 45)
        self.username_input.setPlaceholderText("نام کاربری")

        self.password_input = QLineEdit(self)
        self.password_input.setGeometry(50, 240, 320, 45)
        self.password_input.setPlaceholderText("رمز عبور")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("ورود به پنل", self)
        self.login_btn.setGeometry(50, 310, 320, 50)
        self.login_btn.clicked.connect(self.handle_login)

        self.error_label = QLabel("", self)
        self.error_label.setGeometry(50, 370, 320, 40)
        self.error_label.setAlignment(Qt.AlignCenter)

    def apply_styles(self):

        self.setStyleSheet("""
            QWidget {
                background-color: #0d0f1a;
                color: #E6E6E6;
                font-family: IRANSans;
            }

            QLabel {
                font-size: 16px;
            }

            QLineEdit {
                background-color: #141824;
                border-radius: 10px;
                padding: 10px;
                border: 1px solid #1e2230;
                color: white;
            }

            QPushButton {
                background-color: #00bfff;
                border-radius: 10px;
                font-size: 16px;
                padding: 8px;
            }

            QPushButton:hover {
                background-color: #14c8ff;
            }
        """)

    def handle_login(self):

        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.error_label.setText("هر دو فیلد الزامی هستند")
            return

        ok, msg, user = authenticate_user(username, password)

        if not ok:
            self.error_label.setText(msg)
            return

        self.error_label.setText("")
        self.open_dashboard(user)

    def open_dashboard(self, user_data):

        role = user_data["role"]

        if role == "user":
            self.dashboard = UserDashboard(user_data)

        elif role == "staff":
            self.dashboard = StaffDashboard(user_data)

        elif role == "manager":
            self.dashboard = ManagerDashboard(user_data)

        else:
            QMessageBox.warning(self, "خطا", "نقش کاربر نامعتبر است")
            return

        self.dashboard.show()
        self.close()
