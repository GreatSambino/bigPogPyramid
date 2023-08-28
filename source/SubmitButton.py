from PyQt5.QtWidgets import QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, QEvent

class SubmitButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.isHoveredState = False
        self.isCancelState = False
        self.update_stylesheet()
        # Enable hover event tracking
        self.setAttribute(Qt.WA_Hover, True)

    def event(self, event):
        # Hover enter event
        if event.type() == QEvent.HoverEnter:
            self.isHoveredState = True
            self.update_stylesheet()
        # Hover leave event
        elif event.type() == QEvent.HoverLeave:
            self.isHoveredState = False
            self.update_stylesheet()
        
        return super().event(event)

    def set_labels(self, mainLabel, subLabel):
        self.mainLabel = mainLabel
        self.subLabel = subLabel

        # Inner layout to position two labels vertically
        self.labels_layout = QVBoxLayout()
        self.labels_layout.addWidget(mainLabel)
        self.labels_layout.addWidget(subLabel)

        # Central layout to center the inner layout within the button
        self.central_layout = QVBoxLayout()
        self.central_layout.addStretch()
        self.central_layout.addLayout(self.labels_layout)
        self.central_layout.addStretch()

        self.setLayout(self.central_layout)

    def set_submit_state(self):
        self.mainLabel.setText("Submit")
        self.subLabel.setVisible(False)
        self.isCancelState = False
        self.update_stylesheet()

    def set_cancel_state(self):
        self.mainLabel.setText("Cancel")
        self.subLabel.setVisible(True)
        self.isCancelState = True
        self.update_stylesheet()

    def update_stylesheet(self):
        if self.isHoveredState:
            if self.isCancelState:
                self.setStyleSheet("color: #FFFFFF; background-color: #D46060; border-radius: 12px;")
            else:
                self.setStyleSheet("color: #FFFFFF; background-color: #C9A5FF; border-radius: 12px;")
        # Hover leave event
        else:
            if self.isCancelState:
                self.setStyleSheet("color: #FFFFFF; background-color: #BB0000; border-radius: 12px;")
            else:
                self.setStyleSheet("color: #FFFFFF; background-color: #A970FF; border-radius: 12px;")

    def set_sub_label_text(self, value):
        formatted_value = format(value, '.1f')
        self.subLabel.setText(formatted_value)

    def hide_sub_label(self):
        self.subLabel.setVisible(False)