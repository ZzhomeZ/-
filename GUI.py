from PyQt5 import QtWidgets,QtGui,QtCore
import sys
import cv2
import count

class CountDisplay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('电子元器件智能计数系统')  # 创建整个界面
        self.setGeometry(500,250,800,600)  # 设计几何形状:界面左上角点出现的位置x、y，整个界面的宽度和高度

        # 创建一个空,塞点东西进去
        self.kong1 = QtWidgets.QLineEdit(self)
        self.kong1.setGeometry(QtCore.QRect(650,400,50,20))
        self.kong1.setText()
        self.info1 = QtWidgets.QLabel('电容数量：',self)
        self.info1.setGeometry(QtCore.QRect(650,380,60,20))

        self.kong2 = QtWidgets.QLineEdit(self)
        self.kong2.setGeometry(QtCore.QRect(650,340,50,20))
        self.info2 = QtWidgets.QLabel('电阻数量：',self)
        self.info2.setGeometry(QtCore.QRect(650,320,60,20))

        self.kong3 = QtWidgets.QLineEdit(self)
        self.kong3.setGeometry(QtCore.QRect(650,280,50,20))
        self.info3 = QtWidgets.QLabel('LED数量：',self)
        self.info3.setGeometry(QtCore.QRect(650,260,60,20))

        self.kong4 = QtWidgets.QLineEdit(self)
        self.kong4.setGeometry(QtCore.QRect(650,220,50,20))
        self.info4 = QtWidgets.QLabel('芯片数量：',self)
        self.info4.setGeometry(QtCore.QRect(650,200,60,20))

        self.kong5 = QtWidgets.QLineEdit(self)
        self.kong5.setGeometry(QtCore.QRect(650,160,50,20))
        self.info5 = QtWidgets.QLabel('数码管数量：',self)
        self.info5.setGeometry(QtCore.QRect(650,140,75,20))

        # 视频展示的空
        self.img_label = QtWidgets.QLabel(self)
        self.img_label.setGeometry(QtCore.QRect(10,10,600,400))

        self.videocap = cv2.VideoCapture(0)
        self.width = self.videocap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.videocap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        ratio1 = self.width/600
        ratio2 = self.height/480
        self.ratio = max(ratio1,ratio2)


        # 创建定时器
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)  # 定时器实时更新
        self.timer.start()  # 启动定时器










    def update(self):
        ret,frame = self.videocap.read()
        # 图片
        # img = cv2.imread('Aaa.png')
        # ratio1 = img.shape[1]/600
        # ratio2 = img.shape[0]/480
        # ratio = max(ratio1,ratio2)
        p = QtGui.QImage(frame.data, self.width,self.height,3*self.width,QtGui.QImage.Format_BGR888)
        pixmap = QtGui.QPixmap.fromImage(p)
        pixmap.setDevicePixelRatio(self.ratio)
        self.img_label.setPixmap(pixmap)
        self.img_label.show()

        self.kong1.setText(str())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    countdispaly = CountDisplay()
    countdispaly.show()
    sys.exit(app.exec_())