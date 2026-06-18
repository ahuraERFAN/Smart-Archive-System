from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QTextEdit,
    QPushButton, QMessageBox, QGroupBox, QSplitter, QHBoxLayout
)
from PyQt5.QtCore import Qt
from tickets.ticket_service import get_user_tickets, create_ticket

class TicketHistory(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_id = user_data["id"]
        
        self.init_ui()
        self.load_tickets()

    def init_ui(self):
        self.setWindowTitle("تیکت‌های من")
        self.resize(700, 650)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # عنوان بالا
        header = QLabel("پشتیبانی و تیکت‌ها")
        header.setObjectName("headerLabel")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # --- بخش ارسال تیکت جدید ---
        new_ticket_group = QGroupBox("📝 ارسال تیکت جدید")
        new_ticket_layout = QVBoxLayout()
        
        self.new_ticket_input = QTextEdit()
        self.new_ticket_input.setPlaceholderText("مشکل یا درخواست خود را اینجا با جزئیات بنویسید...")
        self.new_ticket_input.setMaximumHeight(90)
        new_ticket_layout.addWidget(self.new_ticket_input)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_send_ticket = QPushButton("📤 ارسال تیکت")
        self.btn_send_ticket.setObjectName("sendBtn")
        self.btn_send_ticket.setCursor(Qt.PointingHandCursor)
        self.btn_send_ticket.clicked.connect(self.send_new_ticket)
        btn_layout.addWidget(self.btn_send_ticket)
        new_ticket_layout.addLayout(btn_layout)
        
        new_ticket_group.setLayout(new_ticket_layout)
        main_layout.addWidget(new_ticket_group)

        # --- بخش تاریخچه تیکت‌ها ---
        history_group = QGroupBox("🗂️ تاریخچه تیکت‌های شما")
        history_layout = QVBoxLayout()

        splitter = QSplitter(Qt.Horizontal)
        
        # لیست تیکت‌ها (سمت چپ/راست بسته به سیستم)
        self.ticket_list = QListWidget()
        self.ticket_list.setObjectName("ticketList")
        self.ticket_list.currentRowChanged.connect(self.show_ticket)
        splitter.addWidget(self.ticket_list)

        # بخش نمایش محتوای تیکت
        view_widget = QWidget()
        view_layout = QVBoxLayout(view_widget)
        view_layout.setContentsMargins(0, 0, 0, 0)

        view_layout.addWidget(QLabel("متن پیام شما:"))
        self.message_box = QTextEdit()
        self.message_box.setReadOnly(True)
        self.message_box.setObjectName("readOnlyText")
        view_layout.addWidget(self.message_box)

        view_layout.addWidget(QLabel("پاسخ پشتیبانی:"))
        self.response_box = QTextEdit()
        self.response_box.setReadOnly(True)
        self.response_box.setObjectName("responseText")
        view_layout.addWidget(self.response_box)

        splitter.addWidget(view_widget)
        splitter.setSizes([250, 400])
        
        history_layout.addWidget(splitter)
        history_group.setLayout(history_layout)

        main_layout.addWidget(history_group)
        self.setLayout(main_layout)

        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f9;
                font-family: 'Segoe UI', Tahoma, sans-serif;
            }
            QLabel#headerLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
            }
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #34495e;
                border: 1px solid #dcdde1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                background-color: #fff;
                font-size: 13px;
            }
            QTextEdit:focus {
                border: 1px solid #3498db;
            }
            QTextEdit#readOnlyText {
                background-color: #fdfdfd;
                color: #555;
            }
            QTextEdit#responseText {
                background-color: #e8f6f3;
                border: 1px solid #1abc9c;
                color: #16a085;
                font-weight: bold;
            }
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #fff;
                padding: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
                border-radius: 3px;
            }
            QPushButton#sendBtn {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#sendBtn:hover {
                background-color: #2980b9;
            }
        """)

    def send_new_ticket(self):
        text = self.new_ticket_input.toPlainText().strip()
        
        if not text:
            QMessageBox.warning(self, "خطا", "لطفاً متن تیکت را وارد کنید.")
            return
            
        try:
            # ارسال None به عنوان document_id در تیکت‌های عمومی
            create_ticket(self.user_id, None, text)
            QMessageBox.information(self, "موفق", "تیکت شما با موفقیت ارسال شد و در انتظار پاسخ است.")
            self.new_ticket_input.clear()
            self.load_tickets()
        except Exception as e:
            QMessageBox.critical(self, "خطا در ارسال", str(e))

    def load_tickets(self):
        self.tickets = get_user_tickets(self.user_id)
        self.ticket_list.clear()

        for t in self.tickets:
            status = t["status"]
            if status == "pending": status_fa = "در انتظار پاسخ ⏳"
            elif status == "answered": status_fa = "پاسخ داده شده ✅"
            else: status_fa = status
            
            text = f"تیکت #{t['id']}\nوضعیت: {status_fa}"
            self.ticket_list.addItem(text)

    def show_ticket(self, index):
        if index == -1:
            return

        ticket = self.tickets[index]
        self.message_box.setText(ticket["message"])

        if ticket["response"]:
            self.response_box.setText(ticket["response"])
        else:
            self.response_box.setText("مدیر هنوز پاسخی به این تیکت نداده است.")
