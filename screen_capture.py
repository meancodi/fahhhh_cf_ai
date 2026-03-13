import sys, os
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QRect
from PIL import ImageGrab

SAVE_FOLDER  = "screenshots"
TRIGGER_FILE = "./trigger.txt"

class ScreenSelector(QWidget):

    def __init__(self):
        super().__init__()
        os.makedirs(SAVE_FOLDER, exist_ok=True)

        self.start = None
        self.end   = None
        self.saved = False

        self.setWindowOpacity(0.15)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowState(Qt.WindowFullScreen)
        self.setCursor(Qt.CrossCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self.show()
        self.activateWindow()   # force keyboard focus
        self.raise_()

    def mousePressEvent(self, event):
        self.start = event.pos()
        self.end   = self.start
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()

        x1, y1 = self.start.x(), self.start.y()
        x2, y2 = self.end.x(),   self.end.y()

        # ignore accidental tiny clicks
        if abs(x2 - x1) < 5 or abs(y2 - y1) < 5:
            return

        bbox = (min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2))
        self.setWindowOpacity(0.01)

        screenshot = ImageGrab.grab(bbox)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath  = os.path.join(SAVE_FOLDER, f"screenshot_{timestamp}.png")
        screenshot.save(filepath)

        # notify inference
        with open(TRIGGER_FILE, "w") as f:
            f.write(filepath)

        print("Saved to:", filepath)
        self.saved = True
        QApplication.quit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            print("Capture cancelled")
            with open("./trigger.txt", "w") as f:
                f.write("CANCELLED")
            QApplication.quit()

    def paintEvent(self, event):
        if self.start and self.end:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2))
            painter.drawRect(QRect(self.start, self.end))


app = QApplication(sys.argv)
selector = ScreenSelector()
sys.exit(app.exec_())