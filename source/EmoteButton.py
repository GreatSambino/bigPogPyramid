from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt, QEvent, QSize
from PyQt5.QtGui import QPixmap, QIcon
from resourcepath import resource_path

class EmoteButton(QPushButton):
    def __init__(self, parent, emoteName: str, onClickFunction):
        super().__init__(parent)
        self.update_stylesheet(False)
        # Enable hover event tracking
        self.setAttribute(Qt.WA_Hover, True)
        
        self.resize(36,36)
        relative_path = emoteName + ".png"
        pixmap = QPixmap(resource_path(relative_path))
        icon = QIcon(pixmap)
        self.setIcon(icon)
        self.setIconSize(QSize(28,28))  # Set icon size to match pixmap size

        self.emoteName = emoteName
        self.onClickFunction = onClickFunction
        self.clicked.connect(self.trigger_on_click)

    def trigger_on_click(self):
        self.onClickFunction(self.emoteName)

    def event(self, event):
        # Hover enter event
        if event.type() == QEvent.HoverEnter:
            self.update_stylesheet(True)
        # Hover leave event
        elif event.type() == QEvent.HoverLeave:
            self.update_stylesheet(False)
        
        return super().event(event)

    def update_stylesheet(self, hovered: bool):
        if hovered:
            self.setStyleSheet("color: #FFFFFF; background-color: #999999; border-radius: 12px;")
        else:
            self.setStyleSheet("color: #FFFFFF; background-color: #666666; border-radius: 12px;")