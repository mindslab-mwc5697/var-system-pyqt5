import sys
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QGraphicsView
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from datetime import datetime
import mmcv, cv2, qimage2ndarray
from PIL import Image, ImageQt

form_class = uic.loadUiType("airport_control_system_v5.ui")[0]

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.view_ch1 = self.findChild(QGraphicsView, 'View_Ch1')
        self.view_ch2 = self.findChild(QGraphicsView, 'View_Ch2')
        self.view_ch3 = self.findChild(QGraphicsView, 'View_Ch3')
        self.view_ch4 = self.findChild(QGraphicsView, 'View_Ch4')

        self.table_action_check1 = self.findChild(QTableWidget, 'table_action_check')
        self.table_action_check2 = self.findChild(QTableWidget, 'table_action_check_2')

        self.view_person1 = self.findChild(QGraphicsView, 'view_person1')
        self.view_person2 = self.findChild(QGraphicsView, 'view_person2')

        self.table_info_time = self.findChild(QTableWidget, 'table_info_time')
        self.table_info_area = self.findChild(QTableWidget, 'table_info_area')
        self.table_info_action = self.findChild(QTableWidget, 'table_info_action')
        self.table_info_regi = self.findChild(QTableWidget, 'table_info_regi')

        self.button_close = self.findChild(QPushButton, 'button_close')
        self.button_close.clicked.connect(QCoreApplication.instance().quit)

        self.button_min = self.findChild(QPushButton, 'button_min')
        self.button_min.clicked.connect(lambda: self.showMinimized())

        self.button_max = self.findChild(QPushButton, 'button_max')
        self.button_max.clicked.connect(lambda: self.showMaximized())

    def cell_setup(self, font, enable):
        item = QTableWidgetItem()
        item.setFont(font)
        if enable:
            item.setForeground(QBrush(QColor(252, 233, 79)))
        else:
            item.setForeground(QBrush(QColor(22, 17, 58)))

        return item

    # action setup
    # Input : action(ex. Dash)
    #         action_check(ex. self.table_action_check1)
    def action_setup(self, action, action_check, enable):
        action_font = QFont('Noto Sans CJK KR', 19, QFont.Bold)
        item = self.cell_setup(action_font, enable)
        item.setText('●')
        item.setTextAlignment(Qt.AlignTop)
        item.setTextAlignment(Qt.AlignHCenter)
        if action == 'Dash' or action == 'Two':
            action_check.setItem(0, 0, item)
        elif action == 'Opposite' or action == 'Abandon':
            action_check.setItem(0, 1, item)
        else:
            action_check.setItem(0, 2, item)

    # information setup
    # Input : category(ex. self.table_info_time)
    #        info(ex. '2020-11-06 14:08:20')
    def info_setup(self, category, info):
        info_font = QFont('Noto Sans CJK KR', 10, QFont.Bold)
        item = self.cell_setup(info_font, True)
        item.setText(info)
        category.setItem(0, 1, item)

    # reset all cells
    def reset_cells(self):
        self.action_setup('Dash', self.table_action_check1, False)
        self.action_setup('Opposite', self.table_action_check1, False)
        self.action_setup('Faint', self.table_action_check1, False)
        self.action_setup('Two', self.table_action_check2, False)
        self.action_setup('Abandon', self.table_action_check2, False)
        self.action_setup('Assault', self.table_action_check2, False)


        self.table_info_time.setItem(0, 1, QTableWidgetItem())
        self.table_info_area.setItem(0, 1, QTableWidgetItem())
        self.table_info_action.setItem(0, 1, QTableWidgetItem())
        self.table_info_regi.setItem(0, 1, QTableWidgetItem())

    # setup channels and alarm scenes' frames
    def scene_setup(self, view, qimage):
        scene = QGraphicsScene()
        width = view.width()
        height = view.height()
        pixmap = QPixmap.fromImage(qimage).scaled(QSize(width-6,height-6))

        rounded = QPixmap(pixmap.size())
        rounded.fill(QColor('transparent'))

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(pixmap))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(pixmap.rect(), 6, 6)
        painter.end()

        scene.addPixmap(rounded)
        view.setScene(scene)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # def displayFrame(self, frame):
    #
    #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #     image = qimage2ndarray.array2qimage(frame)
    #     self.scene_setup(myWindow.view_ch1, image)
    #     self.reset_cells()
    #     time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     self.action_setup('Opposite', self.table_action_check1, True)
    #     self.info_setup(self.table_info_time, time)
    #     self.info_setup(self.table_info_area, 'Immigrant Area')
    #     self.info_setup(self.table_info_action, 'Dash')
    #     self.info_setup(self.table_info_regi, 'Jisu Choi\nUnknown')

if __name__ == "__main__" :
    app = QApplication(sys.argv)

    myWindow = WindowClass()

#####################################################################################################
# 6 frames list in order, json file with info
# ex. [ ch_1_frame, ch_2_frame, ch_3_frame, ch_4_frame, person_1_frame, person_2_frame ]
#     { action : Opposite,

    file_path = './record.avi'
    video = cv2.VideoCapture(file_path)
    video.set(1, 500)


    def displayFrame():
        ret, frame = video.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = qimage2ndarray.array2qimage(frame)
        myWindow.scene_setup(myWindow.view_ch1, image)
        myWindow.reset_cells()
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        myWindow.action_setup('Opposite', myWindow.table_action_check1, True)
        myWindow.info_setup(myWindow.table_info_time, time)
        myWindow.info_setup(myWindow.table_info_area, 'Immigrant Area')
        myWindow.info_setup(myWindow.table_info_action, 'Dash')
        myWindow.info_setup(myWindow.table_info_regi, 'Jisu Choi\nUnknown')

#####################################################################################################

    timer = QTimer()
    timer.timeout.connect(displayFrame)
    timer.start(30)


    myWindow.showFullScreen()

    app.exec_()