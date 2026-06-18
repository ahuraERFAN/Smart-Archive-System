# staff_panel/ticket_manager.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QTextEdit,
    QPushButton, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt

from tickets.ticket_service import get_staff_tickets, reply_ticket


class TicketManager(QWidget):
    def __init__(self, staff_data):
        super().__init__()
        self.staff_id = staff_data["id"]

        self.setWindowTitle("مدیریت تیکت‌ها")
        self.setMinimumSize(800, 550)
        self.setObjectName("ticketRoot")

        self.tickets = []

        self.init_ui()
        self.apply_styles()
        self.load_tickets()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        title = QLabel("تیکت‌های کاربران")
        title.setObjectName("sectionTitle")
        main_layout.addWidget(title)

        # لیست تیکت + دکمه رفرش
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        self.ticket_list = QListWidget()
        self.ticket_list.setObjectName("ticketList")
        self.ticket_list.currentRowChanged.connect(self.show_ticket)
        top_layout.addWidget(self.ticket_list, 3)

        self.reload_btn = QPushButton("🔄 بروزرسانی")
        self.reload_btn.setObjectName("secondaryBtn")
        self.reload_btn.clicked.connect(self.load_tickets)
        top_layout.addWidget(self.reload_btn, 1)

        main_layout.addLayout(top_layout)

        # پیام کاربر
        user_label = QLabel("پیام کاربر")
        user_label.setObjectName("sectionTitle")
        main_layout.addWidget(user_label)

        self.message_box = QTextEdit()
        self.message_box.setObjectName("textArea")
        self.message_box.setReadOnly(True)
        main_layout.addWidget(self.message_box, 2)

        # پاسخ کارمند
        resp_label = QLabel("پاسخ شما")
        resp_label.setObjectName("sectionTitle")
        main_layout.addWidget(resp_label)

        self.response_box = QTextEdit()
        self.response_box.setObjectName("textArea")
        self.response_box.setPlaceholderText("پاسخ خود را بنویسید...")
        main_layout.addWidget(self.response_box, 2)

        # دکمه ارسال
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.send_btn = QPushButton("✅ ارسال پاسخ")
        self.send_btn.setObjectName("approveBtn")
        self.send_btn.clicked.connect(self.send_reply)
        btn_layout.addWidget(self.send_btn)

        main_layout.addLayout(btn_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget#ticketRoot {
                background-color: #121212;
                color: #f0f0f0;
            }

            QLabel#sectionTitle {
                font-size: 13px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 4px;
            }

            QListWidget#ticketList {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 4px;
                color: #f0f0f0;
            }

            QTextEdit#textArea {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 4px;
                color: #f0f0f0;
                font-size: 11px;
            }

            QPushButton {
                padding: 6px 12px;
                border-radius: 4px;
                border: none;
                font-size: 12px;
            }

            QPushButton#secondaryBtn {
                background-color: #141824;
                color: #f0f0f0;
            }
            QPushButton#secondaryBtn:hover {
                background-color: #1f2330;
            }

            QPushButton#approveBtn {
                background-color: #00b894;
                color: #ffffff;
            }
            QPushButton#approveBtn:hover {
                background-color: #00a183;
            }
        """)

    # ---------- منطق تیکت ----------

    def load_tickets(self):
        try:
            # دریافت داده‌ها از سرویس
            try:
                raw_tickets = get_staff_tickets(self.staff_id)
            except TypeError:
                raw_tickets = get_staff_tickets()

            # تبدیل آبجکت‌های دیتابیس به دیکشنری معمولی پایتون
            # این کار باعث می‌شود مشکل تابع get به طور کامل برطرف شود
            self.tickets = [dict(t) for t in raw_tickets] if raw_tickets else []

            self.ticket_list.clear()
            self.message_box.clear()
            self.response_box.clear()

            if not self.tickets:
                self.ticket_list.addItem("هیچ تیکتی برای شما ثبت نشده است.")
                self.ticket_list.setEnabled(False)
            else:
                self.ticket_list.setEnabled(True)
                for t in self.tickets:
                    tid = t["id"]
                    doc_title = t.get("doc_title", "بدون عنوان")
                    user_name = t.get("user_name", "ناشناخته")
                    status = t.get("status", "")
                    self.ticket_list.addItem(f"#{tid} | {doc_title} | کاربر: {user_name} | وضعیت: {status}")

        except Exception as e:
            QMessageBox.critical(self, "خطا در بارگذاری تیکت‌ها", str(e))

    def show_ticket(self, index):
        if index == -1 or not self.tickets:
            return

        ticket = self.tickets[index]
        self.message_box.setPlainText(ticket.get("message", ""))

        resp = ticket.get("response")
        if resp:
            self.response_box.setPlainText(resp)
        else:
            self.response_box.clear()

    def send_reply(self):
        index = self.ticket_list.currentRow()
        if index == -1 or not self.tickets:
            QMessageBox.warning(self, "هشدار", "یک تیکت انتخاب کنید.")
            return

        response = self.response_box.toPlainText().strip()
        if not response:
            QMessageBox.warning(self, "هشدار", "پاسخ خالی است.")
            return

        ticket = self.tickets[index]

        try:
            reply_ticket(
                ticket_id=ticket["id"],
                staff_id=self.staff_id,
                response=response
            )
            QMessageBox.information(self, "موفق", "پاسخ ارسال شد.")
            self.load_tickets()
        except Exception as e:
            QMessageBox.critical(self, "خطا در ارسال پاسخ", str(e))
