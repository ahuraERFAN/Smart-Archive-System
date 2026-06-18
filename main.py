import sys

from PyQt5.QtWidgets import QApplication

from auth.login import LoginWindow
from database.db import init_db


def main():

    # ساخت دیتابیس
    init_db()

    app = QApplication(sys.argv)

    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
