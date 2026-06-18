import os
import shutil

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QTextEdit, QPushButton, QFileDialog,
    QMessageBox, QHBoxLayout, QComboBox
)
from PyQt5.QtCore import Qt

from database.db import get_connection


class UploadForm(QDialog):

    def __init__(self, user_data):
        super().__init__()

        self.user_id = user_data["id"]
        self.file_path = None

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        self.setWindowTitle("ثبت و ارسال فرم")
        self.resize(520, 500)
        self.setObjectName("dialogWindow")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        header = QLabel("📄 ثبت و ارسال فرم پر شده")
        header.setObjectName("headerLabel")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # 1. انتخاب فرم از لیست فرم‌های کارمندان
        form_label = QLabel("انتخاب فرم:")
        form_label.setObjectName("fieldLabel")
        self.form_combo = QComboBox()
        self.form_combo.setObjectName("comboBox")
        self.load_registered_forms() # فراخوانی فرم‌ها از دیتابیس

        main_layout.addWidget(form_label)
        main_layout.addWidget(self.form_combo)

        # 2. انتخاب روش ثبت (دستی یا سیستمی OCR)
        mode_label = QLabel("روش بررسی و ثبت:")
        mode_label.setObjectName("fieldLabel")
        self.mode_combo = QComboBox()
        self.mode_combo.setObjectName("comboBox")
        self.mode_combo.addItems([
            "دستی (بررسی و تطابق توسط کارمند)", 
            "سیستمی (استخراج اطلاعات با OCR)"
        ])

        main_layout.addWidget(mode_label)
        main_layout.addWidget(self.mode_combo)

        # 3. انتخاب فایل
        file_layout = QHBoxLayout()
        file_label = QLabel("فایل فرم پر شده:")
        file_label.setObjectName("fieldLabel")

        self.file_button = QPushButton("انتخاب فایل")
        self.file_button.setObjectName("secondaryBtn")
        self.file_button.setCursor(Qt.PointingHandCursor)
        self.file_button.clicked.connect(self.select_file)

        file_layout.addWidget(file_label)
        file_layout.addStretch()
        file_layout.addWidget(self.file_button)
        main_layout.addLayout(file_layout)

        # 4. توضیحات
        desc_label = QLabel("توضیحات تکمیلی (اختیاری):")
        desc_label.setObjectName("fieldLabel")

        self.desc_input = QTextEdit()
        self.desc_input.setObjectName("textArea")
        self.desc_input.setPlaceholderText("اگر توضیحاتی برای کارمند یا سیستم دارید اینجا بنویسید...")

        main_layout.addWidget(desc_label)
        main_layout.addWidget(self.desc_input)

        # 5. دکمه‌های تایید و انصراف
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("انصراف")
        cancel_btn.setObjectName("dangerBtn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("ثبت و ارسال")
        save_btn.setObjectName("actionBtn")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.save_document)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)

        main_layout.addLayout(btn_layout)

    def load_registered_forms(self):
        """بارگذاری لیست فرم‌های ثبت شده توسط کارمندان از دیتابیس"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM registered_forms WHERE status = 'active'")
            forms = cursor.fetchall()
            conn.close()

            if forms:
                for form in forms:
                    # پشتیبانی از بازگشت به صورت دیکشنری یا تاپل
                    title = form['title'] if isinstance(form, dict) else form[0]
                    self.form_combo.addItem(title)
            else:
                self.form_combo.addItem("هیچ فرمی توسط کارمندان ثبت نشده است")
                self.form_combo.setEnabled(False)
        except Exception as e:
            self.form_combo.addItem("خطا در بارگذاری فرم‌ها")
            print(f"Error loading forms: {e}")

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog#dialogWindow {
                background-color: #121212;
                color: #f0f0f0;
            }
            QLabel#headerLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel#fieldLabel {
                font-size: 13px;
                color: #bbbbbb;
                margin-top: 5px;
            }
            QComboBox#comboBox {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 8px;
                color: #f0f0f0;
                font-size: 13px;
            }
            QComboBox#comboBox:focus {
                border: 1px solid #00bfff;
            }
            QComboBox::drop-down {
                border-left: 1px solid #333333;
            }
            QTextEdit#textArea {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 6px;
                color: #f0f0f0;
            }
            QTextEdit#textArea:focus {
                border: 1px solid #00bfff;
            }
            QPushButton {
                font-weight: bold;
            }
            QPushButton#secondaryBtn {
                background-color: #141824;
                color: #f0f0f0;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton#secondaryBtn:hover {
                background-color: #1f2330;
            }
            QPushButton#actionBtn {
                background-color: #00b894;
                color: #ffffff;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton#actionBtn:hover {
                background-color: #00a183;
            }
            QPushButton#dangerBtn {
                background-color: transparent;
                color: #ff7675;
                padding: 8px 20px;
                border: 1px solid #ff7675;
                border-radius: 4px;
            }
            QPushButton#dangerBtn:hover {
                background-color: rgba(255,118,117,0.12);
            }
        """)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "انتخاب فایل",
            "",
            "Documents (*.pdf *.docx *.png *.jpg *.jpeg)"
        )

        if file_path:
            self.file_path = file_path
            self.file_button.setText("✅ فایل انتخاب شد")
            self.file_button.setStyleSheet("background-color: #27ae60; color: white;")

    def save_document(self):
        if self.form_combo.count() == 0 or not self.form_combo.isEnabled():
            QMessageBox.warning(self, "خطا", "فرمی برای ثبت وجود ندارد.")
            return

        selected_form = self.form_combo.currentText()
        submission_mode = self.mode_combo.currentText()
        user_description = self.desc_input.toPlainText().strip()

        if not self.file_path:
            QMessageBox.warning(self, "خطا", "لطفاً یک فایل انتخاب کنید")
            return

        # ترکیب عنوان فرم و نوع ثبت برای نمایش در پنل کارمند
        final_title = f"{selected_form} | روش: {submission_mode}"
        
        os.makedirs("uploads", exist_ok=True)
        file_name = os.path.basename(self.file_path)
        destination = os.path.join("uploads", file_name)

        try:
            shutil.copy(self.file_path, destination)

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO documents
                (user_id, title, description, file_path)
                VALUES (?, ?, ?, ?)
            """, (self.user_id, final_title, user_description, destination))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "موفق", "فرم با موفقیت ارسال شد و در انتظار بررسی است.")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ثبت اطلاعات: {str(e)}")
