import sys, first, init
from PyQt5 import QtWidgets

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()    # 创建窗体类对象--窗口类型对象
    ui = first.Ui_MainWindow()              # 创建first窗体对象
    ui.setupUi(MainWindow)                  # 初始化MainWindow窗口设置
    init.init_first(ui, MainWindow)         # 初始化first窗口
    MainWindow.show()                       # 显示窗口
    sys.exit(app.exec_())



