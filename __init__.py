from aqt import mw
from aqt.utils import showInfo, askUser
from aqt.qt import *


class ResetEase(QDialog):
    def __init__(self, parent=mw):
        super(ResetEase, self).__init__(parent)
        self.mainWindow()


    def mainWindow(self):
        self.choose_ease()
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        self.setLayout(self.layout)
        self.setWindowTitle("Reset Ease")


    def choose_ease(self):
        deck_label = QLabel("Deck: ")
        deck_label.setFixedWidth(60)
        self.deck_chooser = QComboBox()
        self.deck_chooser.setFixedWidth(200)
        self.deck_chooser.addItem('Whole Collection', 'collection')
        did_list = []
        decks = mw.col.decks.all()
        for item in decks:
            deck_name = item["name"]
            deck_id = item["id"]
            self.deck_chooser.addItem(deck_name, deck_id)
            did_list.append(deck_id)
        ease_label = QLabel("Enter Ease: ")
        ease_label.setFixedWidth(60)
        self.ease_spinbox = QSpinBox()
        self.ease_spinbox.setFixedWidth(200)
        self.ease_spinbox.setRange(130, 500)
        self.ease_spinbox.setValue(250)
        self.ease_spinbox.setSuffix("%")
        self.ease_spinbox.setSingleStep(10)
        reset_button = QPushButton("&Reset")
        reset_button.clicked.connect(lambda: self.accept())
        reset_button.clicked.connect(lambda: self.hide())
        cancel_button = QPushButton("&Cancel")
        cancel_button.clicked.connect(lambda: self.hide())
        deck_line = QHBoxLayout()
        deck_line.addWidget(deck_label)
        deck_line.addWidget(self.deck_chooser)
        ease_line = QHBoxLayout()
        ease_line.addWidget(ease_label)
        ease_line.addWidget(self.ease_spinbox)
        button_line = QHBoxLayout()
        button_line.addWidget(reset_button)
        button_line.addWidget(cancel_button)
        self.layout = QVBoxLayout()
        self.layout.addLayout(deck_line)
        self.layout.addLayout(ease_line)
        self.layout.addLayout(button_line)


    def accept(self):
        deck_id = self.deck_chooser.currentData()
        deck_name = self.deck_chooser.currentText()
        user_ease = self.ease_spinbox.value()
        anki_ease = user_ease * 10
        reset = askUser("<div style='font-size: 16px'>Reset ease for all cards in \"{}\" to {}%?<br><font color=red>This action can't be undone.</font></div>".format(deck_name, user_ease), defaultno=True, title="Reset Ease")
        if reset:
            mw.col.db.execute("update cards set factor = ? where did = ?", anki_ease, deck_id)
            showInfo("Ease has been reset to {}%.".format(user_ease), title="Reset Ease")
        else:
            pass


def open_window():
    ease_dialog = ResetEase()
    ease_dialog.exec()

action = QAction("Reset &Ease", mw)
action.triggered.connect(open_window)
mw.form.menuTools.addAction(action)
mw.addonManager.setConfigAction(__name__, open_window)
