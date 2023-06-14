# This Python file uses the following encoding: utf-8
"""
Code Structure
The Snake Synth code consists of two main files: form.py and main.py. The form.py file contains the 
implementation of the GUI using PySide6 widgets, while main.py acts as the entry point for the application.

To use the synthesizer, follow these steps:

1. Make sure you have all the required dependencies installed, including PySide6, NumPy, and sounddevice.
You can use the command 'pip install -r requirements.txt' in the root directory.
2. To run the synthesizer, use the command 'python3 main.py'
"""

import sys
from form import MainWidget
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSize

WINDOW_WIDTH = 1001
WINDOW_HEIGHT = 590

if __name__ == "__main__":
    app = QApplication([])
    widget = MainWidget()
    widget.setWindowTitle("Snake Synth")
    widget.setFixedSize(QSize(WINDOW_WIDTH, WINDOW_HEIGHT))
    widget.show()
    sys.exit(app.exec())
