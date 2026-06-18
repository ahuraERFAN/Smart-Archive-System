# manager_panel/dashboard.py
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget
)
from PyQt5.QtCore import Qt

from manager_panel.user_management import UserManagementWidget
from manager_panel.key_manager import KeyManagerWidget
from manager_panel.stats_widget import StatsWidget
from manager_panel.analytics import AnalyticsWidget
from manager_panel.ticket_viewer import ManagerTicketViewer
from manager_panel.document_archiver import ManagerDocumentArchiver


class ManagerDashboard(QWidget):
    def __init__(self, user_data):
        super().__init__()

        self.user_data = user_data
        self.setWindowTitle("داشبورد مدیر")
        self.resize(1100, 650)

        # متغیرهایی برای نگهداری پنجره‌های مدیریت تیکت و بررسی اسناد
        self.review_window = None
        self.ticket_window = None

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # سایدبار
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(16, 16, 16, 16)
        side_layout.setSpacing(12)

        lbl_title = QLabel("SMART ARCHIVE")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("color:#00bfff; font-size:18px; font-weight:bold;")
        side_layout.addWidget(lbl_title)

        side_layout.addSpacing(16)

        lbl_role = QLabel("مدیر سیستم")
        lbl_role.setAlignment(Qt.AlignCenter)
        lbl_role.setStyleSheet("color:#bbbbbb; font-size:13px;")
        side_layout.addWidget(lbl_role)

        side_layout.addSpacing(8)

        lbl_user = QLabel(self.user_data.get("full_name") or self.user_data.get("username"))
        lbl_user.setAlignment(Qt.AlignCenter)
        lbl_user.setStyleSheet("font-size:14px; font-weight:bold; color: white;")
        side_layout.addWidget(lbl_user)

        side_layout.addSpacing(24)

        # دکمه‌های ناوبری موجود
        self.btn_stats = QPushButton("📊 داشبورد آمار")
        self.btn_users = QPushButton("👥 مدیریت کاربران")
        self.btn_keys = QPushButton("🔑 مدیریت کلیدها")
        self.btn_analytics = QPushButton("📈 گزارش‌ها و تحلیل")
        
        # دکمه‌های جدید اضافه شده برای مدیر
        self.btn_review = QPushButton("📄 بررسی و تأیید اسناد")
        self.btn_tickets = QPushButton("🎫 مدیریت تیکت‌ها")

        self.btn_logout = QPushButton("🚪 خروج")

        # اضافه کردن همه دکمه‌ها به سایدبار
        for btn in [self.btn_stats, self.btn_users, self.btn_keys, self.btn_analytics, self.btn_review, self.btn_tickets]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setObjectName("navBtn")
            side_layout.addWidget(btn)

        side_layout.addStretch()
        self.btn_logout.setObjectName("logoutBtn")
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        side_layout.addWidget(self.btn_logout)

        root_layout.addWidget(sidebar)

        # محتوای اصلی
        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack, 1)

        self.stats_widget = StatsWidget()
        self.users_widget = UserManagementWidget()
        self.keys_widget = KeyManagerWidget()
        self.analytics_widget = AnalyticsWidget()

        self.stack.addWidget(self.stats_widget)     # index 0
        self.stack.addWidget(self.users_widget)     # index 1
        self.stack.addWidget(self.keys_widget)      # index 2
        self.stack.addWidget(self.analytics_widget) # index 3

        # اتصال دکمه‌های تغییر تب
        self.btn_stats.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_users.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_keys.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.btn_analytics.clicked.connect(lambda: self.stack.setCurrentIndex(3))

        # اتصال دکمه‌های جدید به متدهای مربوطه
        self.btn_review.clicked.connect(self.open_review)
        self.btn_tickets.clicked.connect(self.open_tickets)

        self.btn_logout.clicked.connect(self.close)

        self.apply_styles()

    # ——— توجه: تو رفتگی این بخش اصلاح شد تا داخل کلاس قرار بگیرد ———
    def open_review(self):
        if self.review_window is None:
             self.review_window = ManagerDocumentArchiver()
        self.review_window.show()

    def open_tickets(self):
        if self.ticket_window is None:
             self.ticket_window = ManagerTicketViewer()
        self.ticket_window.show()

    def apply_styles(self):
        self.setStyleSheet("""
            #sidebar {
                background-color: #0d0f1a;
                border-right: 1px solid #20263a;
            }

            #navBtn {
                background-color: #161b2b;
                color: #e6e6e6;
                border: none;
                padding: 10px;
                text-align: right;
                border-radius: 6px;
            }
            #navBtn:hover {
                background-color: #1f2638;
            }

            #logoutBtn {
                background-color: #2b1620;
                color: #ff6b81;
                border: none;
                padding: 10px;
                text-align: right;
                border-radius: 6px;
            }
            #logoutBtn:hover {
                background-color: #3a1d2b;
            }
        """)
