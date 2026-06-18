import sys
import os
import sqlite3
import json
import shutil
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt

class ManagerDocumentArchiver(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("بایگانی نهایی اسناد")
        self.resize(900, 600)

        # پوشه بایگانی نهایی
        self.archive_dir = "final_archive"
        os.makedirs(self.archive_dir, exist_ok=True)

        layout = QVBoxLayout(self)

        # دکمه‌های عملیاتی
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("🔄 بروزرسانی لیست")
        self.btn_refresh.clicked.connect(self.load_pending_documents)
        
        self.btn_archive = QPushButton("📁 بایگانی سند انتخاب شده")
        self.btn_archive.clicked.connect(self.archive_document)
        self.btn_archive.setStyleSheet("background-color: #28a745; color: white;")

        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_archive)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # جدول نمایش اسناد
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "عنوان", "مسیر فایل", "نوع فرم", "اطلاعات استخراج شده", "تاریخ"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # مخفی کردن ستون های مسیر فایل و JSON برای زیبایی بیشتر (اختیاری)
        self.table.setColumnHidden(2, True)
        self.table.setColumnHidden(4, True)
        
        layout.addWidget(self.table)

        self.apply_dark_theme()
        self.load_pending_documents()

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
            QPushButton {
                background-color: #00bfff;
                color: #000000;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0099cc;
            }
        """)

    def load_pending_documents(self):
        self.table.setRowCount(0)
        try:
            conn = sqlite3.connect("database/archive.db")
            cursor = conn.cursor()
            
            # فعلا بدون شرط وضعیت، تا هر ۹ سند شما در جدول نمایش داده شود
            cursor.execute("""
                SELECT id, title, file_path, extracted_json, created_at 
                FROM documents 
            """)
            docs = cursor.fetchall()  # <--- مشکل اینجا بود که docs = را جا انداخته بودم
            conn.close()

            for row_idx, doc in enumerate(docs):
                self.table.insertRow(row_idx)
                
                doc_id = str(doc[0])
                title = str(doc[1])
                file_path = str(doc[2])
                extracted_json_str = str(doc[3])
                created_at = str(doc[4])
                
                # استخراج نوع فرم از JSON
                form_type = "نامشخص"
                if extracted_json_str and extracted_json_str != "None":
                    try:
                        extracted_data = json.loads(extracted_json_str)
                        form_type = extracted_data.get("form_type", "نامشخص")
                    except:
                        pass
                
                # پر کردن ردیف‌های جدول
                self.table.setItem(row_idx, 0, QTableWidgetItem(doc_id))
                self.table.setItem(row_idx, 1, QTableWidgetItem(title))
                self.table.setItem(row_idx, 2, QTableWidgetItem(file_path))
                self.table.setItem(row_idx, 3, QTableWidgetItem(form_type))
                self.table.setItem(row_idx, 4, QTableWidgetItem(extracted_json_str))
                self.table.setItem(row_idx, 5, QTableWidgetItem(created_at))
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری اسناد: {e}")

    def archive_document(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "اخطار", "لطفاً یک سند را برای بایگانی انتخاب کنید.")
            return

        row = selected_rows[0].row()
        doc_id = self.table.item(row, 0).text()
        file_path = self.table.item(row, 2).text()
        form_type = self.table.item(row, 3).text()
        extracted_json_str = self.table.item(row, 4).text()

        # استخراج نام و نام خانوادگی از JSON
        full_name = "نامشخص"
        if extracted_json_str and extracted_json_str != "None":
            try:
                extracted_data = json.loads(extracted_json_str)
                full_name = extracted_data.get("full_name", "نامشخص")
            except:
                pass

        form_name_mapping = {"form1": "فرم اول", "form2": "فرم دوم", "form3": "فرم سوم"}
        persian_form_type = form_name_mapping.get(form_type, form_type)

        date_str = datetime.now().strftime("%Y%m%d")
        _, ext = os.path.splitext(file_path)
        new_filename = f"{date_str}_{full_name}_{persian_form_type}{ext}"
        
        # جایگزینی کاراکترهای غیرمجاز در نام فایل
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            new_filename = new_filename.replace(char, '')

        dest_path = os.path.join(self.archive_dir, new_filename)

        try:
            if os.path.exists(file_path):
                shutil.copy2(file_path, dest_path)
            else:
                QMessageBox.warning(self, "خطا", "فایل اصلی در مسیر یافت نشد!")
                return

            # تغییر وضعیت به archived
            conn = sqlite3.connect("database/archive.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE documents SET status = 'archived' WHERE id = ?", (doc_id,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "موفق", f"سند با موفقیت با نام\n{new_filename}\nبایگانی شد.")
            self.load_pending_documents()

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در عملیات بایگانی: {e}")
