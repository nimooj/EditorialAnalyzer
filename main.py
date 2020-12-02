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

from iri import IriAnalyzer
from colorCalculator import ColorCalculator


class EditorialAnalyzer(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)


        self.ui = uic.loadUi("firstForm.ui")

        self.ui.openFilesBtn.clicked.connect(self.openFiles)
        self.ui.analyzeBtn.clicked.connect(self.analyze)

        self.ui.mainColorLabel.setStyleSheet("border: 1px solid black; background-color: white;")
        self.ui.subColorLabel.setStyleSheet("border: 1px solid black; background-color: white;")
        self.ui.accentColorLabel.setStyleSheet("border: 1px solid black; background-color: white;")

        self.ui.iriLabel0.setStyleSheet("border: 1px solid black; background-color: white;")
        self.ui.iriLabel1.setStyleSheet("border: 1px solid black; background-color: white;")
        self.ui.iriLabel2.setStyleSheet("border: 1px solid black; background-color: white;")

        self.ui.show()

        self.editorial = ""
        self.dominantColors_RGB = []
        self.dominantColors_HVC = []



    @QtCore.pyqtSlot()
    def analyze(self):
        print("analyze")
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
            self.dominantColors_RGB.append([
                round(red_scaled * red_std),
                round(green_scaled * green_std),
                round(blue_scaled * blue_std)
                ]) 

        print("RGB: ")
        print(self.dominantColors_RGB)

        # Show top 3 colors
        ### Main color
        mainColor = self.dominantColors_RGB[0]
        self.ui.mainColorLabel.setStyleSheet("background-color: rgb(" + str(mainColor[0]) + ", " + str(mainColor[1]) + ", " + str(mainColor[2]) + ")")
        self.ui.Main_R.setText(str(mainColor[0]))
        self.ui.Main_G.setText(str(mainColor[1]))
        self.ui.Main_B.setText(str(mainColor[2]))

        ### Sub color
        subColor = self.dominantColors_RGB[1]
        self.ui.subColorLabel.setStyleSheet("background-color: rgb(" + str(subColor[0]) + ", " + str(subColor[1]) + ", " + str(subColor[2]) + ")")
        self.ui.Sub_R.setText(str(subColor[0]))
        self.ui.Sub_G.setText(str(subColor[1]))
        self.ui.Sub_B.setText(str(subColor[2]))

        ### Accent color
        accentColor = self.dominantColors_RGB[2]
        self.ui.accentColorLabel.setStyleSheet("background-color: rgb(" + str(accentColor[0]) + ", " + str(accentColor[1]) + ", " + str(accentColor[2]) + ")")
        self.ui.Accent_R.setText(str(accentColor[0]))
        self.ui.Accent_G.setText(str(accentColor[1]))
        self.ui.Accent_B.setText(str(accentColor[2]))

        # HVC 값 계산 
        self.convert2Munsell()

        # IRI 분석
        groupName = self.iriModel.analyzeColorScheme(self.dominantColors_RGB)
        self.ui.iriGroupName0.setText(groupName)
        self.ui.iriLabel0.setStyleSheet(
                "background-color: rgb(" 
                +  str(self.iriModel.colorScheme[0][0]) 
                + ", "
                +  str(self.iriModel.colorScheme[0][1]) 
                + ", "
                +  str(self.iriModel.colorScheme[0][2]) 
                + ")"
                )
        self.ui.iriLabel1.setStyleSheet(
                "background-color: rgb(" 
                +  str(self.iriModel.colorScheme[1][0]) 
                + ", "
                +  str(self.iriModel.colorScheme[1][1]) 
                + ", "
                +  str(self.iriModel.colorScheme[1][2]) 
                + ")"
                )
        self.ui.iriLabel2.setStyleSheet(
                "background-color: rgb(" 
                +  str(self.iriModel.colorScheme[2][0]) 
                + ", "
                +  str(self.iriModel.colorScheme[2][1]) 
                + ", "
                +  str(self.iriModel.colorScheme[2][2]) 
                + ")"
                )

        self.ui.iriGroupName1.setText(groupName)
        for adjective in self.iriModel.adjectives :
            self.ui.iriAdjectivesList.addItem(adjective)




    def convert2Munsell(self):
        for i, rgb in enumerate(self.dominantColors_RGB) :
            calculator = ColorCalculator()
            calculator.RGB.append(rgb[0])
            calculator.RGB.append(rgb[1])
            calculator.RGB.append(rgb[2])

            calculator.rgb2hvc()

            if i == 0 :
                self.ui.Main_X.setText(str(calculator.XYZ[0]))
                self.ui.Main_Y.setText(str(calculator.XYZ[1]))
                self.ui.Main_Z.setText(str(calculator.XYZ[2]))

                self.ui.Main_L.setText(str(calculator.LAB[0]))
                self.ui.Main_a.setText(str(calculator.LAB[1]))
                self.ui.Main_b.setText(str(calculator.LAB[2]))

            elif i == 1 :
                self.ui.Sub_X.setText(str(calculator.XYZ[0]))
                self.ui.Sub_Y.setText(str(calculator.XYZ[1]))
                self.ui.Sub_Z.setText(str(calculator.XYZ[2]))

                self.ui.Sub_L.setText(str(calculator.LAB[0]))
                self.ui.Sub_a.setText(str(calculator.LAB[1]))
                self.ui.Sub_b.setText(str(calculator.LAB[2]))

            elif i == 2 :
                self.ui.Accent_X.setText(str(calculator.XYZ[0]))
                self.ui.Accent_Y.setText(str(calculator.XYZ[1]))
                self.ui.Accent_Z.setText(str(calculator.XYZ[2]))

                self.ui.Accent_L.setText(str(calculator.LAB[0]))
                self.ui.Accent_a.setText(str(calculator.LAB[1]))
                self.ui.Accent_b.setText(str(calculator.LAB[2]))



            self.dominantColors_HVC.append((calculator.HVC[0], calculator.HVC[1], calculator.HVC[2]))



        ### Main color
        mainColor = self.dominantColors_HVC[0]
        self.ui.Main_H.setText(str(mainColor[0]))
        self.ui.Main_V.setText(str(mainColor[1]))
        self.ui.Main_C.setText(str(mainColor[2]))

        ### Sub color
        subColor = self.dominantColors_HVC[1]
        self.ui.Sub_H.setText(str(subColor[0]))
        self.ui.Sub_V.setText(str(subColor[1]))
        self.ui.Sub_C.setText(str(subColor[2]))

        ### Accent color
        accentColor = self.dominantColors_HVC[2]
        self.ui.Accent_H.setText(str(accentColor[0]))
        self.ui.Accent_V.setText(str(accentColor[1]))
        self.ui.Accent_C.setText(str(accentColor[2]))




    def openFiles(self):
        # Initialization
        self.ui.mainColorLabel.setStyleSheet("background-color: white;")
        self.ui.Main_R.setText("")
        self.ui.Main_G.setText("")
        self.ui.Main_B.setText("")
        self.ui.Main_X.setText("")
        self.ui.Main_Y.setText("")
        self.ui.Main_Z.setText("")
        self.ui.Main_L.setText("")
        self.ui.Main_a.setText("")
        self.ui.Main_b.setText("")
        self.ui.Main_H.setText("")
        self.ui.Main_V.setText("")
        self.ui.Main_C.setText("")

        self.ui.subColorLabel.setStyleSheet("background-color: white;")
        self.ui.Sub_R.setText("")
        self.ui.Sub_G.setText("")
        self.ui.Sub_B.setText("")
        self.ui.Sub_X.setText("")
        self.ui.Sub_Y.setText("")
        self.ui.Sub_Z.setText("")
        self.ui.Sub_L.setText("")
        self.ui.Sub_a.setText("")
        self.ui.Sub_b.setText("")
        self.ui.Sub_H.setText("")
        self.ui.Sub_V.setText("")
        self.ui.Sub_C.setText("")

        self.ui.accentColorLabel.setStyleSheet("background-color: white;")
        self.ui.Accent_R.setText("")
        self.ui.Accent_G.setText("")
        self.ui.Accent_B.setText("")
        self.ui.Accent_X.setText("")
        self.ui.Accent_Y.setText("")
        self.ui.Accent_Z.setText("")
        self.ui.Accent_L.setText("")
        self.ui.Accent_a.setText("")
        self.ui.Accent_b.setText("")
        self.ui.Accent_H.setText("")
        self.ui.Accent_V.setText("")
        self.ui.Accent_C.setText("")
        
        self.ui.iriLabel0.setStyleSheet("background-color: white;")
        self.ui.iriLabel1.setStyleSheet("background-color: white;")
        self.ui.iriLabel2.setStyleSheet("background-color: white;")

        self.ui.iriGroupName0.setText("")
        self.ui.iriGroupName1.setText("")

        self.ui.iriAdjectivesList.clear()

        self.iriModel = IriAnalyzer()

        self.dominantColors_RGB.clear()
        self.dominantColors_HVC.clear()



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
                if imgHeight > 301:
                    loadedPic = loadedPic.scaledToHeight(301)
                else :
                    loadedPic = loadedPic.scaledToWidth(661)
            else:
                loadedPic = loadedPic.scaledToHeight(301)

            self.ui.imageField.setPixmap(loadedPic)

            self.editorial = img.imread(fileName)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = EditorialAnalyzer()
    sys.exit(app.exec_())
