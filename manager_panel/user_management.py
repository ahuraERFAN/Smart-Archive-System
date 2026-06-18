import string
import random
from utils.security import hash_password
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QHBoxLayout, QPushButton, QMessageBox, QDialog, QLineEdit, QComboBox
)
from PyQt5.QtCore import Qt
from database.db import get_connection

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("افزودن کاربر جدید")
        self.resize(400, 320)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e2e; color: #cdd6f4; font-family: Tahoma; }
            QLabel { font-size: 14px; color: #cdd6f4; font-weight: bold; }
            QLineEdit, QComboBox {
                background-color: #313244; color: #cdd6f4;
                border: 1px solid #45475a; border-radius: 6px; padding: 8px; font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #89b4fa; }
            QComboBox QAbstractItemView {
                background-color: #313244; color: #cdd6f4;
                selection-background-color: #45475a; selection-color: #cdd6f4;
            }
            QPushButton {
                border-radius: 6px; padding: 10px 15px; font-weight: bold; font-size: 13px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("نام کاربری:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("مثال: ali_reza")
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("نام کامل:"))
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("مثال: علیرضا محمدی")
        layout.addWidget(self.fullname_input)

        layout.addWidget(QLabel("نقش کاربر:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["کاربر عادی", "کارمند", "مدیر"])
        layout.addWidget(self.role_combo)

        layout.addWidget(QLabel("رمز عبور:"))
        pass_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("رمز عبور قوی وارد کنید")
        
        btn_generate = QPushButton("تولید رمز")
        btn_generate.setStyleSheet("background-color: #89dceb; color: #11111b; padding: 8px;")
        btn_generate.clicked.connect(self.generate_password)
        
        pass_layout.addWidget(self.password_input)
        pass_layout.addWidget(btn_generate)
        layout.addLayout(pass_layout)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("ذخیره کاربر")
        btn_save.setStyleSheet("background-color: #a6e3a1; color: #11111b;")
        btn_save.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("لغو")
        btn_cancel.setStyleSheet("background-color: #f38ba8; color: #11111b;")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save) 
        layout.addLayout(btn_layout)

    def generate_password(self):
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        secure_pass = ''.join(random.choice(chars) for _ in range(12))
        self.password_input.setText(secure_pass)
        self.password_input.setEchoMode(QLineEdit.Normal)

    def get_data(self):
        role_map = {"مدیر": "manager", "کارمند": "staff", "کاربر عادی": "user"}
        return (
            self.username_input.text().strip(),
            self.fullname_input.text().strip(),
            role_map.get(self.role_combo.currentText(), "user"),
            self.password_input.text().strip()
        )


class UserManagementWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("userMgmtRoot")
        self.setStyleSheet("""
            QWidget#userMgmtRoot { background-color: #1e1e2e; color: #cdd6f4; font-family: Tahoma; }
            QLabel { color: #cdd6f4; }
            QTableWidget {
                background-color: #313244; color: #cdd6f4;
                border: 1px solid #45475a; border-radius: 8px;
                gridline-color: #45475a;
                selection-background-color: #585b70;
                selection-color: #cdd6f4;
            }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #45475a; }
            QHeaderView::section {
                background-color: #181825; color: #a6adc8; 
                padding: 10px; border: none; font-weight: bold; font-size: 13px;
                border-bottom: 2px solid #89b4fa;
            }
            QTableCornerButton::section { background-color: #181825; border: none; }
            QPushButton {
                border-radius: 6px; padding: 8px 16px; font-weight: bold; font-size: 13px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # بخش هدر و دکمه‌های بالا
        header_layout = QHBoxLayout()
        title = QLabel("👥 مدیریت کاربران")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #b4befe;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.btn_refresh = QPushButton("↻ بروزرسانی")
        self.btn_refresh.setStyleSheet("background-color: #89b4fa; color: #11111b;")
        self.btn_refresh.clicked.connect(self.load_users)
        
        self.btn_add = QPushButton("+ افزودن کاربر جدید")
        self.btn_add.setStyleSheet("background-color: #a6e3a1; color: #11111b;")
        self.btn_add.clicked.connect(self.add_user_dialog)

        header_layout.addWidget(self.btn_refresh)
        header_layout.addWidget(self.btn_add)
        layout.addLayout(header_layout)

        # جدول کاربران
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "نام کاربری", "نام کامل", "نقش", "وضعیت"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        layout.addWidget(self.table)

        # دکمه‌های پایین
        bottom_layout = QHBoxLayout()
        
        self.btn_activate = QPushButton("✔️ فعال‌سازی")
        self.btn_activate.setStyleSheet("background-color: #a6e3a1; color: #11111b;")
        self.btn_activate.clicked.connect(self.activate_user)

        self.btn_deactivate = QPushButton("❌ غیرفعال‌سازی")
        self.btn_deactivate.setStyleSheet("background-color: #fab387; color: #11111b;") 
        self.btn_deactivate.clicked.connect(self.deactivate_user)

        self.btn_delete = QPushButton("🗑️ حذف کاربر")
        self.btn_delete.setStyleSheet("background-color: #f38ba8; color: #11111b;") 
        self.btn_delete.clicked.connect(self.delete_user)

        bottom_layout.addWidget(self.btn_activate)
        bottom_layout.addWidget(self.btn_deactivate)
        bottom_layout.addWidget(self.btn_delete)
        bottom_layout.addStretch()
        
        layout.addLayout(bottom_layout)

        self.load_users()

    def show_msg(self, title, text, icon=QMessageBox.Information, buttons=QMessageBox.Ok):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)
        msg.setStandardButtons(buttons)
        
        # استایل پس‌زمینه و متن پیام
        msg.setStyleSheet("""
            QMessageBox { background-color: #1e1e2e; }
            QLabel { color: #cdd6f4; font-size: 13px; font-family: Tahoma; }
        """)

        # استایلی که مستقیماً به خود دکمه‌ها تزریق می‌شود (روش قطعی)
        btn_style = """
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 6px 20px;
                font-family: Tahoma;
                font-size: 13px;
                min-width: 70px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45475a;
                border: 1px solid #89b4fa;
            }
            QPushButton:pressed {
                background-color: #585b70;
            }
        """

        # اعمال نام فارسی و استایل مستقیم روی هر دکمه
        if buttons & QMessageBox.Yes:
            btn = msg.button(QMessageBox.Yes)
            btn.setText("بله")
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.PointingHandCursor)
            
        if buttons & QMessageBox.No:
            btn = msg.button(QMessageBox.No)
            btn.setText("خیر")
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.PointingHandCursor)
            msg.setDefaultButton(QMessageBox.No)
            
        if buttons & QMessageBox.Ok:
            btn = msg.button(QMessageBox.Ok)
            btn.setText("تایید")
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.PointingHandCursor)
            
        if buttons & QMessageBox.Cancel:
            btn = msg.button(QMessageBox.Cancel)
            btn.setText("لغو")
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.PointingHandCursor)

        return msg.exec_()


    def load_users(self):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, username, full_name, role, COALESCE(is_active, 1) AS is_active
                FROM users ORDER BY id
            """)
            rows = cur.fetchall()
        finally:
            conn.close()

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            is_active = row["is_active"]
            status_text = "🟢 فعال" if is_active else "🔴 غیرفعال"
            
            role_val = row["role"]
            role_map_display = {"manager": "مدیر", "admin": "مدیر", "staff": "کارمند", "employee": "کارمند", "user": "کاربر عادی"}
            role_display = role_map_display.get(role_val, role_val or "کاربر عادی")
            
            full_name = row["full_name"] or ""
            
            data = [
                row["id"], row["username"], full_name,
                role_display, status_text
            ]
            for c, val in enumerate(data):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(r, c, item)
                
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)

    def add_user_dialog(self):
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            username, full_name, role, password = dialog.get_data()
            
            if not username or not full_name or not password:
                self.show_msg("خطا", "وارد کردن نام کاربری، نام کامل و رمز عبور الزامی است.", QMessageBox.Warning)
                return
                
            hashed_password = hash_password(password)

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cur.fetchone():
                    self.show_msg("خطا", "این نام کاربری از قبل در سیستم وجود دارد.", QMessageBox.Warning)
                    return
                
                cur.execute(
                    "INSERT INTO users (username, full_name, password_hash, role, is_active) VALUES (?, ?, ?, ?, 1)",
                    (username, full_name, hashed_password, role)
                )
                conn.commit()
                self.show_msg("موفق", "کاربر جدید با موفقیت اضافه شد.", QMessageBox.Information)
            except Exception as e:
                self.show_msg("خطا", f"خطا در ثبت کاربر:\n{e}", QMessageBox.Critical)
            finally:
                conn.close()
            self.load_users()

    def get_selected_user_id(self):
        row = self.table.currentRow()
        if row < 0:
            self.show_msg("انتخاب کاربر", "لطفاً ابتدا یک کاربر را از جدول انتخاب کنید.", QMessageBox.Warning)
            return None
        return int(self.table.item(row, 0).text())

    def _set_user_active(self, active: bool):
        user_id = self.get_selected_user_id()
        if user_id is None:
            return
            
        row = self.table.currentRow()
        username = self.table.item(row, 1).text()
        if username == 'admin':
            self.show_msg("خطا", "تغییر وضعیت مدیر اصلی سیستم (admin) مجاز نیست.", QMessageBox.Warning)
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE users SET is_active = ? WHERE id = ?", (1 if active else 0, user_id))
            conn.commit()
        except Exception as e:
            self.show_msg("خطا", f"خطا در بروزرسانی وضعیت کاربر:\n{e}", QMessageBox.Critical)
        finally:
            conn.close()
        self.load_users()

    def activate_user(self):
        self._set_user_active(True)

    def deactivate_user(self):
        self._set_user_active(False)

    def delete_user(self):
        user_id = self.get_selected_user_id()
        if user_id is None:
            return
            
        row = self.table.currentRow()
        username = self.table.item(row, 1).text()
        
        if username == 'admin':
            self.show_msg("خطا", "شما نمی‌توانید مدیر اصلی (admin) را حذف کنید.", QMessageBox.Warning)
            return

        reply = self.show_msg(
            'تایید حذف', 
            f"آیا از حذف دائم کاربر '{username}' مطمئن هستید؟\nاین عملیات قابل بازگشت نیست!",
            QMessageBox.Question,
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                self.show_msg("موفق", "کاربر با موفقیت از سیستم حذف شد.", QMessageBox.Information)
            except Exception as e:
                self.show_msg("خطا", f"خطا در حذف کاربر:\n{e}", QMessageBox.Critical)
            finally:
                conn.close()
            self.load_users()
