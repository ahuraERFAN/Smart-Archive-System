# staff_panel/form_registration.py
import os
import shutil
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QFileDialog, QListWidget, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt

# فرض بر این است که تابع ارتباط با دیتابیس در مسیر زیر قرار دارد
from database.db import get_connection

class FormRegistration(QWidget):
    def __init__(self, staff_data):
        super().__init__()
        self.staff_data = staff_data
        self.staff_id = staff_data.get("id")
        self.selected_file_path = None

        self.setWindowTitle("ثبت و مدیریت فرم‌ها")
        self.setMinimumSize(850, 600)
        self.setObjectName("formRoot")

        self.init_ui()
        self.apply_styles()
        self.load_forms() # بارگذاری اولیه فرم‌های ثبت شده

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # ==========================================
        # پنل سمت چپ: لیست فرم‌های ثبت شده (نمایش زنده)
        # ==========================================
        left_panel = QVBoxLayout()
        
        list_title = QLabel("📋 فرم‌های ثبت شده اخیر")
        list_title.setObjectName("sectionTitle")
        left_panel.addWidget(list_title)

        self.form_list = QListWidget()
        self.form_list.setObjectName("formList")
        left_panel.addWidget(self.form_list)

        self.refresh_btn = QPushButton("🔄 بروزرسانی لیست")
        self.refresh_btn.setObjectName("secondaryBtn")
        self.refresh_btn.clicked.connect(self.load_forms)
        left_panel.addWidget(self.refresh_btn)

        # ==========================================
        # پنل سمت راست: ثبت فرم جدید
        # ==========================================
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        create_title = QLabel("📝 ثبت فرم جدید")
        create_title.setObjectName("sectionTitle")
        right_panel.addWidget(create_title)

        # عنوان فرم
        self.title_input = QLineEdit()
        self.title_input.setObjectName("inputField")
        self.title_input.setPlaceholderText("عنوان فرم را وارد کنید...")
        right_panel.addWidget(self.title_input)

        # بخش آپلود فایل
        file_layout = QHBoxLayout()
        self.file_label = QLabel("فایلی انتخاب نشده است (پشتیبانی از PNG, PDF و...)")
        self.file_label.setObjectName("fileLabel")
        
        self.upload_btn = QPushButton("📁 انتخاب فایل فرم")
        self.upload_btn.setObjectName("secondaryBtn")
        self.upload_btn.clicked.connect(self.select_file)
        
        file_layout.addWidget(self.upload_btn)
        file_layout.addWidget(self.file_label, 1) # 1 برای گرفتن فضای بیشتر
        right_panel.addLayout(file_layout)

        # توضیحات متنی
        desc_label = QLabel("توضیحات و دستورالعمل فرم:")
        desc_label.setObjectName("subTitle")
        right_panel.addWidget(desc_label)

        self.desc_input = QTextEdit()
        self.desc_input.setObjectName("textArea")
        self.desc_input.setPlaceholderText("توضیحات مربوط به نحوه پر کردن این فرم را بنویسید...")
        right_panel.addWidget(self.desc_input)

        # دکمه ثبت نهایی
        self.submit_btn = QPushButton("✅ ثبت و انتشار فرم")
        self.submit_btn.setObjectName("primaryBtn")
        self.submit_btn.setMinimumHeight(40)
        self.submit_btn.clicked.connect(self.submit_form)
        right_panel.addWidget(self.submit_btn)

        # اضافه کردن پنل‌ها به لیوت اصلی (نسبت 1 به 1.5)
        main_layout.addLayout(left_panel, 1)
        
        # خط جداکننده عمودی
        v_line = QFrame()
        v_line.setFrameShape(QFrame.VLine)
        v_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(v_line)
        
        main_layout.addLayout(right_panel, 2)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget#formRoot {
                background-color: #121212;
                color: #f0f0f0;
            }
            QLabel#sectionTitle {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 5px;
            }
            QLabel#subTitle {
                font-size: 13px;
                color: #bbbbbb;
            }
            QLabel#fileLabel {
                font-size: 12px;
                color: #888888;
                font-style: italic;
            }
            QLineEdit#inputField {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-size: 13px;
            }
            QTextEdit#textArea, QListWidget#formList {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 4px;
                color: #f0f0f0;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
                font-size: 13px;
                font-weight: bold;
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
                border: 1px solid #2a3040;
            }
            QPushButton#secondaryBtn:hover {
                background-color: #1f2330;
            }
            QFrame {
                background-color: #333333;
            }
        """)

    def select_file(self):
        # فیلتر برای فایل‌های تصویر و اسناد
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "انتخاب فایل فرم", 
            "", 
            "Images (*.png *.jpg *.jpeg);;Documents (*.pdf *.doc *.docx);;All Files (*)", 
            options=options
        )
        if file_path:
            self.selected_file_path = file_path
            filename = os.path.basename(file_path)
            self.file_label.setText(f"فایل انتخاب شد: {filename}")
            self.file_label.setStyleSheet("color: #00b894; font-weight: bold; font-style: normal;")

    def submit_form(self):
        title = self.title_input.text().strip()
        description = self.desc_input.toPlainText().strip()

        if not title:
            QMessageBox.warning(self, "خطا", "لطفاً عنوان فرم را وارد کنید.")
            return
        if not self.selected_file_path:
            QMessageBox.warning(self, "خطا", "لطفاً فایل فرم را انتخاب کنید.")
            return

        try:
            # ایجاد پوشه آپلود در صورت عدم وجود
            upload_dir = "uploads/registered_forms"
            os.makedirs(upload_dir, exist_ok=True)

            # کپی فایل به پوشه پروژه
            filename = os.path.basename(self.selected_file_path)
            # جلوگیری از تداخل نام‌ها با اضافه کردن تایم استمپ
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            saved_filename = f"{timestamp}_{filename}"
            dest_path = os.path.join(upload_dir, saved_filename)
            
            shutil.copy(self.selected_file_path, dest_path)

            # ذخیره در دیتابیس
            conn = get_connection()
            cursor = conn.cursor()
            
            # فرض می‌کنیم جدولی به نام registered_forms برای این منظور ایجاد کرده‌اید
            # فیلدها: id, title, description, file_path, creator_id, created_at, status
            cursor.execute("""
                INSERT INTO registered_forms (title, description, file_path, creator_id, status)
                VALUES (?, ?, ?, ?, 'active')
            """, (title, description, dest_path, self.staff_id))
            
            conn.commit()
            conn.close()

            QMessageBox.information(self, "موفق", "فرم با موفقیت ثبت شد و در سیستم قرار گرفت.")
            
            # پاکسازی فرم بعد از ثبت
            self.title_input.clear()
            self.desc_input.clear()
            self.selected_file_path = None
            self.file_label.setText("فایلی انتخاب نشده است (پشتیبانی از PNG, PDF و...)")
            self.file_label.setStyleSheet("color: #888888; font-style: italic;")
            
            # بروزرسانی لیست لایو
            self.load_forms()

        except Exception as e:
            QMessageBox.critical(self, "خطای سیستم", f"خطا در ثبت فرم:\n{str(e)}")

    def load_forms(self):
        """بارگذاری لایو فرم‌های ثبت شده از دیتابیس"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # در صورتی که جدول registered_forms را ساخته‌اید
            # اگر نساخته‌اید باید در فایل ستاپ دیتابیس خود این جدول را اضافه کنید
            cursor.execute("""
                SELECT id, title, status 
                FROM registered_forms 
                ORDER BY id DESC LIMIT 20
            """)
            rows = cursor.fetchall()
            conn.close()

            self.form_list.clear()
            if not rows:
                self.form_list.addItem("هیچ فرمی ثبت نشده است.")
            else:
                for row in rows:
                    f_id = row["id"] if isinstance(row, dict) else row[0]
                    f_title = row["title"] if isinstance(row, dict) else row[1]
                    f_status = row["status"] if isinstance(row, dict) else row[2]
                    
                    status_fa = "فعال" if f_status == 'active' else "غیرفعال"
                    self.form_list.addItem(f"📌 #{f_id} | {f_title} ({status_fa})")
                    
        except Exception as e:
            # اگر تیبل هنوز در دیتابیس ساخته نشده باشد این خطا نمایش داده می‌شود
            self.form_list.clear()
            self.form_list.addItem("⚠️ تیبل registered_forms یافت نشد.")
            # چاپ خطا در کنسول برای دیباگ
            print("DB Load Error:", e)
