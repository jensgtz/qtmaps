# -*- coding: UTF-8 -*-

'''
@created: 12.10.2017
@author : Jens Götze
@email  : jg_git@gmx.net
@license: BSD
'''

import os

from PyQt5.QtWidgets import QAction, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QDialog,\
    QComboBox, QLineEdit, QCheckBox, QTextEdit, QPlainTextEdit, QButtonGroup, QToolButton
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtCore import Qt
from PyQt5.Qt import QStyle, QIcon, QSize, QToolBar


CHECKSTATE_DISTATE_MAP = ((Qt.Unchecked, Qt.Checked), (False, True))
CHECKSTATE_TRISTATE_MAP = ((Qt.Unchecked, Qt.PartiallyChecked, Qt.Checked), (False, None, True))


def add_menu(qmainwindow, menu_label, actions=[]):
    menubar = qmainwindow.menuBar()
    menu = menubar.addMenu("&"+menu_label)
    for action_label, action_func in actions:
        action = QAction("&"+action_label, qmainwindow)
        action.triggered.connect(action_func)
        #self._actions["%s.%s" % (menu_name, action_name)] = action
        menu.addAction(action)
        
def button(label, func) -> QPushButton:
    button = QPushButton()
    button.setText(label)
    button.clicked.connect(func)
    return button 

def toolbutton(label:str, func, grp=None, tt=None, size=None) -> QToolButton:
    w = QToolButton()
    if label.startswith("icon:"):
        set_icon(w, label[5:])
        if size: 
            w.setIconSize(QSize(*size))
    else:
        w.setText(label)
    if grp: 
        grp.addButton(w)
    if tt: 
        w.setToolTip(tt)
    w.clicked.connect(func)
    return w

def radiobutton(label, value):
    #TODO
    raise NotImplementedError
    
def buttongroup(*buttons) -> QButtonGroup:
    buttongroup = QButtonGroup()
    for button in buttons:
        buttongroup.addButton(button)
    return buttongroup

def hbox_layout(*widgets, align=None, stretch=None) -> QHBoxLayout:
    stretch = [1] * len(widgets) if stretch is None else stretch
    layout = QHBoxLayout()
    if align in ("center", "right"):
        layout.addStretch(1)
    for i in range(len(widgets)):
        if type(widgets[i]) in (QVBoxLayout, QHBoxLayout):
            layout.addLayout(widgets[i], stretch=stretch[i])
        else:
            layout.addWidget(widgets[i], stretch=stretch[i])
    if align in ("left", "center"):
        layout.addStretch(1)
    return layout

def vbox_layout(*widgets, align=None, stretch=None) -> QVBoxLayout:
    stretch = [1] * len(widgets) if stretch is None else stretch
    layout = QVBoxLayout()
    if align in ("center", "bottom"):
        layout.addStretch(1)
    for i in range(len(widgets)):
        wtype = type(widgets[i]) 
        if wtype in (QVBoxLayout, QHBoxLayout):
            layout.addLayout(widgets[i], stretch=stretch[i])
        elif wtype == QButtonGroup:
            layout.addWidget(widgets[i])
        else:
            layout.addWidget(widgets[i], stretch=stretch[i])
    if align in ("top", "center"):
        layout.addStretch(1)
    return layout

def grid_layout(master, widgets) -> QGridLayout:
    layout = QGridLayout()
    master.setLayout(layout)
    for x, y, widget in widgets:
        layout.addWidget(widget, x, y)
    return layout
    
def lineedit(text, tt=None) -> QLineEdit:
    w = QLineEdit()
    w.setText(text)
    if tt: w.setToolTip(tt)
    return w

def textedit(text, tt=None) -> QTextEdit:
    w = QTextEdit()
    w.textCursor().insertText(text)
    if tt: w.setToolTip(tt)
    return w

def plaintextedit(text, tt=None) -> QPlainTextEdit:
    w = QPlainTextEdit()
    w.setPlainText(text)
    if tt: w.setToolTip(tt)
    return w

def bool_value(v):
    if v in (False, 0, "0"):
        return False
    elif v in (True, 1, "1"):
        return True
    else:
        return None
    
def checkstate_to_value(state, tristate):
    if tristate:
        return CHECKSTATE_TRISTATE_MAP[1][CHECKSTATE_TRISTATE_MAP[0].index(state)]
    else:
        return CHECKSTATE_DISTATE_MAP[1][CHECKSTATE_DISTATE_MAP[0].index(state)]
    
def value_to_checkstate(value, tristate):
    _value = bool_value(value)
    if tristate:
        return CHECKSTATE_TRISTATE_MAP[0][CHECKSTATE_TRISTATE_MAP[1].index(_value)]
    else:
        return CHECKSTATE_DISTATE_MAP[0][CHECKSTATE_DISTATE_MAP[1].index(_value)]
    
def checkbox(label=None, value=False, tristate=False, tt=None) -> QCheckBox:
    if label:
        w = QCheckBox(label)
    else:
        w = QCheckBox()
    w.setTristate(tristate)
    state = value_to_checkstate(value, tristate)
    w.setCheckState(state)
    if tt: w.setToolTip(tt)
    return w

def combobox(items, default, editable=False, tt=None) -> QComboBox:
    w = QComboBox()
    w.addItems(items)
    if editable:
        w.setCurrentText(default)
    else:
        w.setCurrentIndex(items.index(default))
    w.setEditable(editable)
    if tt: w.setToolTip(tt)
    return w    

def integerfield(value=None, minmax=None, tt=None) -> QLineEdit:
    w = QLineEdit()
    if minmax:
        w.setValidator(QIntValidator(*minmax))
    else:
        w.setValidator(QIntValidator())
    if tt: w.setToolTip(tt)
    text = "" if value is None else str(value)
    w.setText(text)
    return w
    
def floatfield(value=None, minmaxdig=None, tt=None) -> QLineEdit:
    w = QLineEdit()
    if minmaxdig:
        w.setValidator(QDoubleValidator(*minmaxdig))
    else:
        #w.setValidator(QDoubleValidator)
        pass
    if tt: w.setToolTip(tt)
    text = "" if value is None else str(value)
    w.setText(text)
    return w

###

def get_icon(name):
    path = os.path.join(os.path.dirname(__file__), "icons", name+".png")
    icon = QIcon(path)
    return icon

def set_icon(widget, name):
    if hasattr(QStyle, name):
        style = widget.style()
        icon = style.standardIcon(getattr(QStyle, name))
    else:
        icon = get_icon(name)
    widget.setIcon(icon)
    
###

def iconaction(icon_name, func, tt=None):
    icon = get_icon(icon_name)
    w = QAction()
    w.setIcon(icon)
    if tt: w.setToolTip(tt)
    w.triggered.connect(func)
    return w

def action(label, func, tt=None, toggle=None):
    #print("action(label=%r, func=%r, tt=%r, toggle=%r)" % (label, func, tt, toggle))
    w = QAction()
    if label.startswith("icon:"):
        icon = get_icon(label[5:]) 
        w.setIcon(icon)
    else:
        w.setText(label)
    w.triggered.connect(func)
    if tt: 
        w.setToolTip(tt)
    if not(toggle is None):
        w.setCheckable(True)
        w.setChecked(toggle)
    return w

def actionstoolbar(actions=[]):
    w = QToolBar()
    w._actions = []
    for aparams in actions:
        a = action(*aparams)
        w.addAction(a)
        w._actions.append(a)
    return w
    


# test

def test():
    pass

if __name__ == "__main__":
    test()