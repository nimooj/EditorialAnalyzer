import json
import math


class IriAnalyzer():
    def __init__(self, parent=None) :
        with open('irijson') as data :
            self.groups = json.load(data)

        self.name_colors = {}
        self.name_adjectives = {}

        self.group = ""
        self.colorScheme = []
        self.adjectives = []


    # @params
    # x : float
    # y : float
    # z : float
    def getDist(self, x, y, z) :
        return (x ** 2 + y ** 2 + z ** 2) ** 0.5


    # @params
    # f : [R, G, B]
    # s : [R, G, B]
    def getColorDist(self, f, s) :
        return ((f[0] - s[0]) ** 2 + (f[1] - s[1]) ** 2 + (f[2] - s[2]) ** 2) ** 0.5


    # @params
    # f : [[R, G, B], [R, G, B], [R, G, B]]
    # s : [[R, G, B], [R, G, B], [R, G, B]]
    def getSchemeDist(self, f, s) :
        red_dist = self.getColorDist(f[0], s[0])
        green_dist = self.getColorDist(f[1], s[0])
        blue_dist = self.getColorDist(f[2], s[0])
        return self.getDist(red_dist, green_dist, blue_dist)


    # @params
    # fcolors : [[[R, G, B], [R, G, B], [R, G, B]], ... ] in IRI color scheme
    # scolors : [[R, G, B], [R, G, B], [R, G, B]] 
    def getClosest(self, fcolors, scolors):
        dists = []

        # 아래 여섯 조합 중 가장 dists가 작은 조합을 선택 
        schemeCases = []
        # ABC - ABC -> dist0
        schemeCases.append([scolors[0], scolors[1], scolors[2]])

        # ABC - ACB -> dist1
        schemeCases.append([scolors[0], scolors[2], scolors[1]])

        # ABC - BAC -> dist2
        schemeCases.append([scolors[1], scolors[0], scolors[2]])

        # ABC - BCA -> dist3
        schemeCases.append([scolors[1], scolors[2], scolors[0]])

        # ABC - CAB -> dist4
        schemeCases.append([scolors[2], scolors[0], scolors[1]])

        # ABC - CBA -> dist5
        schemeCases.append([scolors[2], scolors[1], scolors[0]])
        

        # Group 내 배색칩들과 에디토리얼 배색칩과의 거리 ::
        # 에디토리얼 배색칩의 조합 중 min-square dist를 갖는 배색칩 조합과
        # Group 내 배색칩들과의 거리를 구한다
        minDists = []
        minDistInCombi = 1000000
        for schemeIdx, fcolor in enumerate(fcolors) :
            dists.append(self.getSchemeDist(fcolor, schemeCases[0]))
            dists.append(self.getSchemeDist(fcolor, schemeCases[1]))
            dists.append(self.getSchemeDist(fcolor, schemeCases[2]))
            dists.append(self.getSchemeDist(fcolor, schemeCases[3]))
            dists.append(self.getSchemeDist(fcolor, schemeCases[4]))
            dists.append(self.getSchemeDist(fcolor, schemeCases[5]))

            minDistInCombi = dists[0]
            minDistSchemeIdxInCombi = 0
            # 각 배색칩과 에디토리얼 배색칩의 최소 거리
            for i in range(0, len(dists)) :
                if dists[i] < minDistInCombi :
                    minDistInCombi = dists[i]
                    # fcolors들 중 몇 번 쨰 배색칩인지
                    minDistSchemeIdxInCombi = schemeIdx

            minDists.append(minDistInCombi) 

        
        # Group 내 배색칩들 중 에디토리얼 배색칩과 가장 유사한 배색을 찾는다
        minDist = 1000000
        for i in range(0, len(minDists)):
            if minDists[i] < minDist :
                minDist = minDists[i]


        return minDist, minDistSchemeIdxInCombi

                

    def analyzeColorScheme(self, rgbList) :
        self.group = ""
        self.colorScheme.clear()
        self.adjectives.clear()

        self.name_colors.clear()
        self.name_adjectives.clear()

        groupNames = []

        for name in self.groups :
            groupNames.append(name)


        for i in range(0, len(groupNames)) :
            groupName = groupNames[i]

            schemes = []
            for group in self.groups[groupName]["color-scheme"] :
                schemes.append(group)

            self.name_colors[groupName] = schemes
            self.name_adjectives[groupName] = self.groups[groupName]["adjective"]


        minDist = 1000000
        minIdx = 0
        minGroup = groupName[0]
        for i in range(0, len(groupNames)) :
            groupName = groupNames[i]

            # name_colors[groupName] : 비교할 배색칩들
            # rgbList : 에디토리얼 배색칩
            thisDist, thisSchemeIdx = self.getClosest(self.name_colors[groupName], rgbList)

            if thisDist < minDist :
                minDist = thisDist
                minIdx = thisSchemeIdx
                minGroup = groupName

        self.group = minGroup
        self.adjectives = self.name_adjectives[minGroup]
        self.colorScheme = self.name_colors[minGroup][minIdx]

        return self.group

