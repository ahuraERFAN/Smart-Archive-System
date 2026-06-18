# staff_panel/dashboard.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt

from staff_panel.review_documents import ReviewDocuments
from staff_panel.ticket_manager import TicketManager
from staff_panel.form_registration import FormRegistration


class StaffDashboard(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data  # شامل id, full_name, ...
        self.review_window = None
        self.ticket_window = None
        self.form_window = None

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        self.setObjectName("staffRoot")
        self.setWindowTitle("پنل کارمند")
        self.resize(750, 420)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # هدر
        header = QLabel("پنل کارمند")
        header.setObjectName("staffHeader")
        header.setAlignment(Qt.AlignCenter)

        sub_header = QLabel(f"کاربر: {self.user_data.get('full_name', '')}")
        sub_header.setObjectName("staffSubHeader")
        sub_header.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(header)
        main_layout.addWidget(sub_header)

        # خط جداکننده
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # دکمه‌ها
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.review_btn = QPushButton("📂 بررسی اسناد")
        self.review_btn.setObjectName("primaryBtn")
        self.review_btn.clicked.connect(self.open_review)

        self.ticket_btn = QPushButton("🎫 مدیریت تیکت‌ها")
        self.ticket_btn.setObjectName("secondaryBtn")
        self.ticket_btn.clicked.connect(self.open_tickets)

        # دکمه جدید برای ثبت فرم
        self.form_reg_btn = QPushButton("📝 ثبت فرم جدید")
        self.form_reg_btn.setObjectName("secondaryBtn")
        self.form_reg_btn.clicked.connect(self.open_form_registration)

        self.logout_btn = QPushButton("❌ خروج")
        self.logout_btn.setObjectName("dangerBtn")
        self.logout_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.review_btn)
        btn_layout.addWidget(self.ticket_btn)
        btn_layout.addWidget(self.form_reg_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.logout_btn)

        main_layout.addLayout(btn_layout)

        # محل اضافه‌کردن ویجت‌های دیگر
        placeholder = QLabel("از منوی بالا می‌توانید اسناد را بررسی، تیکت‌ها را مدیریت و یا فرم‌های جدید ثبت کنید.")
        placeholder.setObjectName("placeholderLabel")
        placeholder.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(placeholder)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget#staffRoot {
                background-color: #121212;
                color: #f0f0f0;
            }

            QLabel#staffHeader {
                font-size: 20px;
                font-weight: bold;
                color: #ffffff;
            }

            QLabel#staffSubHeader {
                font-size: 13px;
                color: #bbbbbb;
            }

            QLabel#placeholderLabel {
                font-size: 12px;
                color: #888888;
            }

            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
                font-size: 13px;
            }

            QPushButton#primaryBtn {
                background-color: #00b894;
                color: white;
            }
            QPushButton#primaryBtn:hover {
                background-color: #00a183;
            }

            QPushButton#secondaryBtn {
                background-color: #141824;
                color: #f0f0f0;
            }
            QPushButton#secondaryBtn:hover {
                background-color: #1f2330;
            }

            QPushButton#dangerBtn {
                background-color: transparent;
                color: #ff7675;
                border: 1px solid #ff7675;
            }
            QPushButton#dangerBtn:hover {
                background-color: rgba(255,118,117,0.12);
            }

            QFrame {
                background-color: #333333;
            }
        """)

    def open_review(self):
        if self.review_window is None:
            self.review_window = ReviewDocuments(self.user_data)
        self.review_window.show()
        self.review_window.raise_()
        self.review_window.activateWindow()

    def open_tickets(self):
        if self.ticket_window is None:
            self.ticket_window = TicketManager(self.user_data)
        self.ticket_window.show()
        self.ticket_window.raise_()
        self.ticket_window.activateWindow()

    def open_form_registration(self):
        if self.form_window is None:
            self.form_window = FormRegistration(self.user_data)
        self.form_window.show()
        self.form_window.raise_()
        self.form_window.activateWindow()
