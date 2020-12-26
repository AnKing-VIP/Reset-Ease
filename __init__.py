from aqt import mw
from aqt.utils import showInfo, askUser
from aqt.qt import *

class QHSeparationLine(QFrame):
    '''
    a horizontal separation line\n
    '''
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(1)
        self.setFixedHeight(20)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

class DlgResetEase(QDialog):
    def __init__(self, parent=mw):
        super(DlgResetEase, self).__init__(parent)
        self.setWindowTitle("Reset Ease")
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)

        self._deck_chooser = QComboBox()
        self._deck_chooser.addItem('Whole Collection', None)
        decks = {item["name"]:item["id"] for item in mw.col.decks.all()}
        for name in sorted(decks.keys()):
            self._deck_chooser.addItem(name, decks[name])
        self._deck_chooser.activated.connect(self._describe)

        self._new_ease = self._spinbox(250, '250% is the default Anki starting ease')
        self._old_ease = self._spinbox(130, '130% is the value for cards stuck in Anki "ease hell"')
        self._any_old_ease = QCheckBox()
        self._any_old_ease.setText('any')
        self._any_old_ease.toggled.connect(self._toggled)
 
        self._explanation = QLabel()
        self._explanation.setWordWrap(True)
        self._describe()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QGridLayout()
        layout.addWidget(self._label('Deck: '), 0, 0)
        layout.addWidget(self._deck_chooser, 0, 1, 1, 2)
        layout.addWidget(self._label('Old ease: '), 1, 0)
        layout.addWidget(self._old_ease, 1, 1)
        layout.addWidget(self._any_old_ease, 1, 2)
        layout.addWidget(self._label('New ease: '), 2, 0)
        layout.addWidget(self._new_ease, 2, 1)
        layout.addWidget(QHSeparationLine(), 3, 0, 1, 3)
        layout.addWidget(self._explanation, 4, 0, 1, 3)
        layout.addWidget(QLabel('<font color=red>This action cannot be undone.</font>'), 5, 0, 1, 3)
        layout.addWidget(QHSeparationLine(), 6, 0, 1, 3)
        layout.addWidget(buttonBox, 7, 0, 1, 3)
        self.setLayout(layout)

    def _spinbox(self, value, tooltip):
        spinbox = QSpinBox()
        spinbox.setRange(130, 500)
        spinbox.setValue(value)
        spinbox.setSuffix("%")
        spinbox.setSingleStep(10)
        spinbox.setToolTip(tooltip)
        spinbox.valueChanged.connect(self._describe)
        return spinbox

    def _label(self, text):
        label = QLabel(text)
        label.setFixedWidth(90)
        return label

    def _toggled(self):
        self._old_ease.setEnabled(not self._any_old_ease.isChecked())
        self._describe()

    def _describe(self):
        (sql, params) = self.sql('count(*)')
        n = mw.col.db.scalar(sql, *params)
        d = 'the {0} deck'.format(self._deck_chooser.currentText()) if self._deck_chooser.currentData() else 'any deck' 
        e = 'a different ease' if self._any_old_ease.isChecked() else 'an ease of {0}%'.format(self._old_ease.value())
        s = 'Press OK to change the ease to {0}% for the {1} cards in {2} which currently have {3}.\n'.format(self.new_ease(), n, d, e)
        self._explanation.setText(s)

    def new_ease(self):
        return self._new_ease.value()

    def sql(self, what='id'):
        predicates = []
        parameters = []
    
        # don't touch cards which already have the requested new ease.
        predicates.append('factor != ?')
        parameters.append(self._new_ease.value() * 10)
    
        if self._any_old_ease.isChecked():
            predicates.append('factor != 0')
        else:
            predicates.append('factor = ?')
            parameters.append(self._old_ease.value() * 10)
    
        if self._deck_chooser.currentData() is not None:
            predicates.append('did = ?')
            parameters.append(self._deck_chooser.currentData())
    
        select = 'SELECT {0} FROM cards'.format(what)
        return (select + ' WHERE ' + ' AND '.join(predicates), parameters)


def open_window():
    ease_dialog = DlgResetEase()
    if ease_dialog.exec():
        (sql, params) = ease_dialog.sql()
        num_cards = 0
        # update and flush the cards so on sync they will be gracefully updated.
        for card_id in mw.col.db.list(sql, *params):
            card = mw.col.getCard(card_id)
            card.factor = ease_dialog.new_ease() * 10
            card.flush()
            num_cards += 1
        msg = "Ease factor of {} card{} has been reset to {}%.".format(num_cards, "s" if num_cards != 1 else "", ease_dialog.new_ease())
        showInfo(msg, title="Reset Ease")

action = QAction("Reset &Ease", mw)
action.triggered.connect(open_window)
mw.form.menuTools.addAction(action)
mw.addonManager.setConfigAction(__name__, open_window)
