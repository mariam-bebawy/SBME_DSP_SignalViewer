from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtGui import *
from pyqtgraph import PlotWidget, plot
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene
import numpy as np
import sys
import os
import pandas as pd
import pyqtgraph as pg
import matplotlib.pyplot as plt
from pyqtgraph.graphicsItems.ImageItem import ImageItem
import scipy
from scipy import signal
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import cv2
import numpy as np
import matplotlib.pyplot as plt
import statistics
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from matplotlib.backends.backend_pdf import PdfPages
from PyPDF2 import PdfFileMerger
import pyqtgraph.exporters


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi(r'GUI.ui', self)


        # TIMER

        self.timer = QtCore.QTimer()


        # RADIO BUTTONS

        self.ch1.toggled.connect(self.labelChange)
        self.ch2.toggled.connect(self.labelChange)
        self.ch3.toggled.connect(self.labelChange)

        # BUTTONS

        self.actionExit_2.triggered.connect(lambda: self.close_app())
        self.open.clicked.connect(lambda: self.load())
        self.play.clicked.connect(lambda: self.playafterpause())
        self.pause.clicked.connect(lambda: self.Pause())
        self.zoomin.clicked.connect(lambda: self.zoomIn())
        self.zoomout.clicked.connect(lambda: self.zoomOut())
        self.clear.clicked.connect(lambda: self.Clear())
        self.spectrogram.clicked.connect(lambda: self.Spectrogram())
        self.speedup.clicked.connect(lambda: self.Speedup())
        self.speeddown.clicked.connect(lambda: self.Speeddown())
        self.hidee.clicked.connect(lambda: self.Hide())
        self.showw.clicked.connect(lambda: self.Show())
        self.print.clicked.connect(lambda: self.export_pdf())

        # SLIDERS

        self.spectrogramMinSlider.valueChanged.connect(
            lambda: self.spectrominslider())
        self.spectogramMaxSlider.valueChanged.connect(
            lambda: self.spectromaxslider())

        # SIGNAL SLIDERS

        self.hSlider.valueChanged.connect(lambda: self.plotHSlide())
        self.vSlider.valueChanged.connect(lambda: self.plotVSlide())

        # COMBO BOX

        self.comboBox.activated[str].connect(self.colorChanger)
        
        self.spectrocolorChanger()
        self.spectrocomboBox.activated[str].connect(self.spectrocolorChanger)

        # 
        ## GLOBAL VARIABLES ##    
        # 

        # signal plot color
        self.pen1 = pg.mkPen(color=(255, 0, 0))
        self.pen2 = pg.mkPen(color=(255, 0, 0))
        self.pen3 = pg.mkPen(color=(255, 0, 0))

        # rgb levels
        self.min_r = 50
        self.max_r = 200
        self.min_g = 50
        self.max_g = 200
        self.min_b = 50
        self.max_b = 200

        # check loaded channel
        self.ch1loaded = False
        self.ch2loaded = False
        self.ch3loaded = False
        
        # counters
        self.i1 = 0
        self.i2 = 0
        self.i3 = 0
        self.j1 = 0
        self.j2 = 0
        self.j3 = 0
        self.k=0
        
        # signal data lists
        self.Listx1 = []
        self.Listy1 = []
        self.Listx2 = []
        self.Listy2 = []
        self.Listx3 = []
        self.Listy3 = []

        # initiate signal slider values
        self.hpreVal = 100
        self.vpreVal = 5       
        
        # hiden channel variables
        self.hide1 = False
        self.hide2 = False
        self.hide3 = False

        self.scmap = "viridis" #initiate colormap for spectrogram
        self.timer_delay = 150 #initiate time delay
        self.speed = 200 #initiate speed
        
        self.timer.setInterval(self.timer_delay)

    #
    ## FUNCTIONS ##
    #

    def labelChange(self):
        if self.ch1.isChecked() == True:
            self.activeChannel.setText("CHANNEL 1 IS ACTIVE")
        elif self.ch2.isChecked() == True:
            self.activeChannel.setText("CHANNEL 2 IS ACTIVE")
        elif self.ch3.isChecked() == True:
            self.activeChannel.setText("CHANNEL 3 IS ACTIVE")
        self.activeChannel.setFont(QFont('Arial', 12))
        self.activeChannel.setAlignment(QtCore.Qt.AlignCenter)

    # loading data
    def load(self):
        if self.ch1.isChecked() == True:
            self.fname1 = QFileDialog.getOpenFileName(
                None, "Select a file...", os.getenv('HOME'), filter="All files (*)")
            path1 = self.fname1[0]
            data1 = pd.read_csv(path1)
            self.y1 = data1.values[:, 1]
            self.y1max = max(self.y1)
            self.y1min = min(self.y1)
            self.x1 = data1.values[:, 0]
            self.x1max = self.x1[-1]
            self.ch1loaded = True
            self.Play()
        elif self.ch2.isChecked() == True:
            self.fname2 = QFileDialog.getOpenFileName(
                None, "Select a file...", os.getenv('HOME'), filter="All files (*)")
            path2 = self.fname2[0]
            data2 = pd.read_csv(path2)
            self.y2 = data2.values[:, 1]
            self.x2 = data2.values[:, 0]
            self.x2max = self.x2[-1]
            self.y2max = max(self.y2)
            self.y2min = min(self.y2)
            self.ch2loaded = True
            self.Play()
        elif self.ch3.isChecked() == True:
            self.fname3 = QFileDialog.getOpenFileName(
                None, "Select a file...", os.getenv('HOME'), filter="All files (*)")
            path3 = self.fname3[0]
            data3 = pd.read_csv(path3)
            self.y3 = data3.values[:, 1]
            self.x3 = data3.values[:, 0]
            self.x3max = self.x3[-1]
            self.y3max = max(self.y3)
            self.y3min = min(self.y3)
            self.ch3loaded = True
            self.Play()
        else:
            pass

    # hide signal
    def Hide(self):
        if self.ch1.isChecked():
            self.hide1 = True
            self.Update_plot_1()
        if self.ch2.isChecked():
            self.hide2 = True
            self.Update_plot_2()
        if self.ch3.isChecked():
            self.hide3 = True
            self.Update_plot_3()

    # show signal
    def Show(self):
        if self.ch1.isChecked():
            self.hide1 = False
            self.Update_plot_1()
        if self.ch2.isChecked():
            self.hide2 = False
            self.Update_plot_2()
        if self.ch3.isChecked():
            self.Update_plot_3()
            self.hide3 = False

    # update graph
    def Update_data1(self):
        if self.ch1loaded == True:
            tempx = self.x1[self.i1 *
                            self.speed: (self.i1 + 1) * self.speed]+(self.j1*self.x1[-1])
            tempy = self.y1[self.i1*self.speed: (self.i1 + 1) * self.speed]
            self.Listx1 = np.concatenate((self.Listx1, tempx))
            self.Listy1 = np.concatenate((self.Listy1, tempy))
            self.i1 += 1
            self.signalWidget.plotItem.setXRange(tempx[0]-self.k*(tempx[-1]-tempx[0]),tempx[-1])
        else:
            pass

    def Update_data2(self):
        if self.ch2loaded == True:
            tempx = self.x2[self.i2 *
                            self.speed: (self.i2 + 1) * self.speed]+self.j2*self.x2[-1]
            tempy = self.y2[self.i2*self.speed: (self.i2 + 1) * self.speed]
            self.Listx2 = np.concatenate((self.Listx2, tempx))
            self.Listy2 = np.concatenate((self.Listy2, tempy))
            self.i2 += 1
            self.signalWidget.plotItem.setXRange(tempx[0]-self.k*(tempx[-1]-tempx[0]),tempx[-1])
        else:
            pass

    def Update_data3(self):
        if self.ch3loaded == True:
            tempx = self.x3[self.i3 *
                            self.speed: (self.i3 + 1) * self.speed]+self.j3*self.x3[-1]
            tempy = self.y3[self.i3*self.speed: (self.i3 + 1) * self.speed]
            self.Listx3 = np.concatenate((self.Listx3, tempx))
            self.Listy3 = np.concatenate((self.Listy3, tempy))
            self.i3 += 1
            self.signalWidget.plotItem.setXRange(tempx[0]-self.k*(tempx[-1]-tempx[0]),tempx[-1])
        else:
            pass

    # update plot
    def Update_plot_1(self):
        if self.ch1loaded == True:
            if self.hide1 == False:
                self.data_line1.setData(self.Listx1, self.Listy1)
            if self.hide1 == True:
                self.data_line1.setData()
            if(len(self.Listx1) == (self.j1+1)*len(self.x1)):
                self.j1 = self.j1+1
                self.i1 = 0
                self.setlimits()
        else:
            pass

    def Update_plot_2(self):
        if self.ch2loaded == True:
            if self.hide2 == False:
                self.data_line2.setData(self.Listx2, self.Listy2)
            if self.hide2 == True:
                self.data_line2.setData()
            if(len(self.Listx2) == (self.j2+1)*len(self.x2)):
                self.j2 += 1
                self.i2 = 0
                self.setlimits()
        else:
            pass

    def Update_plot_3(self):
        if self.ch3loaded == True:
            if self.hide3 == False:
                self.data_line3.setData(self.Listx3, self.Listy3)
            if self.hide3 == True:
                self.data_line3.setData()
            if(len(self.Listx3) == (self.j3+1)*len(self.x3)):
                self.j3 += 1
                self.i3 = 0
                self.setlimits()
        else:
            pass

    # setting limits
    def setlimits(self):
        if(self.ch1.isChecked() == True and self.ch1loaded == True):
            if (self.ch2loaded == True or self.ch3loaded == True) and self.ch1loaded == True:
                if (self.j1+1)*self.x1max > self.xmax:
                    self.xmax = (self.j1+1)*self.x1max
                if self.y1max > self.ymax:
                    self.ymax = self.y1max
                if self.y1min < self.ymin:
                    self.ymin = self.y1min
            else:
                self.xmax = self.x1max*(self.j1+1)
                self.ymin = self.y1min
                self.ymax = self.y1max
        if(self.ch2.isChecked() == True and self.ch2loaded == True):
            if (self.ch1loaded == True or self.ch3loaded == True) and self.ch2loaded == True:
                if self.x2max*(self.j2+1) > self.xmax:
                    self.xmax = self.x2max*(self.j2+1)
                if self.y2max > self.ymax:
                    self.ymax = self.y2max
                if self.y2min < self.ymin:
                    self.ymin = self.y2min
            else:
                self.xmax = self.x2max*(self.j2+1)
                self.ymin = self.y2min
                self.ymax = self.y2max
        if(self.ch3.isChecked() == True and self.ch3loaded == True):
            if (self.ch1loaded == True or self.ch2loaded == True) and self.ch3loaded == True:
                if self.x3max*(self.j3+1) > self.xmax:
                    self.xmax = self.x3max*(self.j3+1)
                if self.y3max > self.ymax:
                    self.ymax = self.y3max
                if self.y3min < self.ymin:
                    self.ymin = self.y3min
            else:
                self.xmax = self.x3max*(self.j3+1)
                self.ymin = self.y3min
                self.ymax = self.y3max
        self.signalWidget.plotItem.getViewBox().setLimits(
            xMin=0, xMax=self.xmax, yMin=self.ymin, yMax=self.ymax)

    # initial play of signal
    def Play(self):
        if (self.ch1loaded == False and self.ch2loaded == False and self.ch3loaded == False):
            return
        self.signalWidget.clear()
        self.data_line1 = self.signalWidget.plot(pen=self.pen1)
        self.data_line2 = self.signalWidget.plot(pen=self.pen2)
        self.data_line3 = self.signalWidget.plot(pen=self.pen3)
        self.i1 = 0
        self.i2 = 0
        self.i3 = 0
        self.Listx1 = []
        self.Listy1 = []
        self.Listx2 = []
        self.Listy2 = []
        self.Listx3 = []
        self.Listy3 = []
        self.j1 = 0
        self.j2 = 0
        self.j3 = 0
        self.setlimits()
        self.timer.timeout.connect(self.Update_data1)
        self.timer.timeout.connect(self.Update_data2)
        self.timer.timeout.connect(self.Update_data3)
        self.timer.timeout.connect(self.Update_plot_1)
        self.timer.timeout.connect(self.Update_plot_2)
        self.timer.timeout.connect(self.Update_plot_3)
        self.timer.start()

    # pause
    def Pause(self):
        self.timer.stop()
        if self.ch1loaded == True:
            self.signalWidget.plotItem.getViewBox().setLimits(
                xMin=0, xMax=self.Listx1[-1], yMin=self.ymin, yMax=self.ymax)
        elif self.ch2loaded == True:
            self.signalWidget.plotItem.getViewBox().setLimits(
                xMin=0, xMax=self.Listx2[-1], yMin=self.ymin, yMax=self.ymax)
        elif self.ch3loaded == True:
            self.signalWidget.plotItem.getViewBox().setLimits(
                xMin=0, xMax=self.Listx3[-1], yMin=self.ymin, yMax=self.ymax)
        else:
            pass

    # zoom in
    def zoomIn(self):
        if (self.ch1loaded==True or self.ch2loaded==True or self.ch3loaded==True):
            if    self.timer.isActive():
                if self.k>0:
                    self.k=self.k-1
                else:
                    self.k-=((self.k+1)/2)
            else:
                 self.signalWidget.plotItem.getViewBox().scaleBy((0.9, 1))
        else:
            pass

    # zoom out
    def zoomOut(self):
        if (self.ch1loaded==True or self.ch2loaded==True or self.ch3loaded==True):
            if    self.timer.isActive():
                if self.k>=0:
                    self.k=self.k+1
                else:
                    self.k=((self.k)*2)+1
            else:
                self.signalWidget.plotItem.getViewBox().scaleBy((1.1, 1.1))
        else:
            pass
   
    # clear graph
    def Clear(self):
        self.signalWidget.clear()
        self.spectrogramWidget.clear()
        self.timer.stop()
        self.x1 = []
        self.x2 = []
        self.x3 = []
        self.y1 = []
        self.y2 = []
        self.y3 = []
        self.i1 = 0
        self.i2 = 0
        self.i3 = 0
        self.Listx1 = []
        self.Listy1 = []
        self.Listx2 = []
        self.Listy2 = []
        self.Listx3 = []
        self.Listy3 = []
        self.j1 = 0
        self.j2 = 0
        self.j3 = 0
        self.ch1loaded = False
        self.ch2loaded = False
        self.ch3loaded = False

    # figure to img
    def get_img_from_fig(self, fig, dpi=90):
        buf = io.BytesIO()
        fig.savefig(buf, format="jpeg", dpi=dpi)
        buf.seek(0)
        img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
        buf.close()
        img = cv2.imdecode(img_arr, 1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    # spectrogram colorchange
    def spectrocolorChanger(self):
        scb = self.spectrocomboBox
        if scb.currentText() == "viridis":
            self.scmap = "viridis"
        elif scb.currentText() == "plasma":
            self.scmap = "plasma"
        elif scb.currentText() == "cubehelix":
            self.scmap = "cubehelix"
        elif scb.currentText() == "jet":
            self.scmap = "jet"
        elif scb.currentText() == "rainbow":
            self.scmap = "rainbow"
        return self.scmap

    # spectrogram
    def Spectrogram(self):
        if self.ch1.isChecked() == True:
            fig = plt.figure()
            self.spec_gram = plt.specgram(self.y1, Fs=256, cmap=self.scmap)
            self.plot_graph = pg.PlotItem()
            pg.PlotItem.enableAutoScale(self.plot_graph)
            pg.PlotItem.hideAxis(self.plot_graph, 'left')
            pg.PlotItem.hideAxis(self.plot_graph, 'bottom')
            self.spectrogramWidget.setCentralItem(self.plot_graph)
            self.img = self.get_img_from_fig(fig)
            self.img = np.rot90(self.img, k=1, axes=(1, 0))
            self.image = pg.ImageItem(self.img)
            self.image.setLevels(
                [[self.min_r, self.max_r], [self.min_g, self.max_g], [self.min_b, self.max_b]])
            self.plot_graph.addItem(self.image)
        elif self.ch2.isChecked() == True:
            fig = plt.figure()
            self.spec_gram = plt.specgram(self.y2, Fs=256, cmap=self.scmap)
            self.plot_graph = pg.PlotItem()
            pg.PlotItem.enableAutoScale(self.plot_graph)
            pg.PlotItem.hideAxis(self.plot_graph, 'left')
            pg.PlotItem.hideAxis(self.plot_graph, 'bottom')
            self.spectrogramWidget.setCentralItem(self.plot_graph)
            self.img = self.get_img_from_fig(fig)
            self.img = np.rot90(self.img, k=1, axes=(1, 0))
            self.image = pg.ImageItem(self.img)
            self.image.setLevels(
                [[self.min_r, self.max_r], [self.min_g, self.max_g], [self.min_b, self.max_b]])
            self.plot_graph.addItem(self.image)
        elif self.ch3.isChecked() == True:
            fig = plt.figure()
            self.spec_gram = plt.specgram(self.y3, Fs=256, cmap=self.scmap)
            self.plot_graph = pg.PlotItem()
            pg.PlotItem.enableAutoScale(self.plot_graph)
            pg.PlotItem.hideAxis(self.plot_graph, 'left')
            pg.PlotItem.hideAxis(self.plot_graph, 'bottom')
            self.spectrogramWidget.setCentralItem(self.plot_graph)
            self.img = self.get_img_from_fig(fig)
            self.img = np.rot90(self.img, k=1, axes=(1, 0))
            self.image = pg.ImageItem(self.img)
            self.image.setLevels(
                [[self.min_r, self.max_r], [self.min_g, self.max_g], [self.min_b, self.max_b]])
            self.plot_graph.addItem(self.image)
        else:
            pass

    # spectrogramsliders
    def spectrominslider(self):
        slider_value = self.spectrogramMinSlider.value()
        self.min_r = slider_value
        self.min_g = slider_value
        self.min_b = slider_value
        self.spectrogramWidget.clear()
        self.Spectrogram()

    def spectromaxslider(self):
        slider_value = self.spectogramMaxSlider.value()
        self.max_r = slider_value
        self.max_g = slider_value
        self.max_b = slider_value
        self.spectrogramWidget.clear()
        self.Spectrogram()

    # graphSliders
    def Scrollh(self, temp):
        self.signalWidget.plotItem.getViewBox().translateBy(x=temp)

    def Scrollv(self, temp):
        self.signalWidget.plotItem.getViewBox().translateBy(y=temp)

    def plotHSlide(self):
        hnewVal = self.hSlider.value()
        if self.ch1loaded:
            temp = (hnewVal - self.hpreVal)*(self.Listx1[-1]/100)
        elif self.ch2loaded:
            temp = (hnewVal - self.hpreVal)*(self.Listx2[-1]/100)
        elif self.ch3loaded:
            temp = (hnewVal - self.hpreVal)*(self.Listx3[-1]/100)
        else:
            return
        self.Scrollh(temp)
        self.hpreVal = hnewVal

    def plotVSlide(self):
        if (self.ch1loaded == True or self.ch2loaded == True or self.ch3loaded == True):
            vnewVal = self.vSlider.value()
            temp = (vnewVal - self.vpreVal)*((self.ymax-self.ymin)/5)
            self.Scrollv(temp)
            self.vpreVal = vnewVal
        else:
            pass

    # close
    def close_app(self):
        sys.exit()

    # colorchange
    def colorChanger(self):
        cb = self.comboBox
        if cb.currentText() == "Red":
            if self.ch1.isChecked() == True:
                self.pen1 = pg.mkPen(color=(255, 0, 0))
            if self.ch2.isChecked() == True:
                self.pen2 = pg.mkPen(color=(255, 0, 0))
            if self.ch3.isChecked() == True:
                self.pen3 = pg.mkPen(color=(255, 0, 0))

        elif cb.currentText() == "Green":
            if self.ch1.isChecked() == True:
                self.pen1 = pg.mkPen(color=(0, 255, 0))
            if self.ch2.isChecked() == True:
                self.pen2 = pg.mkPen(color=(0, 255, 0))
            if self.ch3.isChecked() == True:
                self.pen3 = pg.mkPen(color=(0, 255, 0))

        elif cb.currentText() == "Blue":
            if self.ch1.isChecked() == True:
                self.pen1 = pg.mkPen(color=(0, 0, 255))
            if self.ch2.isChecked() == True:
                self.pen2 = pg.mkPen(color=(0, 0, 255))
            if self.ch3.isChecked() == True:
                self.pen3 = pg.mkPen(color=(0, 0, 255))

        elif cb.currentText() == "Pink":
            if self.ch1.isChecked() == True:
                self.pen1 = pg.mkPen(color=(255, 192, 203))
            if self.ch2.isChecked() == True:
                self.pen2 = pg.mkPen(color=(255, 192, 203))
            if self.ch3.isChecked() == True:
                self.pen3 = pg.mkPen(color=(255, 192, 203))
        elif cb.currentText() == "Yellow":
            if self.ch1.isChecked() == True:
                self.pen1 = pg.mkPen(color=(255, 255, 0))
            if self.ch2.isChecked() == True:
                self.pen2 = pg.mkPen(color=(255, 255, 0))
            if self.ch3.isChecked() == True:
                self.pen3 = pg.mkPen(color=(255, 255, 0))
        self.data_line1 = self.signalWidget.plot(pen=self.pen1)
        self.data_line1.setData(self.Listx1, self.Listy1)
        self.data_line2 = self.signalWidget.plot(pen=self.pen2)
        self.data_line2.setData(self.Listx2, self.Listy2)
        self.data_line3 = self.signalWidget.plot(pen=self.pen3)
        self.data_line3.setData(self.Listx3, self.Listy3)

    # speedup
    def Speedup(self):
        self.timer_delay = int(self.timer_delay*0.5+1)
        self.timer.setInterval(self.timer_delay)

    # speeddown
    def Speeddown(self):
        self.timer_delay = int(self.timer_delay*2+1)
        self.timer.setInterval(self.timer_delay)

    # playafterpause
    def playafterpause(self):
        if (self.ch1loaded or self.ch2loaded or self.ch3loaded):
            self.setlimits()
            self.timer.start()
        else:
            pass

    def setStats(self, y, x):
        ymin = min(y)
        ymax = max(y)
        xmin = x[y.index(min(y))]
        xmax = x[y.index(max(y))]
        duration = x[-1]
        mean = statistics.mean(y)
        std = statistics.stdev(y)
        statData = [ymin, xmin, ymax, xmax, duration, mean, std]
        return statData

    def stats(self):
        statData1 = [0, 0, 0, 0, 0, 0, 0]
        if self.ch1loaded != False:
            y1 = self.y1.tolist()
            x1 = self.x1.tolist()
            statData1 = self.setStats(y1, x1)
        statData2 = [0, 0, 0, 0, 0, 0, 0]
        if self.ch2loaded != False:
            y2 = self.y2.tolist()
            x2 = self.x2.tolist()
            statData2 = self.setStats(y2, x2)
        statData3 = [0, 0, 0, 0, 0, 0, 0]
        if self.ch3loaded != False:
            y3 = self.y3.tolist()
            x3 = self.x3.tolist()
            statData3 = self.setStats(y3, x3)
        dict = {'ch1': statData1, 'ch2': statData2, 'ch3': statData3}
        # dict = {'ch1': statData1}
        statTitle = ["min. value of data", "time of min. value", "max. value of data", "time of max. value",
                     "duration of signal data", "mean of data", "standard deviation of data"]
        table = pd.DataFrame(data=dict, index=statTitle)
        self.table = table.transpose()
        self.table.insert(0, "Channel", [1, 2, 3])
        return self.table

    def export_pdf(self):
        # Content for PDF
        self.dfToPdf()
        exporter = pg.exporters.ImageExporter(self.signalWidget.scene())
        exporter.export('sig_img.png')
        exporter = pg.exporters.ImageExporter(self.spectrogramWidget.scene())
        exporter.export('spec_img.png')
        # Signals imgs used in generating PDF
        self.sig_img = 'sig_img.png'
        self.spec_img = 'spec_img.png'
        # Create document with content given
        save_name = os.path.join(os.path.expanduser("~"), "file.pdf")
        self.pdf = canvas.Canvas(save_name)
        self.pdf.setFont('Courier-Bold', 18)
        self.pdf.drawString(259, 790, 'Signal')
        self.pdf.drawString(245, 400, 'Spectrogram')
        self.sigImage(self.sig_img)
        self.spectroImage(self.spec_img)
        self.pdf.save()
        self.merger()

    def merger(self):
        merger = PdfFileMerger()
        merger.append("file.pdf")
        merger.append("stats.pdf")
        merger.write("Desktop/result.pdf")
        merger.close

    def dfToPdf(self):
        df = self.stats()
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.axis('tight')
        ax.axis('off')
        ax.table(cellText=df.values, colLabels=df.columns, loc='center')
        pp = PdfPages("stats.pdf")
        pp.savefig(fig, bbox_inches='tight')
        pp.close()

     # Sending all signals images to their positions in the table
    def sigImage(self, img1):
        self.pdf.drawInlineImage(img1, 80, 470, width=450,
                                 height=310, preserveAspectRatio=False, showBoundary=True)

    def spectroImage(self, img1):
        self.pdf.drawInlineImage(img1, 80, 80, width=450,
                                 height=310, preserveAspectRatio=False, showBoundary=True)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
