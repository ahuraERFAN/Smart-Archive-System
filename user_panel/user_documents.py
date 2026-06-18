import os
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget,
    QPushButton, QMessageBox, QInputDialog, QHBoxLayout, QSplitter
)
from PyQt5.QtCore import Qt
from database.db import get_connection
from tickets.ticket_service import create_ticket

class UserDocuments(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_id = user_data["id"]
        self.documents = []
        self.init_ui()
        self.load_docs()

    def init_ui(self):
        self.setWindowTitle("اسناد من")
        self.resize(850, 600)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header = QLabel("مدیریت اسناد شما")
        header.setObjectName("headerLabel")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setSizes([300, 550])

        # --- بخش لیست ---
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        self.list = QListWidget()
        self.list.setObjectName("docList")
        self.list.currentRowChanged.connect(self.display_doc_details)
        list_layout.addWidget(self.list)

        btn_reload = QPushButton("🔄 به‌روزرسانی لیست")
        btn_reload.setObjectName("refreshBtn")
        btn_reload.clicked.connect(self.load_docs)
        list_layout.addWidget(btn_reload)

        splitter.addWidget(list_widget)

        # --- بخش جزئیات ---
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(10, 0, 0, 0)
        details_layout.setSpacing(15)

        self.doc_title_label = QLabel("عنوان سند: انتخاب نشده")
        self.doc_title_label.setObjectName("detailBox")
        details_layout.addWidget(self.doc_title_label)

        self.doc_status_label = QLabel("وضعیت: انتخاب نشده")
        self.doc_status_label.setObjectName("detailBox")
        details_layout.addWidget(self.doc_status_label)
        
        self.file_path_label = QLabel("مسیر فایل: یافت نشد")
        self.file_path_label.setObjectName("pathBox")
        self.file_path_label.setWordWrap(True)
        details_layout.addWidget(self.file_path_label)

        details_layout.addStretch()

        # دکمه‌های عملیاتی
        action_btn_layout = QHBoxLayout()
        btn_open = QPushButton("📂 باز کردن فایل")
        btn_open.setObjectName("openFileBtn")
        btn_open.setCursor(Qt.PointingHandCursor)
        btn_open.clicked.connect(self.open_file)
        
        btn_ticket = QPushButton("🎫 ارسال تیکت برای این سند")
        btn_ticket.setObjectName("ticketBtn")
        btn_ticket.setCursor(Qt.PointingHandCursor)
        btn_ticket.clicked.connect(self.create_ticket_for_doc)
        
        action_btn_layout.addWidget(btn_open)
        action_btn_layout.addWidget(btn_ticket)
        details_layout.addLayout(action_btn_layout)

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
            QLabel#headerLabel { font-size: 24px; font-weight: bold; color: #ffffff; margin-bottom: 10px; }
            QSplitter::handle { background-color: #333333; width: 2px; }
            
            QListWidget#docList {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 5px;
                font-size: 14px;
                outline: none;
            }
            QListWidget#docList::item {
                padding: 15px;
                border-bottom: 1px solid #2b2b2b;
            }
            QListWidget#docList::item:selected {
                background-color: #2980b9;
                color: white;
                border-radius: 6px;
            }
            
            QLabel#detailBox {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 15px;
                font-size: 15px;
            }
            QLabel#pathBox {
                background-color: #252526;
                border: 1px dashed #555555;
                border-radius: 8px;
                padding: 15px;
                font-size: 13px;
                color: #a0a0a0;
            }
            
            QPushButton { padding: 12px; border-radius: 8px; font-size: 14px; font-weight: bold; }
            QPushButton#refreshBtn { background-color: #34495e; color: white; border: none; }
            QPushButton#refreshBtn:hover { background-color: #2c3e50; }
            
            QPushButton#openFileBtn { background-color: #27ae60; color: white; border: none; }
            QPushButton#openFileBtn:hover { background-color: #2ecc71; }
            
            QPushButton#ticketBtn { background-color: #d35400; color: white; border: none; }
            QPushButton#ticketBtn:hover { background-color: #e67e22; }
        """)

    def load_docs(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, status, file_path FROM documents WHERE user_id = ? ORDER BY created_at DESC", (self.user_id,))
        self.documents = cur.fetchall()
        self.list.clear()
        for d in self.documents:
            self.list.addItem(f"📄 {d['title']}\nوضعیت: {self.get_status_fa(d['status'])}")
        conn.close()
        self.display_doc_details(-1)

    def get_status_fa(self, status):
        if status == "pending": return "در انتظار بررسی ⏳"
        elif status == "approved": return "تأیید شده ✅"
        elif status == "rejected": return "رد شده ❌"
        return status

    def display_doc_details(self, index):
        if index == -1 or index >= len(self.documents):
            self.doc_title_label.setText("عنوان سند: انتخاب نشده")
            self.doc_status_label.setText("وضعیت: انتخاب نشده")
            self.file_path_label.setText("مسیر فایل: یافت نشد")
            return
        doc = self.documents[index]
        self.doc_title_label.setText(f"<b>عنوان سند:</b> {doc['title']}")
        self.doc_status_label.setText(f"<b>وضعیت:</b> {self.get_status_fa(doc['status'])}")
        self.file_path_label.setText(f"<b>مسیر:</b> {doc['file_path']}")

    def get_selected_doc(self):
        idx = self.list.currentRow()
        if idx == -1: return None
        return self.documents[idx]

    def open_file(self):
        doc = self.get_selected_doc()
        if not doc: return
        path = doc["file_path"]
        if not os.path.exists(path):
            QMessageBox.warning(self, "خطا", "فایل پیدا نشد.")
            return
        try:
            if os.name == "nt": os.startfile(path)
            else: subprocess.call(["xdg-open", path])
        except Exception as e:
            QMessageBox.critical(self, "خطا", str(e))

    def create_ticket_for_doc(self):
        doc = self.get_selected_doc()
        if not doc: return
        text, ok = QInputDialog.getMultiLineText(self, "ارسال تیکت", f"مشکل خود درباره سند '{doc['title']}' را بنویسید:")
        if ok and text.strip():
            try:
                # اصلاح تابع برای ارسال هر 3 آرگومان به ترتیب: user_id, document_id, message
                create_ticket(self.user_id, doc['id'], f"سند: {doc['title']}\n\n{text}")
                QMessageBox.information(self, "موفق", "تیکت ثبت شد.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", str(e))
