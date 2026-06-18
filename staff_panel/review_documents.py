import os
import subprocess
import sys
import json

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QMessageBox,
    QTextEdit, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt

from database.db import get_connection
try:
    from ocr_engine.ocr_reader import read_text
    from ocr_engine.field_extractor import extract_fields
except Exception:
    read_text = None
    extract_fields = None


class ReviewDocuments(QWidget):
    def __init__(self, staff_data):
        super().__init__()
        self.staff_data = staff_data
        self.staff_id = staff_data.get("id")

        self.setWindowTitle("بررسی اسناد")
        self.setMinimumSize(800, 600)
        self.setObjectName("reviewRoot")

        self.documents = []

        self.init_ui()
        self.apply_styles()
        self.load_documents()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        title = QLabel("لیست اسناد در انتظار بررسی")
        title.setObjectName("sectionTitle")
        main_layout.addWidget(title)

        # لیست اسناد + دکمه‌ها در بالا
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        self.doc_list = QListWidget()
        self.doc_list.setObjectName("docList")
        # اتصال رویداد کلیک روی لیست برای نمایش توضیحات
        self.doc_list.currentRowChanged.connect(self.show_document_details)
        top_layout.addWidget(self.doc_list, 3)

        btn_col = QVBoxLayout()
        btn_col.setSpacing(6)

        self.reload_btn = QPushButton("🔄 بارگذاری اسناد")
        self.reload_btn.setObjectName("secondaryBtn")
        self.reload_btn.clicked.connect(self.load_documents)

        self.open_btn = QPushButton("📂 باز کردن فایل")
        self.open_btn.setObjectName("secondaryBtn")
        self.open_btn.clicked.connect(self.open_file)

        self.ocr_btn = QPushButton("🧾 اجرای OCR")
        self.ocr_btn.setObjectName("secondaryBtn")
        self.ocr_btn.clicked.connect(self.run_ocr)

        self.approve_btn = QPushButton("✅ تایید سند")
        self.approve_btn.setObjectName("approveBtn")
        self.approve_btn.clicked.connect(self.approve_document)

        self.reject_btn = QPushButton("❌ رد سند")
        self.reject_btn.setObjectName("rejectBtn")
        self.reject_btn.clicked.connect(self.reject_document)

        btn_col.addWidget(self.reload_btn)
        btn_col.addWidget(self.open_btn)
        btn_col.addWidget(self.ocr_btn)
        btn_col.addStretch()
        btn_col.addWidget(self.approve_btn)
        btn_col.addWidget(self.reject_btn)

        top_layout.addLayout(btn_col, 1)
        main_layout.addLayout(top_layout)

        # ---------------- بخش توضیحات کاربر ----------------
        desc_label = QLabel("توضیحات کاربر:")
        desc_label.setObjectName("sectionTitle")
        main_layout.addWidget(desc_label)

        self.user_desc_view = QTextEdit()
        self.user_desc_view.setObjectName("textArea")
        self.user_desc_view.setReadOnly(True)
        main_layout.addWidget(self.user_desc_view)
        # ---------------------------------------------------

        # بخش OCR
        ocr_label = QLabel("متن استخراج شده (OCR)")
        ocr_label.setObjectName("sectionTitle")
        main_layout.addWidget(ocr_label)

        self.ocr_text_view = QTextEdit()
        self.ocr_text_view.setObjectName("textArea")
        self.ocr_text_view.setReadOnly(False)
        main_layout.addWidget(self.ocr_text_view, 2)

        # بخش فیلدها
        fields_label = QLabel("اطلاعات استخراج شده")
        fields_label.setObjectName("sectionTitle")
        main_layout.addWidget(fields_label)

        self.fields_view = QTextEdit()
        self.fields_view.setObjectName("textArea")
        self.fields_view.setReadOnly(False)
        main_layout.addWidget(self.fields_view, 2)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget#reviewRoot {
                background-color: #121212;
                color: #f0f0f0;
            }
            QLabel#sectionTitle {
                font-size: 13px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 4px;
                margin-top: 5px;
            }
            QListWidget#docList {
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
                font-family: Consolas, monospace;
                font-size: 12px;
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
            QPushButton#rejectBtn {
                background-color: transparent;
                color: #ff7675;
                border: 1px solid #ff7675;
            }
            QPushButton#rejectBtn:hover {
                background-color: rgba(255,118,117,0.12);
            }
        """)

    def load_documents(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, title, description, file_path, status
                FROM documents
                WHERE status = 'pending'
                ORDER BY id DESC
            """)
            rows = cursor.fetchall()
            conn.close()

            self.documents = rows
            self.doc_list.clear()

            if not rows:
                self.doc_list.addItem("هیچ سندی در انتظار بررسی نیست.")
                self.doc_list.setEnabled(False)
            else:
                self.doc_list.setEnabled(True)
                for doc in rows:
                    doc_id = doc["id"] if isinstance(doc, dict) else doc[0]
                    title = doc["title"] if isinstance(doc, dict) else doc[1]
                    status = doc["status"] if isinstance(doc, dict) else doc[4]
                    self.doc_list.addItem(f"#{doc_id} | {title} | وضعیت: {status}")

            self.clear_fields()

        except Exception as e:
            QMessageBox.critical(self, "خطا در بارگذاری اسناد", str(e))

    def show_document_details(self, index):
        if index == -1 or not self.documents:
            return

        doc = self.documents[index]
        description = doc["description"] if isinstance(doc, dict) else doc[2]
        
        if description and str(description).strip():
            self.user_desc_view.setPlainText(str(description))
        else:
            self.user_desc_view.setPlainText("کاربر توضیحاتی برای این فرم ثبت نکرده است.")
            
        self.ocr_text_view.clear()
        self.fields_view.clear()

    def clear_fields(self):
        self.user_desc_view.clear()
        self.ocr_text_view.clear()
        self.fields_view.clear()

    def get_selected_doc(self):
        idx = self.doc_list.currentRow()
        if idx == -1 or not self.documents or len(self.documents) == 0:
            QMessageBox.warning(self, "هشدار", "لطفاً یک سند را انتخاب کنید.")
            return None
        return self.documents[idx]

    def open_file(self):
        doc = self.get_selected_doc()
        if not doc:
            return

        path = doc["file_path"] if isinstance(doc, dict) else doc[3]

        if not os.path.exists(path):
            QMessageBox.warning(self, "خطا", "فایل پیدا نشد.")
            return

        try:
            if os.name == "nt":  # Windows
                os.startfile(path)
            elif sys.platform == "darwin":  # macOS
                subprocess.call(["open", path])
            else:  # Linux
                subprocess.call(["xdg-open", path])
        except Exception as e:
            QMessageBox.critical(self, "خطا در باز کردن فایل", str(e))

    def run_ocr(self):
        doc = self.get_selected_doc()
        if not doc:
            return

        doc_id = doc["id"] if isinstance(doc, dict) else doc[0]
        path = doc["file_path"] if isinstance(doc, dict) else doc[3]

        if not os.path.exists(path):
            QMessageBox.warning(self, "خطا", "فایل پیدا نشد.")
            return

        if read_text is None or extract_fields is None:
            QMessageBox.warning(self, "OCR غیرفعال است", "ماژول OCR در دسترس نیست. مسیر import را چک کنید.")
            return

        try:
            text = read_text(path)
            extracted_json = extract_fields(text)
            
            try:
                fields = json.loads(extracted_json)
                pretty_fields = json.dumps(fields, indent=4, ensure_ascii=False)
            except:
                pretty_fields = extracted_json

            self.ocr_text_view.setPlainText(text if text else "متنی استخراج نشد.")
            self.fields_view.setPlainText(pretty_fields if pretty_fields else "")

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE documents
            SET ocr_text=?, extracted_json=?
            WHERE id=?
            """, (text, extracted_json, doc_id))
            conn.commit()
            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطا در اجرای OCR", str(e))

    def approve_document(self):
        doc = self.get_selected_doc()
        if not doc:
            return

        doc_id = doc["id"] if isinstance(doc, dict) else doc[0]

        try:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE documents
                    SET status = 'employee_ok',
                        reviewed_by = ?,
                        reviewed_by_role = 'employee'
                    WHERE id = ?
                """, (self.staff_id, doc_id))
            except Exception:
                cursor.execute("UPDATE documents SET status = 'employee_ok' WHERE id = ?", (doc_id,))

            conn.commit()
            conn.close()
            QMessageBox.information(self, "موفق", "سند با موفقیت تایید شد.")
            self.load_documents()

        except Exception as e:
            QMessageBox.critical(self, "خطا در تایید سند", str(e))

    def reject_document(self):
        doc = self.get_selected_doc()
        if not doc:
            return

        doc_id = doc["id"] if isinstance(doc, dict) else doc[0]

        try:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE documents
                    SET status = 'employee_reject',
                        reviewed_by = ?,
                        reviewed_by_role = 'employee'
                    WHERE id = ?
                """, (self.staff_id, doc_id))
            except Exception:
                cursor.execute("UPDATE documents SET status = 'employee_reject' WHERE id = ?", (doc_id,))

            conn.commit()
            conn.close()
            QMessageBox.information(self, "ثبت شد", "سند رد شد.")
            self.load_documents()

        except Exception as e:
            QMessageBox.critical(self, "خطا در رد سند", str(e))
