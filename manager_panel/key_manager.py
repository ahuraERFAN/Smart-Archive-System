import string
import random
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton, QMessageBox, QDialog, QLineEdit, QApplication
)
from PyQt5.QtCore import Qt
from database.db import get_connection

class AddKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("افزودن کلید API")
        self.resize(450, 200)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e2e; color: #cdd6f4; font-family: Tahoma; }
            QLabel { font-size: 14px; color: #cdd6f4; }
            QLineEdit {
                background-color: #313244; color: #cdd6f4;
                border: 1px solid #45475a; border-radius: 5px; padding: 6px;
            }
            QPushButton {
                background-color: #89b4fa; color: #11111b;
                border-radius: 5px; padding: 8px 15px; font-weight: bold;
            }
            QPushButton:hover { background-color: #b4befe; }
        """)

        layout = QVBoxLayout(self)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("کلید API...")
        
        btn_generate = QPushButton("تولید خودکار کلید امن")
        btn_generate.clicked.connect(self.generate_key)
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(self.key_input)
        key_layout.addWidget(btn_generate)
        
        layout.addWidget(QLabel("کلید API:"))
        layout.addLayout(key_layout)

        layout.addWidget(QLabel("توضیحات:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("توضیحات (اختیاری)...")
        layout.addWidget(self.desc_input)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("ذخیره")
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("لغو")
        btn_cancel.setStyleSheet("background-color: #f38ba8; color: #11111b;")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def generate_key(self):
        chars = string.ascii_letters + string.digits
        secure_key = ''.join(random.choice(chars) for _ in range(32))
        self.key_input.setText(secure_key)

    def get_data(self):
        return self.key_input.text().strip(), self.desc_input.text().strip()


class KeyManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget { background-color: #1e1e2e; color: #cdd6f4; font-family: Tahoma; }
            QTableWidget {
                background-color: #313244; color: #cdd6f4;
                border: 1px solid #45475a; border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #45475a; color: #cdd6f4; padding: 6px; border: none; font-weight: bold;
            }
            QPushButton {
                background-color: #89b4fa; color: #11111b;
                border-radius: 5px; padding: 8px 15px; font-weight: bold;
            }
            QPushButton:hover { background-color: #b4befe; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        title = QLabel("مدیریت کلیدهای API")
        title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #89b4fa; background: transparent;")
        layout.addWidget(title)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_refresh = QPushButton("↻ بروزرسانی")
        self.btn_refresh.clicked.connect(self.load_keys)

        self.btn_add = QPushButton("+ کلید جدید")
        self.btn_add.clicked.connect(self.add_key)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_refresh)
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "کلید (Key)", "توضیحات", "تاریخ ایجاد"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setColumnHidden(0, True) # پنهان کردن ستون ID بر اساس درخواست شما
        layout.addWidget(self.table)

        bottom_layout = QHBoxLayout()
        self.btn_copy = QPushButton("کپی کلید")
        self.btn_copy.setStyleSheet("background-color: #a6e3a1; color: #11111b;")
        self.btn_copy.clicked.connect(self.copy_key)
        
        self.btn_delete = QPushButton("حذف کلید")
        self.btn_delete.setStyleSheet("background-color: #f38ba8; color: #11111b;")
        self.btn_delete.clicked.connect(self.delete_key)
        
        bottom_layout.addWidget(self.btn_copy)
        bottom_layout.addWidget(self.btn_delete)
        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)

        self.load_keys()

    def load_keys(self):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, key_code, description, created_at FROM archive_keys ORDER BY id DESC")
            rows = cur.fetchall()
        finally:
            conn.close()

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            # رفع خطای مربوط به sqlite3.Row با استفاده از براکت به جای متد get
            desc = row["description"] or ""
            created_at = row["created_at"] or ""
            
            data = [row["id"], row["key_code"], desc, created_at]
            for c, val in enumerate(data):
                item = QTableWidgetItem(str(val))
                self.table.setItem(r, c, item)
        self.table.resizeColumnsToContents()

    def add_key(self):
        dialog = AddKeyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            key_code, description = dialog.get_data()
            if not key_code:
                QMessageBox.warning(self, "خطا", "کلید نمی‌تواند خالی باشد.")
                return

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO archive_keys (key_code, description) VALUES (?, ?)",
                    (key_code, description or None)
                )
                conn.commit()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در افزودن کلید:\n{e}")
            finally:
                conn.close()
            self.load_keys()

    def get_selected_row_data(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "انتخاب", "لطفاً یک سطر را از جدول انتخاب کنید.")
            return None, None
        key_id = int(self.table.item(row, 0).text())
        key_code = self.table.item(row, 1).text()
        return key_id, key_code

    def copy_key(self):
        _, key_code = self.get_selected_row_data()
        if key_code:
            QApplication.clipboard().setText(key_code)
            QMessageBox.information(self, "کپی شد", "کلید در حافظه موقت کپی شد.")

    def delete_key(self):
        key_id, _ = self.get_selected_row_data()
        if key_id is None:
            return
        reply = QMessageBox.question(self, 'تایید حذف', 'آیا از حذف این کلید اطمینان دارید؟ این عمل غیرقابل بازگشت است.', 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM archive_keys WHERE id = ?", (key_id,))
                conn.commit()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف کلید:\n{e}")
            finally:
                conn.close()
            self.load_keys()
