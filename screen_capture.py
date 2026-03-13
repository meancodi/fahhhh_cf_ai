import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QRect
from PIL import ImageGrab

SAVE_FOLDER = "screenshots"

class ScreenSelector(QWidget):

    def __init__(self):
        super().__init__()

        os.makedirs(SAVE_FOLDER, exist_ok=True)

        self.start = None
        self.end = None

        self.setWindowOpacity(0.1)
        self.setWindowState(Qt.WindowFullScreen)
        self.setCursor(Qt.CrossCursor)

        self.setFocusPolicy(Qt.StrongFocus)

        self.show()

    def mousePressEvent(self, event):
        self.start = event.pos()
        self.end = self.start
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):

        self.end = event.pos()

        x1, y1 = self.start.x(), self.start.y()
        x2, y2 = self.end.x(), self.end.y()

        bbox = (min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2))
        self.setWindowOpacity(0.01)

        screenshot = ImageGrab.grab(bbox)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(SAVE_FOLDER, f"screenshot_{timestamp}.png")

        screenshot.save(filepath)

        print("Saved to:", filepath)

        with open("trigger.txt", "w") as f:
            f.write(filepath)   

        QApplication.quit()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            print("Capture cancelled")
            QApplication.quit()

    def paintEvent(self, event):

        if self.start and self.end:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2))

            rect = QRect(self.start, self.end)
            painter.drawRect(rect)


app = QApplication(sys.argv)
selector = ScreenSelector()
sys.exit(app.exec_())