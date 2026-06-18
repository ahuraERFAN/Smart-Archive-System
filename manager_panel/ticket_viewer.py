import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QTextEdit, QSplitter, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt

class ManagerTicketViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظارت بر تیکت‌ها (فقط خواندنی)")
        self.resize(850, 600)

        layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Vertical)

        # جدول نمایش تیکت ها
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "شناسه سند", "شناسه کاربر", "وضعیت", "تاریخ ایجاد"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self.load_ticket_messages)
        splitter.addWidget(self.table)

        # نمایش پیام ها
        self.message_view = QTextEdit()
        self.message_view.setReadOnly(True)
        splitter.addWidget(self.message_view)

        layout.addWidget(splitter)
        
        self.apply_dark_theme()
        self.load_tickets()

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #0d0f1a;
                color: #e6e6e6;
                font-family: Tahoma;
            }
            QTableWidget {
                background-color: #161b2b;
                color: #ffffff;
                border: 1px solid #20263a;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #1f2638;
                color: #00bfff;
                padding: 5px;
                border: 1px solid #20263a;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #161b2b;
                color: #ffffff;
                border: 1px solid #20263a;
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
            }
        """)

    def load_tickets(self):
        try:
            conn = sqlite3.connect("database/archive.db")
            cur = conn.cursor()
            cur.execute("""
                SELECT id, document_id, user_id, status, created_at
                FROM tickets
                ORDER BY id DESC
            """)
            tickets = cur.fetchall()
            conn.close()

            self.table.setRowCount(0)
            for row_idx, ticket in enumerate(tickets):
                self.table.insertRow(row_idx)
                for col_idx, item_data in enumerate(ticket):
                    item = QTableWidgetItem(str(item_data))
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    self.table.setItem(row_idx, col_idx, item)
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری تیکت‌ها: {e}")

    def load_ticket_messages(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        ticket_id = self.table.item(selected_row, 0).text()
        self.message_view.clear()

        try:
            conn = sqlite3.connect("database/archive.db")
            cur = conn.cursor()
            
            cur.execute("SELECT message FROM tickets WHERE id = ?", (ticket_id,))
            initial_message = cur.fetchone()
            if initial_message:
                self.message_view.append(f"🔴 پیام اولیه کاربر:\n{initial_message[0]}\n{'-'*40}")

            cur.execute("""
                SELECT sender_id, message, created_at
                FROM ticket_messages
                WHERE ticket_id = ?
                ORDER BY id ASC
            """, (ticket_id,))
            messages = cur.fetchall()
            conn.close()

            for sender, text, time in messages:
                role = "کاربر" if str(sender) != "staff" else "کارمند"
                self.message_view.append(f"🟢 ({role}) - {time}:\n{text}\n{'-'*40}")
                
        except Exception as e:
            self.message_view.append(f"خطا در بارگذاری پیام‌ها: {e}")
