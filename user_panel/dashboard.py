from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton,
    QMessageBox, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt

from user_panel.upload_form import UploadForm
from user_panel.user_documents import UserDocuments
from user_panel.ticket_history import TicketHistory

class UserDashboard(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.upload_window = None
        self.docs_window = None
        self.ticket_window = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("پنل کاربری - دارک مود")
        self.resize(600, 480)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # --- بخش هدر ---
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        
        welcome_label = QLabel(f"خوش آمدید، {self.user_data.get('full_name')} ✌️")
        welcome_label.setObjectName("welcomeLabel")
        welcome_label.setAlignment(Qt.AlignCenter)
        
        role_label = QLabel("نقش شما: کاربر عادی")
        role_label.setObjectName("roleLabel")
        role_label.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(welcome_label)
        header_layout.addWidget(role_label)
        main_layout.addWidget(header_frame)

        # --- گرید دکمه‌ها ---
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        btn_upload = QPushButton("📄\nثبت سند جدید")
        btn_upload.setObjectName("actionBtn")
        btn_upload.setCursor(Qt.PointingHandCursor)
        btn_upload.clicked.connect(self.open_upload_form)
        grid_layout.addWidget(btn_upload, 0, 0)

        btn_docs = QPushButton("🗂️\nاسناد من")
        btn_docs.setObjectName("actionBtn")
        btn_docs.setCursor(Qt.PointingHandCursor)
        btn_docs.clicked.connect(self.open_my_documents)
        grid_layout.addWidget(btn_docs, 0, 1)

        btn_tickets = QPushButton("🎫\nتیکت‌های من")
        btn_tickets.setObjectName("actionBtn")
        btn_tickets.setCursor(Qt.PointingHandCursor)
        btn_tickets.clicked.connect(self.open_tickets)
        grid_layout.addWidget(btn_tickets, 1, 0)

        btn_logout = QPushButton("🚪\nخروج از حساب")
        btn_logout.setObjectName("logoutBtn")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.clicked.connect(self.logout)
        grid_layout.addWidget(btn_logout, 1, 1)

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }
            QFrame#headerFrame {
                background-color: #1e1e1e;
                border-radius: 12px;
                border: 1px solid #333333;
                padding: 20px;
            }
            QLabel#welcomeLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel#roleLabel {
                font-size: 14px;
                color: #a0a0a0;
                margin-top: 5px;
            }
            QPushButton#actionBtn {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #333333;
                border-radius: 15px;
                padding: 20px;
                min-height: 100px;
            }
            QPushButton#actionBtn:hover {
                background-color: #2980b9;
                border-color: #3498db;
                color: white;
            }
            QPushButton#logoutBtn {
                background-color: #1e1e1e;
                color: #e74c3c;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #c0392b;
                border-radius: 15px;
                padding: 20px;
                min-height: 100px;
            }
            QPushButton#logoutBtn:hover {
                background-color: #c0392b;
                color: white;
            }
        """)

    def open_upload_form(self):
        if self.upload_window is None: self.upload_window = UploadForm(self.user_data)
        self.upload_window.show()

    def open_my_documents(self):
        if self.docs_window is None: self.docs_window = UserDocuments(self.user_data)
        self.docs_window.show()

    def open_tickets(self):
        if self.ticket_window is None: self.ticket_window = TicketHistory(self.user_data)
        self.ticket_window.show()

    def logout(self):
        QMessageBox.information(self, "خروج", "با موفقیت خارج شدید.")
        self.close()
