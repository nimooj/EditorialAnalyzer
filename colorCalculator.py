import re
import math
import sys
import numpy as np

import colour.models as cm
import colour.notation.munsell as munsell

class ColorCalculator:
    def __init__(self, parent=None) :
        self.RGB = []
        self.XYZ = []
        self.LAB = []
        self.HVC = []

        # Hue 5 수준에서의 V/C의 C 최대 수준 [V, C]
        self.boundaries = {
                "R" : [5, 16], # R
                "YR" : [6, 12], # YR
                "Y" : [7, 10], # Y
                "GY" : [8, 12], # GY
                "G" : [8, 10], # G
                "BG" : [7.5, 8], # BG
                "B" : [7.5, 8], # B
                "PB" : [6, 14], # PB
                "P" : [4.5, 16], # P
                "RP" : [5.5, 16] # RP
                }

        self.tone = "V" 

        # [Hue, Tone]
        self.iri898 = []


    def rgb2hvc(self) :
        r = self.RGB[0] / 255 
        g = self.RGB[1] / 255 
        b = self.RGB[2] / 255 
        print(r, g, b)

        if r > 0.04045 :
            r_at = ((r + 0.055) / 1.055) ** 2.4
        elif r <= 0.04045 :
            r_at = r / 12.92

        if g > 0.04045 :
            g_at = ((g + 0.055) / 1.055) ** 2.4
        elif g <= 0.04045 :
            g_at = g / 12.92

        if b > 0.04045 :
            b_at = ((b + 0.055) / 1.055) ** 2.4
        elif b <= 0.04045 :
            b_at = b / 12.92

        x = r_at * 41.24564 + g_at * 35.75761 + b_at * 18.04375
        y = r_at * 21.26729 + g_at * 71.51522 + b_at * 7.2175
        z = r_at * 1.93339 + g_at * 11.9192 + b_at * 95.03041

        self.XYZ.append(round(x, 2))
        self.XYZ.append(round(y, 2))
        self.XYZ.append(round(z, 2))
        print("x : ", x)
        print("y : ", y)
        print("z : ", z)

        ###############################################################3
        cie_x = x 
        cie_y = y
        cie_z = z 
        ###############################################################3

        x = x / 95.0456
        y = y / 100.000
        z = z / 108.8754
        # x0 = 0.9642
        # y0 = 1.0
        # z0 = 0.8249

        if x > 0.008856 :
            x_at = x ** (1/3)
        elif x <= 0.008856 :
            x_at = 7.787 * x + 16/116

        if y > 0.008856 :
            y_at = y ** (1/3)
        elif y <= 0.008856 :
            y_at = 7.787 * y + 16/116
        
        if z > 0.008856 :
            z_at = z ** (1/3)
        elif z <= 0.008856 :
            z_at = 7.787 * z + 16/116


        l = 116 * y_at - 16

        a = 500 * (x_at - y_at)
        b = 200 * (y_at - z_at)

        self.LAB.append(round(l, 2))
        self.LAB.append(round(a, 2))
        self.LAB.append(round(b, 2))
        print("l : ", l)
        print("a : ", a)
        print("b : ", b)


        ###############################################################3
        xyz = np.array([cie_x/(cie_x + cie_y + cie_z), cie_y/(cie_x + cie_y + cie_z), cie_z/(cie_x + cie_y + cie_z)])

        xyY = cm.XYZ_to_xyY(xyz)
        print(xyY)
        munsellColor = munsell.xyY_to_munsell_colour(xyY)
        print(munsellColor)
        munsellColor = re.split(' |\/', munsellColor)
        ###############################################################3
        h = munsellColor[0]
        v = munsellColor[1] # 명도 : 0 ~ 10
        c = munsellColor[2] # 채도 : 0 ~ 16

        print("h : ", h)
        print("v : ", v)
        print("c : ", c)

        self.HVC.append(h)
        self.HVC.append(v)
        self.HVC.append(c)

        # Define tone with V/C
        self.getTone()

        # Define IRI 898 color
        self.getIRI898()



    def getTone(self):
        hue = self.HVC[0][3:]
        value = float(self.HVC[1])
        chroma = float(self.HVC[2])

        boundary = self.boundaries[hue]
        
        # Chroma 기준으로 먼저 사분위(25%, 50%, 75%, 100%)을 나눈다
        chromaOffset = chroma / boundary[1]

        # Maximum Chroma의 Value 수준을 중앙(50%) 수준으로 구간을 나눈다
        valueOffset = ((value - boundary[0]) + 5) / 10

        print("chroma offset : ", chromaOffset)
        print("value offset : ", valueOffset)

        if chromaOffset <= 0.25 :
            if valueOffset <= 0.25 :
                self.tone = "Dp"
            elif valueOffset <=  0.5:
                self.tone = "Gr"
            elif valueOffset <= 0.75 :
                self.tone = "Lgr"
            else :
                self.tone = "Vp"

        elif chromaOffset <= 0.5 :
            if valueOffset <= 0.3125 :
                self.tone = "Dk"
            elif valueOffset <= 0.5 :
                self.tone = "Dl"
            elif valueOffset <= 0.6875 :
                self.tone = "L"
            else :
                self.tone = "P"

        elif chromaOffset <= 0.75 :
            if valueOffset <= 0.375 :
                self.tone = "Dp"
            elif valueOffset <= 0.625 :
                self.tone = "S"
            else :
                self.tone = "B"

        elif chromaOffset <= 1.0 :
            self.tone = "V"



    def getIRI898(self) :
        hueOffset = float(self.HVC[0][0:3])
        hue = self.HVC[0][3:]

        if hueOffset <= 2.5 :
            hueOffset = 2.5
        elif hueOffset <= 5.0 :
            hueOffset = 5
        elif hueOffset <= 7.5 :
            hueOffset = 7.5
        else :
            hueOffset = 10

        self.iri898 = [str(hueOffset) + hue, self.tone]

