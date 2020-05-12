from aqt import mw
from aqt.utils import showInfo, askUser
from aqt.qt import *

def ResetEase():
    dialog = QDialog(mw)
    dialog.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
    ease_label = QLabel("Enter Ease: ")
    ease_spinbox = QSpinBox()
    ease_spinbox.setRange(130, 500)
    ease_spinbox.setValue(250)
    ease_spinbox.setSuffix("%")
    ease_spinbox.setSingleStep(10)
    user_ease = ease_spinbox.value()
    reset_button = QPushButton("&Reset")
    reset_button.clicked.connect(lambda: accept(user_ease))
    reset_button.clicked.connect(lambda: dialog.hide())
    cancel_button = QPushButton("&Cancel")
    cancel_button.clicked.connect(lambda: dialog.hide())
    ease_line = QHBoxLayout()
    ease_line.addWidget(ease_label)
    ease_line.addWidget(ease_spinbox)
    button_line = QHBoxLayout()
    button_line.addWidget(reset_button)
    button_line.addWidget(cancel_button)
    layout = QVBoxLayout()
    layout.addLayout(ease_line)
    layout.addLayout(button_line)
    dialog.setLayout(layout)
    dialog.setWindowTitle("Reset Ease")
    dialog.show()

def accept(user_ease):
    anki_ease = user_ease * 10
    reset = askUser("<div style='font-size: 16px'> Reset all cards Ease to {}%?<br><font color=red>This action can't be undone.</font></div>".format(user_ease), defaultno=True, title="Reset Ease")
    if reset:
        mw.col.db.execute("update cards set factor = ?", anki_ease)
        showInfo("Ease has been reset to {}%.".format(user_ease), title="Reset Ease")
    else:
        pass


action = QAction("Reset &Ease", mw)
action.triggered.connect(ResetEase)
mw.form.menuTools.addAction(action)
mw.addonManager.setConfigAction(__name__, ResetEase)
