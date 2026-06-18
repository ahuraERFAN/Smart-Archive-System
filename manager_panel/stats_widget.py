# manager_panel/stats_widget.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QFrame, QGridLayout, QPushButton
)
from PyQt5.QtCore import Qt

from database.db import get_connection

class StatCard(QFrame):
    """ویجت سفارشی برای نمایش کارت‌های آمار"""
    def __init__(self, title, initial_value, color_hex):
        super().__init__()
        
        self.setMinimumHeight(115)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet("""
            font-size: 14px;
            color: #a0aabf;
            font-weight: bold;
        """)
        
        self.lbl_value = QLabel(str(initial_value))
        self.lbl_value.setAlignment(Qt.AlignCenter)
        self.lbl_value.setStyleSheet(f"""
            font-size: 34px;
            font-weight: bold;
            color: {color_hex};
        """)
        
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)
        
        # استایل اختصاصی کارت با نوار رنگی در سمت راست
        self.setStyleSheet(f"""
            StatCard {{
                background-color: #1a1e24;
                border-radius: 10px;
                border-right: 5px solid {color_hex};
                border-top: 1px solid #2b303b;
                border-bottom: 1px solid #2b303b;
                border-left: 1px solid #2b303b;
            }}
            StatCard:hover {{
                background-color: #232830;
                border-right: 8px solid {color_hex};
            }}
        """)

    def set_value(self, val):
        self.lbl_value.setText(str(val))


class StatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("statsRoot")
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.cards = {}
        self.init_ui()
        self.load_stats()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 20)
        main_layout.setSpacing(25)
        
        # --- هدر و دکمه بروزرسانی ---
        header_layout = QHBoxLayout()
        title = QLabel("نمای کلی آمار و وضعیت سیستم")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffffff;")
        
        btn_refresh = QPushButton("↻ بروزرسانی آمار")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        btn_refresh.clicked.connect(self.load_stats)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(btn_refresh)
        main_layout.addLayout(header_layout)
        
        # ------------------------------------------------
        # 1. بخش آمار کاربران (یک ردیف افقی)
        # ------------------------------------------------
        lbl_users = QLabel("👤 وضعیت کاربران")
        lbl_users.setStyleSheet("font-size: 16px; font-weight: bold; color: #b5b5b5;")
        main_layout.addWidget(lbl_users)
        
        users_layout = QHBoxLayout()
        users_layout.setSpacing(15)
        
        self.cards['total_users'] = StatCard("کل کاربران", 0, "#3498db")   # آبی
        self.cards['admins'] = StatCard("مدیران", 0, "#9b59b6")           # بنفش
        self.cards['staff'] = StatCard("کارمندان", 0, "#f39c12")          # نارنجی
        self.cards['normal'] = StatCard("کاربران عادی", 0, "#1abc9c")     # فیروزه‌ای
        
        users_layout.addWidget(self.cards['total_users'])
        users_layout.addWidget(self.cards['admins'])
        users_layout.addWidget(self.cards['staff'])
        users_layout.addWidget(self.cards['normal'])
        main_layout.addLayout(users_layout)
        
        # ------------------------------------------------
        # 2. بخش آمار اسناد (یک ردیف افقی شامل هر ۵ کارت)
        # ------------------------------------------------
        lbl_docs = QLabel("📄 وضعیت اسناد و مدارک")
        lbl_docs.setStyleSheet("font-size: 16px; font-weight: bold; color: #b5b5b5; margin-top: 15px;")
        main_layout.addWidget(lbl_docs)
        
        docs_layout = QHBoxLayout()
        docs_layout.setSpacing(15)
        
        self.cards['total_docs'] = StatCard("کل اسناد", 0, "#ffffff")         # سفید
        self.cards['pending'] = StatCard("در انتظار بررسی", 0, "#f1c40f")      # زرد
        self.cards['staff_app'] = StatCard("تایید شده (کارمند)", 0, "#3498db") # آبی روشن
        self.cards['admin_app'] = StatCard("تایید نهایی (مدیر)", 0, "#2ecc71") # سبز
        self.cards['rejected'] = StatCard("رد شده", 0, "#e74c3c")            # قرمز
        
        # افزودن هر ۵ مورد به یک ردیف
        docs_layout.addWidget(self.cards['total_docs'])
        docs_layout.addWidget(self.cards['pending'])
        docs_layout.addWidget(self.cards['staff_app'])
        docs_layout.addWidget(self.cards['admin_app'])
        docs_layout.addWidget(self.cards['rejected'])
        
        main_layout.addLayout(docs_layout)
        main_layout.addStretch()

    # -------------- Database Helpers --------------

    def _get_count(self, cur, table_name, condition="1=1"):
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {condition}")
            res = cur.fetchone()
            if isinstance(res, dict):
                return list(res.values())[0]
            return res[0]
        except Exception:
            return 0

    def load_stats(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            self.cards['total_users'].set_value(self._get_count(cur, "users"))
            self.cards['admins'].set_value(self._get_count(cur, "users", "role='admin'"))
            self.cards['staff'].set_value(self._get_count(cur, "users", "role='staff'"))
            self.cards['normal'].set_value(self._get_count(cur, "users", "role='user'"))
            
            self.cards['total_docs'].set_value(self._get_count(cur, "documents"))
            self.cards['pending'].set_value(self._get_count(cur, "documents", "status='pending'"))
            self.cards['staff_app'].set_value(self._get_count(cur, "documents", "status='staff_approved'"))
            
            admin_count = self._get_count(cur, "documents", "status IN ('approved', 'admin_approved')")
            self.cards['admin_app'].set_value(admin_count)
            self.cards['rejected'].set_value(self._get_count(cur, "documents", "status='rejected'"))
            
        except Exception as e:
            print(f"Error loading dashboard stats: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
