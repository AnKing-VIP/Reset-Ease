# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *


ezFactor = 2500
ezFactor2 = ezFactor/10

def ResetEase():
    mw.col.db.execute("update cards set factor = ?", ezFactor)
    # show a message box
    showInfo("Ease has been reset to " + str(ezFactor2) + "%.")


# create a new menu item, "test"
action = QAction("Reset Ease", mw)
# set it to call testFunction when it's clicked
action.triggered.connect(ResetEase)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

