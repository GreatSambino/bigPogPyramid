import pyautogui
import time
import threading
import sys
from SubmitButton import SubmitButton
from EmoteButton import EmoteButton
from threading import Thread
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QGraphicsDropShadowEffect, QLabel, QLineEdit, QSizePolicy
from PyQt5.QtGui import QIcon, QColor, QFont, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp, pyqtSignal, QObject
from resourcepath import resource_path

DEFAULT_PYRAMID_HEIGHT = 4
DEFAULT_START_DELAY = 2.5
DEFAULT_LINE_DELAY = 0
MINIMUM_START_DELAY = 1

pyautogui.PAUSE=0 # This could cause issues with inputs, but speed is key to get an unbroken pyramid. Seems to work fine with testing

running_pyramid_thread = None

# Create a title font
titleFont = QFont("Dotum", 20)
titleFont.setBold(True)

# Create a description font
descriptionFont = QFont("Dotum", 12)
descriptionFont.setItalic(True)

# Create a help font
helpFont = QFont("Dotum", 10)

# Create a input field font
inputFont = QFont("Dotum", 14)

frameStyleSheet = "border-radius: 12px; background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #444444, stop:1 #555555);"

class ButtonSignalEmitter(QObject):
    restoreSubmitAppearanceSignal = pyqtSignal()
    setSubLabelTextSignal = pyqtSignal(float)
    hideSubLabelSignal = pyqtSignal()

def apply_drop_shadow(widget):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(2)
    shadow.setOffset(2, 2)
    shadow.setColor(QColor(0, 0, 0, 64))
    widget.setGraphicsEffect(shadow)

def apply_reverse_drop_shadow(widget):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(2)
    shadow.setOffset(-2, -2)
    shadow.setColor(QColor(0, 0, 0, 32))
    widget.setGraphicsEffect(shadow)

def validate_input(emoteTextInput, pyramidHeightTextInput, startDelayTextInput, lineDelayTextInput):
    try:
        pyramidHeight = int(pyramidHeightTextInput.text())
    except ValueError:
        pyramidHeight = DEFAULT_PYRAMID_HEIGHT
        pyramidHeightTextInput.setText(str(DEFAULT_PYRAMID_HEIGHT))

    try:
        startDelay = float(startDelayTextInput.text())
    except ValueError:
        startDelay = DEFAULT_START_DELAY
        startDelayTextInput.setText(str(DEFAULT_START_DELAY))
    if startDelay < MINIMUM_START_DELAY:
        startDelay = MINIMUM_START_DELAY
        startDelayTextInput.setText(str(MINIMUM_START_DELAY))

    try:
        lineDelay = float(lineDelayTextInput.text())
    except ValueError:
        lineDelay = DEFAULT_LINE_DELAY
        lineDelayTextInput.setText(str(DEFAULT_LINE_DELAY))

    return True, emoteTextInput.text(), pyramidHeight, startDelay, lineDelay

def repeat_string_with_spaces(s, times):
    return ' '.join([s] * times)

def write_and_submit_line(emoteString, pyramidHeight):
    lineString = repeat_string_with_spaces(emoteString, pyramidHeight)
    pyautogui.write(lineString, interval=0)
    pyautogui.press('enter', interval=0)

class CreatePyramidThread(Thread):
    def __init__(self, emoteString, pyramidHeight, startDelay, lineDelay, buttonSignalEmitter: ButtonSignalEmitter):
        super().__init__()
        self.stop_event = threading.Event()
        self.emoteString = emoteString
        self.pyramidHeight = pyramidHeight
        self.startDelay = startDelay
        self.lineDelay = lineDelay
        self.buttonSignalEmitter = buttonSignalEmitter

    def run(self):
        self.create_pyramid()

    def stop(self):
        self.stop_event.set()

    def create_pyramid(self):
        global running_pyramid_thread
        remainingStartDelay = self.startDelay
        while True:
            if self.stop_event.is_set():
                print("Cancelled during start delay")
                return
            
            remainingStartDelay -= 0.01
            if remainingStartDelay > 0:
                self.buttonSignalEmitter.setSubLabelTextSignal.emit(remainingStartDelay)
                time.sleep(0.01)
            else:
                break

        self.buttonSignalEmitter.hideSubLabelSignal.emit()

        # Create ascending part of pyramid
        for currentHeight in range(1, self.pyramidHeight + 1):
            if self.stop_event.is_set():
                print("Cancelled during ascend")
                return
            write_and_submit_line(self.emoteString, currentHeight)
            if self.lineDelay > 0.01:
                time.sleep(self.lineDelay)

        # Create descending part of pyramid, excluding final step
        for currentHeight in range(self.pyramidHeight - 1, 1, -1):
            if self.stop_event.is_set():
                print("Cancelled during descend")
                return
            write_and_submit_line(self.emoteString, currentHeight)
            if self.lineDelay > 0.01:
                time.sleep(self.lineDelay)

        # Create final part of pyramid without triggering line delay afterwards
        write_and_submit_line(self.emoteString, 1)

        running_pyramid_thread = None
        self.buttonSignalEmitter.restoreSubmitAppearanceSignal.emit()
        print("Finished")

def on_submit_button():
    global running_pyramid_thread
    if not running_pyramid_thread is None:
        print("Cancelling")
        submitButton.set_submit_state()
        running_pyramid_thread.stop()
        running_pyramid_thread = None
        return

    valid, emoteString, pyramidHeight, startDelay, lineDelay = validate_input(emoteTextInput, pyramidHeightTextInput, startDelayTextInput, lineDelayTextInput)
    if valid == False:
        print("Invalid input!")
    else:
        submitButton.set_cancel_state()
        thread = CreatePyramidThread(emoteString=emoteString, pyramidHeight=pyramidHeight, startDelay=startDelay, lineDelay=lineDelay, buttonSignalEmitter=buttonSignalEmitter)
        thread.start()
        running_pyramid_thread = thread

app = QApplication(sys.argv)
win = QMainWindow()
win.setFixedSize(640, 252)
win.setWindowTitle("bigPogPyramid")
win.setWindowIcon(QIcon(resource_path("PogChamp_komodo.ico")))
win.setStyleSheet("background-color: #333333;")

submitButton = SubmitButton(win)
submitButton.move(458, 116)
submitButton.resize(178, 132)
apply_drop_shadow(submitButton)
submitButton.clicked.connect(on_submit_button)

submitButtonMainLabel = QLabel(submitButton)
submitButtonMainLabel.setAlignment(Qt.AlignCenter)
submitButtonMainLabel.setStyleSheet("color: #DDDDDD; background-color: transparent;")
submitButtonMainLabel.setFont(titleFont)
apply_drop_shadow(submitButtonMainLabel)

submitButtonSubLabel = QLabel(submitButton)
submitButtonSubLabel.setText("2.5s")
submitButtonSubLabel.setAlignment(Qt.AlignCenter)

submitButtonSubLabel.setStyleSheet("color: #DDDDDD; background-color: transparent;")
submitButtonSubLabel.setFont(descriptionFont)
apply_drop_shadow(submitButtonSubLabel)

buttonSignalEmitter = ButtonSignalEmitter()
buttonSignalEmitter.restoreSubmitAppearanceSignal.connect(submitButton.set_submit_state)
buttonSignalEmitter.setSubLabelTextSignal.connect(submitButton.set_sub_label_text)
buttonSignalEmitter.hideSubLabelSignal.connect(submitButton.hide_sub_label)

submitButton.set_labels(mainLabel=submitButtonMainLabel, subLabel=submitButtonSubLabel)
submitButton.set_submit_state()

emoteFrame = QFrame(win)
emoteFrame.move(4, 4)
emoteFrame.resize(450, 108)
emoteFrame.setStyleSheet(frameStyleSheet)
apply_drop_shadow(emoteFrame)

emoteTitleLabel = QLabel(emoteFrame)
emoteTitleLabel.move(10, 4)
emoteTitleLabel.setText("Emote")
emoteTitleLabel.setStyleSheet("color: #DDDDDD; background-color: transparent;")
emoteTitleLabel.setFont(titleFont)
apply_drop_shadow(emoteTitleLabel)

emoteTextInput = QLineEdit(emoteFrame)
emoteTextInput.resize(434, 48)
emoteTextInput.move(8, 52)
emoteTextInput.setStyleSheet("color: #FFFFFF; background-color: #222222;")
emoteTextInput.setFont(inputFont)
emoteTextInput.setTextMargins(4,0,0,0)
#regex = QRegExp("^[a-zA-Z0-9:_-]+$")
#alphanumericValidator = QRegExpValidator(regex)
#emoteTextInput.setValidator(alphanumericValidator)
emoteTextInput.setText("PogChamp")
apply_reverse_drop_shadow(emoteTextInput)

def set_emote_text(emoteName: str):
    emoteTextInput.setText(emoteName)

def create_emote_button(emoteName: str, id: int):
    button = EmoteButton(emoteFrame, emoteName, set_emote_text)
    x = 132 + 40 * id
    button.move(x,8)
    apply_drop_shadow(button)

create_emote_button("PogChamp", 0)
create_emote_button("TriHard", 1)
create_emote_button("Jebaited", 2)
create_emote_button("Kappa", 3)
create_emote_button("ResidentSleeper", 4)
create_emote_button("LUL", 5)
create_emote_button("4Head", 6)

helpFrame = QFrame(win)
helpFrame.move(458, 4)
helpFrame.resize(178, 108)
helpFrame.setStyleSheet(frameStyleSheet)
apply_drop_shadow(helpFrame)

helpLabel = QLabel(helpFrame)
helpLabel.resize(162, 108)
helpLabel.move(8,0)
helpLabel.setText("Click Submit, then select Twitch chat before the timer finishes")
helpLabel.setStyleSheet("color: #DDDDDD; background-color: transparent;")
helpLabel.setFont(helpFont)
helpLabel.setAlignment(Qt.AlignCenter)
helpLabel.setWordWrap(True)
helpLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
apply_drop_shadow(helpLabel)

pyramidHeightFrame = QFrame(win)
pyramidHeightFrame.move(4, 116)
pyramidHeightFrame.resize(450, 64)
pyramidHeightFrame.setStyleSheet(frameStyleSheet)
apply_drop_shadow(pyramidHeightFrame)

pyramidHeightTitleLabel = QLabel(pyramidHeightFrame)
pyramidHeightTitleLabel.move(10, 4)
pyramidHeightTitleLabel.setText("Pyramid Height")
pyramidHeightTitleLabel.setStyleSheet("color: #DDDDDD; background-color: transparent;")
pyramidHeightTitleLabel.setFont(titleFont)
apply_drop_shadow(pyramidHeightTitleLabel)

# Limit input to integers
regex = QRegExp("^[1-9]$")
heightValidator = QRegExpValidator(regex)

pyramidHeightTextInput = QLineEdit(pyramidHeightFrame)
pyramidHeightTextInput.resize(48, 48)
pyramidHeightTextInput.move(394, 8)
pyramidHeightTextInput.setStyleSheet("color: #FFFFFF; background-color: #222222;")
pyramidHeightTextInput.setFont(inputFont)
pyramidHeightTextInput.setTextMargins(4,0,0,0)
pyramidHeightTextInput.setValidator(heightValidator)
pyramidHeightTextInput.setText(str(DEFAULT_PYRAMID_HEIGHT))
apply_reverse_drop_shadow(pyramidHeightTextInput)

timingFrame = QFrame(win)
timingFrame.move(4, 184)
timingFrame.resize(450, 64)
timingFrame.setStyleSheet(frameStyleSheet)
apply_drop_shadow(timingFrame)

timingTitleLabel = QLabel(timingFrame)
timingTitleLabel.move(10, 4)
timingTitleLabel.setText("Delay")
timingTitleLabel.setStyleSheet("color: #DDDDDD; background-color: transparent;")
timingTitleLabel.setFont(titleFont)
apply_drop_shadow(timingTitleLabel)

startDelayLabel = QLabel(timingFrame)
startDelayLabel.move(138, 20)
startDelayLabel.setText("Start (s):")
startDelayLabel.setStyleSheet("color: #DDDDDD; background-color: transparent;")
startDelayLabel.setFont(descriptionFont)
apply_drop_shadow(startDelayLabel)

lineDelayLabel = QLabel(timingFrame)
lineDelayLabel.move(308, 20)
lineDelayLabel.setText("Line (s):")
lineDelayLabel.setStyleSheet("color: #DDDDDD; background-color: transparent;")
lineDelayLabel.setFont(descriptionFont)
apply_drop_shadow(lineDelayLabel)

# Limit input to non-negative floating point numbers
regex = QRegExp("^\d*\.?\d*$")
floatValidator = QRegExpValidator(regex)

startDelayTextInput = QLineEdit(timingFrame)
startDelayTextInput.resize(48, 48)
startDelayTextInput.move(230, 8)
startDelayTextInput.setStyleSheet("color: #FFFFFF; background-color: #222222;")
startDelayTextInput.setFont(inputFont)
startDelayTextInput.setTextMargins(4,0,0,0)
startDelayTextInput.setValidator(floatValidator)
startDelayTextInput.setText(str(DEFAULT_START_DELAY))
apply_reverse_drop_shadow(startDelayTextInput)

lineDelayTextInput = QLineEdit(timingFrame)
lineDelayTextInput.resize(48, 48)
lineDelayTextInput.move(394, 8)
lineDelayTextInput.setStyleSheet("color: #FFFFFF; background-color: #222222;")
lineDelayTextInput.setFont(inputFont)
lineDelayTextInput.setTextMargins(4,0,0,0)
lineDelayTextInput.setValidator(floatValidator)
lineDelayTextInput.setText(str(DEFAULT_LINE_DELAY))
apply_reverse_drop_shadow(lineDelayTextInput)

win.show()
sys.exit(app.exec_())