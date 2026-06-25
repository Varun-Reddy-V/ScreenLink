"""
ScreenLink Receiver

Application entry point.

Responsibilities:
- Create the QApplication.
- Create the main application window.
- Start the Qt event loop.

All networking and display logic lives in other modules.
"""

import sys

from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main() -> None:
    """
    Start the ScreenLink Receiver application.
    """

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()