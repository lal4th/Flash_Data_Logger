from __future__ import annotations

import sys
from typing import Optional

from PyQt6 import QtWidgets, QtCore
from app.ui.main_window import MainWindow


def run() -> int:
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())


