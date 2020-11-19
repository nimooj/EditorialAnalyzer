import sys
import math 

from PyQt5 import uic

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import pandas as pd
from scipy.cluster.vq import whiten
from scipy.cluster.vq import kmeans

import matplotlib.image as img
import matplotlib.pyplot as plt


class EditorialAnalyzer(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)


        self.ui = uic.loadUi("firstForm.ui")

        self.ui.openFilesBtn.clicked.connect(self.openFiles)
        self.ui.analyzeBtn.clicked.connect(self.analyze)

        self.ui.show()


        self.editorial = ""
        self.dominantColors_RGB = []
        self.dominantColors_HVC = []



    @QtCore.pyqtSlot()
    def analyze(self):
        print("analyze")

        # painter = QPainter()

        # painter.begin(self))

        # pen = QPen()
        # pen.setWidth(40)
        # pen.setColor(QColor('red'))
        # painter.setPen(pen)
        # painter.drawRect(0, 0, 100, 100)

        #painter.end()

        r = []
        g = []
        b = []
        for row in self.editorial:
            for temp_r, temp_g, temp_b in row:
                r.append(temp_r)
                g.append(temp_g)
                b.append(temp_b)

        editorial_df = pd.DataFrame({'red': r, 
                                    'green': g,
                                    'blue': b})

        editorial_df['scaled_color_red'] = whiten(editorial_df['red'])
        editorial_df['scaled_color_green'] = whiten(editorial_df['green'])
        editorial_df['scaled_color_blue'] = whiten(editorial_df['blue'])
        
        cluster_centers, distortion = kmeans(editorial_df[['scaled_color_red', 
                                                            'scaled_color_green', 
                                                            'scaled_color_blue']], 3)
        
        # Three dominant colors 
        self.dominantColors_RGB = []
        red_std, green_std, blue_std = editorial_df[['red', 'green', 'blue']].std()

        for cluster_center in cluster_centers:
            red_scaled, green_scaled, blue_scaled = cluster_center
            self.dominantColors_RGB.append((
                red_scaled * red_std / 255,
                green_scaled * green_std / 255,
                blue_scaled * blue_std / 255
                ))


        self.convert2Munsell()



    def convert2Munsell(self):
        for rgb in self.dominantColors_RGB:
            r = rgb[0]
            g = rgb[1]
            b = rgb[2]

            x = 0.607 * r + 0.174 * g + 0.201 * b
            y = 0.299 * r + 0.587 * g + 0.114 * b
            z = 0.000 * r + 0.066 * g + 1.117 * b

            x0 = 0.9642
            y0 = 1.0
            z0 = 0.8249

            l = 116 * ((y/y0) ** 1/3) - 16
            if y/y0 <= 0.00856 :
                l = 903.3 * (y/y0) 

            a = 500 * ((x/x0) ** 1/3 - (y/y0) ** 1/3)
            b = 200 * ((y/y0) ** 1/3 - (z/z0) ** 1/3)

            h = math.atan(b/a) 
            v = l
            c = (a ** 2 + b ** 2) ** 1/2

            self.dominantColors_HVC.append([h, v, c])

        print(self.dominantColors_HVC)


    def openFiles(self):
        filters = "jpg (*.jpg);; jpeg (*.jpeg);; png (*.png)"
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "", "", filters, options=options)

        if fileName:
            print(fileName)
            loadedPic = QPixmap()
            loadedPic.load(fileName)

            imgWidth = loadedPic.size().width()
            imgHeight = loadedPic.size().height()

            if imgWidth > imgHeight:
                loadedPic = loadedPic.scaledToWidth(661)
            else:
                loadedPic = loadedPic.scaledToHeight(301)
                

            self.ui.imageField.setPixmap(loadedPic)

            self.editorial = img.imread(fileName)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = EditorialAnalyzer()
    sys.exit(app.exec_())
