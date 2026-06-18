from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget,
    QTextEdit, QSplitter, QPushButton, QGroupBox
)
from PyQt5.QtCore import Qt
from tickets.ticket_service import get_user_tickets

class TicketHistory(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_id = user_data["id"]
        self.tickets = []
        self.init_ui()
        self.load_tickets()

    def init_ui(self):
        self.setWindowTitle("تاریخچه تیکت‌ها")
        self.resize(850, 600)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header = QLabel("تیکت‌های پشتیبانی شما")
        header.setObjectName("headerLabel")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setSizes([300, 550])

        # --- لیست تیکت‌ها ---
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        self.ticket_list = QListWidget()
        self.ticket_list.setObjectName("ticketList")
        self.ticket_list.currentRowChanged.connect(self.show_ticket)
        list_layout.addWidget(self.ticket_list)

        btn_reload = QPushButton("🔄 به‌روزرسانی")
        btn_reload.setObjectName("refreshBtn")
        btn_reload.clicked.connect(self.load_tickets)
        list_layout.addWidget(btn_reload)

        splitter.addWidget(list_widget)

        # --- جزئیات تیکت ---
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(10, 0, 0, 0)

        msg_group = QGroupBox("✉️ متن پیام شما")
        msg_layout = QVBoxLayout()
        self.message_box = QTextEdit()
        self.message_box.setReadOnly(True)
        msg_layout.addWidget(self.message_box)
        msg_group.setLayout(msg_layout)
        details_layout.addWidget(msg_group)

        res_group = QGroupBox("👨‍💻 پاسخ تیم پشتیبانی")
        res_layout = QVBoxLayout()
        self.response_box = QTextEdit()
        self.response_box.setReadOnly(True)
        res_layout.addWidget(self.response_box)
        res_group.setLayout(res_layout)
        details_layout.addWidget(res_group)

        splitter.addWidget(details_widget)
        main_layout.addWidget(splitter)
        
        self.setLayout(main_layout)
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                font-family: 'Segoe UI', Tahoma, sans-serif;
                color: #e0e0e0;
            }
            QLabel#headerLabel { font-size: 24px; font-weight: bold; color: #ffffff; }
            QSplitter::handle { background-color: #333333; width: 2px; }
            
            QListWidget#ticketList {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 5px;
                font-size: 14px;
                outline: none;
            }
            QListWidget#ticketList::item {
                padding: 15px;
                border-bottom: 1px solid #2b2b2b;
            }
            QListWidget#ticketList::item:selected {
                background-color: #d35400;
                color: white;
                border-radius: 6px;
            }
            
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #3498db;
                border: 1px solid #333333;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #121212;
            }
            
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 12px;
                color: #ecf0f1;
                font-size: 14px;
            }
            
            QPushButton#refreshBtn {
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                background-color: #34495e;
                color: white;
                border: none;
            }
            QPushButton#refreshBtn:hover { background-color: #2c3e50; }
        """)

    def load_tickets(self):
        self.tickets = get_user_tickets(self.user_id)
        self.ticket_list.clear()
        for t in self.tickets:
            self.ticket_list.addItem(f"تیکت #{t['id']}\nوضعیت: {self.get_status_fa(t['status'])}")
        self.show_ticket(-1)

    def get_status_fa(self, status):
        status_map = {"open": "باز 🟢", "pending": "در حال بررسی ⏳", "closed": "بسته شده 🔴", "answered": "پاسخ داده شده ✅"}
        return status_map.get(status.lower(), status)

    def show_ticket(self, index):
        if index == -1 or index >= len(self.tickets):
            self.message_box.setText("")
            self.response_box.setText("")
            return
        ticket = self.tickets[index]
        self.message_box.setText(ticket["message"])
        
        if ticket["response"]:
            self.response_box.setText(ticket["response"])
            self.response_box.setStyleSheet("border: 1px solid #2ecc71; background-color: #1a251f;") # حاشیه سبز تیره
        else:
            self.response_box.setText("هنوز پاسخی ثبت نشده است ⏳")
            self.response_box.setStyleSheet("border: 1px solid #e67e22; background-color: #2a2015; color: #f39c12;") # حاشیه نارنجی تیره
