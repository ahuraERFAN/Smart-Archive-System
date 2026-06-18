# manager_panel/analytics.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, 
    QScrollArea, QFrame, QGridLayout, QProgressBar
)
from PyQt5.QtCore import Qt

from database.db import get_connection

class AnalyticsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayoutDirection(Qt.RightToLeft)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("📊 گزارش‌ها و آنالیتیکس سیستم")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        
        self.btn_refresh = QPushButton("↻ بروزرسانی گزارش")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #0078D7; color: white; border: none;
                border-radius: 6px; padding: 8px 15px; font-weight: bold;
            }
            QPushButton:hover { background-color: #005A9E; }
        """)
        self.btn_refresh.clicked.connect(self.refresh_report)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_refresh)
        layout.addLayout(header_layout)

        # Scroll Area for Dashboard Cards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.dashboard_container = QWidget()
        self.dashboard_container.setStyleSheet("background-color: transparent;")
        self.dashboard_layout = QVBoxLayout(self.dashboard_container)
        self.dashboard_layout.setSpacing(20)
        
        self.scroll.setWidget(self.dashboard_container)
        layout.addWidget(self.scroll)

        self.refresh_report()

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def create_card(self, title):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1a1e24; border-radius: 10px;
                border: 1px solid #2b303b;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #b5b5b5; border: none;")
        layout.addWidget(lbl_title)
        
        return card, layout

        self.clear_layout(self.dashboard_layout)
        conn = get_connection()
        cur = conn.cursor()

        try:
            # 1. آمار وضعیت اسناد (نمودار میله‌ای افقی)
            cur.execute("SELECT status, COUNT(*) AS cnt FROM documents GROUP BY status")
            rows = cur.fetchall()
            
            status_card, status_layout = self.create_card("📈 توزیع اسناد بر اساس وضعیت")
            total_docs = sum(row['cnt'] for row in rows) if rows else 1
            
            if not rows:
                status_layout.addWidget(QLabel("هیچ سندی ثبت نشده است."))
            else:
                for row in rows:
                    status = row["status"] or "نامشخص"
                    cnt = row["cnt"]
                    
                    row_widget = QWidget()
                    row_layout = QHBoxLayout(row_widget)
                    row_layout.setContentsMargins(0, 0, 0, 0)
                    
                    lbl_name = QLabel(f"{status} ({cnt})")
                    lbl_name.setFixedWidth(150)
                    lbl_name.setStyleSheet("color: white; border: none;")
                    
                    bar = QProgressBar()
                    bar.setMaximum(total_docs)
                    bar.setValue(cnt)
                    bar.setTextVisible(False)
                    bar.setFixedHeight(12)
                    bar.setStyleSheet("""
                        QProgressBar { border: none; border-radius: 6px; background-color: #2b303b; }
                        QProgressBar::chunk { background-color: #3498db; border-radius: 6px; }
                    """)
                    
                    row_layout.addWidget(lbl_name)
                    row_layout.addWidget(bar)
                    status_layout.addWidget(row_widget)
            self.dashboard_layout.addWidget(status_card)

            # 2. برترین کاربران (نمودار میله‌ای)
            cur.execute("""
                SELECT u.username, COUNT(d.id) AS cnt FROM documents d
                JOIN users u ON d.user_id = u.id GROUP BY u.username ORDER BY cnt DESC LIMIT 5
            """)
            rows = cur.fetchall()
            
            users_card, users_layout = self.create_card("🏆 فعال‌ترین کاربران (ثبت سند)")
            max_user_docs = rows[0]['cnt'] if rows else 1
            
            if not rows:
                users_layout.addWidget(QLabel("داده‌ای موجود نیست."))
            else:
                for row in rows:
                    row_widget = QWidget()
                    row_layout = QHBoxLayout(row_widget)
                    row_layout.setContentsMargins(0, 0, 0, 0)
                    
                    lbl_name = QLabel(f"{row['username']} ({row['cnt']} سند)")
                    lbl_name.setFixedWidth(150)
                    lbl_name.setStyleSheet("color: white; border: none;")
                    
                    bar = QProgressBar()
                    bar.setMaximum(max_user_docs)
                    bar.setValue(row['cnt'])
                    bar.setTextVisible(False)
                    bar.setFixedHeight(12)
                    bar.setStyleSheet("""
                        QProgressBar { border: none; border-radius: 6px; background-color: #2b303b; }
                        QProgressBar::chunk { background-color: #2ecc71; border-radius: 6px; }
                    """)
                    
                    row_layout.addWidget(lbl_name)
                    row_layout.addWidget(bar)
                    users_layout.addWidget(row_widget)
            self.dashboard_layout.addWidget(users_card)

            # 3. آخرین تایید شده‌ها
            cur.execute("""
                SELECT d.title, d.reviewed_at, u.username AS reviewer FROM documents d
                LEFT JOIN users u ON d.reviewed_by = u.id WHERE d.status IN ('manager_ok', 'approved')
                ORDER BY d.reviewed_at DESC LIMIT 5
            """)
            rows = cur.fetchall()
            
            recent_card, recent_layout = self.create_card("✅ آخرین اسناد تایید شده نهایی")
            if not rows:
                recent_layout.addWidget(QLabel("هنوز سندی تایید نهایی نشده است."))
            else:
                for row in rows:
                    lbl = QLabel(f"📄 «{row['title']}» - تایید توسط {row.get('reviewer') or '-'} در {row.get('reviewed_at') or '-'}")
                    lbl.setStyleSheet("color: #a0aabf; padding: 5px 0; border: none; border-bottom: 1px solid #2b303b;")
                    recent_layout.addWidget(lbl)
            self.dashboard_layout.addWidget(recent_card)

        finally:
            conn.close()
            
        self.dashboard_layout.addStretch()
    def refresh_report(self):
        self.clear_layout(self.dashboard_layout)
        conn = get_connection()
        cur = conn.cursor()

        try:
            # 1. آمار وضعیت اسناد (نمودار میله‌ای افقی)
            cur.execute("SELECT status, COUNT(*) AS cnt FROM documents GROUP BY status")
            rows = cur.fetchall()
            
            status_card, status_layout = self.create_card("📈 توزیع اسناد بر اساس وضعیت")
            total_docs = sum(row['cnt'] for row in rows) if rows else 1
            
            if not rows:
                # اصلاح رنگ متن حالت خالی
                lbl_empty = QLabel("هیچ سندی ثبت نشده است.")
                lbl_empty.setStyleSheet("color: #a0aabf;") 
                status_layout.addWidget(lbl_empty)
            else:
                for row in rows:
                    status = row["status"] or "نامشخص"
                    cnt = row["cnt"]
                    
                    row_widget = QWidget()
                    row_layout = QHBoxLayout(row_widget)
                    row_layout.setContentsMargins(0, 0, 0, 0)
                    
                    lbl_name = QLabel(f"{status} ({cnt})")
                    lbl_name.setFixedWidth(150)
                    lbl_name.setStyleSheet("color: white; border: none;")
                    
                    bar = QProgressBar()
                    bar.setMaximum(total_docs)
                    bar.setValue(cnt)
                    bar.setTextVisible(False)
                    bar.setFixedHeight(12)
                    bar.setStyleSheet("""
                        QProgressBar { border: none; border-radius: 6px; background-color: #2b303b; }
                        QProgressBar::chunk { background-color: #3498db; border-radius: 6px; }
                    """)
                    
                    row_layout.addWidget(lbl_name)
                    row_layout.addWidget(bar)
                    status_layout.addWidget(row_widget)
            self.dashboard_layout.addWidget(status_card)

            # 2. برترین کاربران (نمودار میله‌ای)
            cur.execute("""
                SELECT u.username, COUNT(d.id) AS cnt FROM documents d
                JOIN users u ON d.user_id = u.id GROUP BY u.username ORDER BY cnt DESC LIMIT 5
            """)
            rows = cur.fetchall()
            
            users_card, users_layout = self.create_card("🏆 فعال‌ترین کاربران (ثبت سند)")
            
            if not rows:
                # اصلاح رنگ متن حالت خالی
                lbl_empty = QLabel("داده‌ای موجود نیست.")
                lbl_empty.setStyleSheet("color: #a0aabf;") 
                users_layout.addWidget(lbl_empty)
            else:
                max_user_docs = rows[0]['cnt'] if rows else 1
                for row in rows:
                    row_widget = QWidget()
                    row_layout = QHBoxLayout(row_widget)
                    row_layout.setContentsMargins(0, 0, 0, 0)
                    
                    lbl_name = QLabel(f"{row['username']} ({row['cnt']} سند)")
                    lbl_name.setFixedWidth(150)
                    lbl_name.setStyleSheet("color: white; border: none;")
                    
                    bar = QProgressBar()
                    bar.setMaximum(max_user_docs)
                    bar.setValue(row['cnt'])
                    bar.setTextVisible(False)
                    bar.setFixedHeight(12)
                    bar.setStyleSheet("""
                        QProgressBar { border: none; border-radius: 6px; background-color: #2b303b; }
                        QProgressBar::chunk { background-color: #2ecc71; border-radius: 6px; }
                    """)
                    
                    row_layout.addWidget(lbl_name)
                    row_layout.addWidget(bar)
                    users_layout.addWidget(row_widget)
            self.dashboard_layout.addWidget(users_card)

            # 3. آخرین تایید شده‌ها
            cur.execute("""
                SELECT d.title, d.reviewed_at, u.username AS reviewer FROM documents d
                LEFT JOIN users u ON d.reviewed_by = u.id WHERE d.status IN ('manager_ok', 'approved')
                ORDER BY d.reviewed_at DESC LIMIT 5
            """)
            rows = cur.fetchall()
            
            recent_card, recent_layout = self.create_card("✅ آخرین اسناد تایید شده نهایی")
            if not rows:
                # اصلاح رنگ متن حالت خالی
                lbl_empty = QLabel("هنوز سندی تایید نهایی نشده است.")
                lbl_empty.setStyleSheet("color: #a0aabf;") 
                recent_layout.addWidget(lbl_empty)
            else:
                for row in rows:
                    lbl = QLabel(f"📄 «{row['title']}» - تایید توسط {row.get('reviewer') or '-'} در {row.get('reviewed_at') or '-'}")
                    lbl.setStyleSheet("color: #a0aabf; padding: 5px 0; border: none; border-bottom: 1px solid #2b303b;")
                    recent_layout.addWidget(lbl)
            self.dashboard_layout.addWidget(recent_card)

        finally:
            conn.close()
            
        self.dashboard_layout.addStretch()
