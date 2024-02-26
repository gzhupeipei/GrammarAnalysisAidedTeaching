from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QComboBox, QTextEdit, QLineEdit
from PyQt5.QtCore import Qt
import first, second, third, GrammarAnalysis
def extend(geometry: QtCore.QRect):     #对窗口进行缩放
    return QtCore.QRect(geometry.x() * 2, geometry.y() * 2, geometry.width() * 2, geometry.height() * 2)

def open_winsecond(ui):     #将second窗口打开
    ui.child = second.Ui_MainWindow()
    init_second(ui.child)
    comboBox: QComboBox = ui.comboBox
    textEdit: QTextEdit = ui.textEdit
    ui.child.textEdit.setText(GrammarAnalysis.create_table(textEdit.toPlainText(), comboBox.currentText()))
    ui.child.show()    #显示窗口

def open_winthird(ui):      #将third窗口打开
    ui.child = third.Ui_MainWindow()
    init_third(ui.child)
    lineEdit: QLineEdit = ui.lineEdit
    ui.child.textEdit.setText(GrammarAnalysis.analysis(lineEdit.text()))
    ui.child.show()     #显示窗口

def init_first(ui, MainWindow):     #初始化first窗口
    size = MainWindow.size()
    MainWindow.setFixedSize(size * 2)
    ui.verticalLayoutWidget.setGeometry(extend(ui.verticalLayoutWidget.geometry()))
    ui.textEdit.setGeometry(extend(ui.textEdit.geometry()))
    ui.menubar.setGeometry(extend(ui.menubar.geometry()))
    ui.label.setAlignment(Qt.AlignCenter)       #label设置居中
    comboBox: QComboBox = ui.comboBox       #添加comboBox的项
    comboBox.addItem('LL(1)分析法')
    comboBox.addItem('LR(0)分析法')
    comboBox.addItem('SLR(1)分析法')
    comboBox.addItem('LR(1)分析法')
    comboBox.addItem('LALR(1)分析法')

    ui.pushButton.clicked.connect(lambda: open_winsecond(ui))       #按钮‘生成预测分析表’打开新窗口second
    ui.pushButton_2.clicked.connect(lambda: MainWindow.close())     #按钮‘退出’执行退出

def init_second(ui):        #初始化second窗口
    size = ui.size()
    ui.resize(size * 2)
    ui.menubar.setGeometry(extend(ui.menubar.geometry()))

    ui.pushButton.clicked.connect(lambda: open_winthird(ui))       #按钮‘进行分析’打开新窗口third
    ui.pushButton_2.clicked.connect(lambda: ui.close())         #按钮‘退出’执行退出

def init_third(ui):         #初始化third窗口
    size = ui.size()
    ui.resize(size * 2)
    ui.menubar.setGeometry(extend(ui.menubar.geometry()))