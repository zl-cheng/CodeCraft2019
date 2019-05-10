# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 15:23:07 2019

@Author: And-ZJ

@Content:
    可视化
    基于 https://github.com/AkatsukiCC/huawei2019-with-visualization
    
@Edited:

    图片扩大一倍。
    可以标识优先和预置等车。
    
    可以用原图大小绘制，可以扩大一倍绘制（不同大小，标记方案不同），可以控制普通车辆的是否显示同一颜色。
    
    修正排序方法。生成图片更有序。更改优先车为紫色。裁掉一部分图片白边。2019-04-08。

    修正裁切方法问题，对于非正方形也能裁。
    
    清空img数组，而不是新建。2019-04-09
    
    去掉random一个过期函数警告。
    
    将路口id摆放的更靠近中间的位置
    
    将路口颜色变浅。
    
    尝试减少原图绘制时间
    1. 将车位的小格子改用长条代表后，降低绘制时间。平均 500张(100s)片降低 18s。修正长条在图2中位置摆放不正确的问题。
    2. 每次绘制时都重新计算了小格子在图中的位置，将其保存在全局中，降低绘制时间。平均500张(100s)降低10s
    
    计算节点坐标的函数 2019-04-11
    
    不裁剪情况下，信息显示到左上角
    
    修复读取空行的BUG。2019-04-12 00:31
    
    car.txt 新旧兼容。
    
    尝试用CrossCoordinate文件中建立的坐标绘图。已完成 20190413
    
    实现跨节点作图。已完成 20190419
    
    生成图片提示位置。
    
"""

#%% 导包
import os
import numpy as np
import cv2 as cv
from time import time
import json
from collections import defaultdict
# from TimeTools import RunTime
# RunTime.init()
#%% 全局变量
np.random.seed(951105)
#%% Reader
def readTextFile(fileName):
    textLines = list()
    with open(fileName,'r',encoding='UTF-8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.rstrip()
            if line != '' and line[0] != '#':
                textLines.append(line)
    return textLines
#%% CAR
class CAR(object):
    def __init__(self,id_,from_,to_,speed_,planTime_,is_priority,is_preset):
        # **** statistic parameters ****#
        #@zj 修复这里预置和优先填反的BUG
        self.id_, self.from_, self.to_, self.speed_, self.planTime_,self.is_priority,self.is_preset = \
            id_, from_, to_, speed_, planTime_ ,is_priority, is_preset
        self.carColor = [int(value) for value in np.random.randint(0, 255+1, [3])]
        self.state,self.x,self.y = 0,0,0
        self.deltaX,self.deltaY=0,0
        self.presetTime = 0
        self.presetPath = []
    def __id__(self):
        return self.id_
    def __from__(self):
        return self.from_
    def __to__(self):
        return self.to_
    def __speed__(self):
        return  self.speed_
    def __planTime__(self):
        return self.planTime_
    def __carColor__(self):
        return self.carColor
    def getId(self):
        return self.__id__()
    def getFrom(self):
        return self.__from__()
    def getTo(self):
        return self.__to__()
    def getSpeed(self):
        return self.__speed__()
    def getPlanTime(self):
        return self.__planTime__()
    def isPriority(self):
        return self.is_priority    
    def isPreset(self):
        return self.is_preset
    def getPresetTime(self):
        return self.presetTime
    def getPresetPath(self):
        return self.presetPath
    def __x__(self):
        return self.x
    def __y__(self):
        return self.y
    

#%% ROAD
class ROAD(object):
    def __init__(self,id_, length_, speed_, channel_, from_, to_, isDuplex_):
        self.id_, self.length_, self.speed_, self.channel_, self.from_, self.to_, self.isDuplex_ = \
            id_, length_, speed_, channel_, from_, to_, isDuplex_
        self.carCapcity = self.channel_ * self.length_
        # absolute bucket
        self.forwardBucket = {i: [None for j in range(self.channel_)] for i in range(self.length_)}
        self.backwardBucket = {i: [None for j in range(self.channel_)] for i in
                               range(self.length_)} if self.isDuplex_ else None
    def __id__(self):
        return self.id_
    def __length__(self):
        return self.length_
    def __speed__(self):
        return self.speed_
    def __channel__(self):
        return self.channel_
    def __from__(self):
        return self.from_
    def __to__(self):
        return self.to_
    def __isDuplex__(self):
        return self.isDuplex_
    def __forwardBucket__(self):
        return self.forwardBucket
    def __backwardBucket__(self):
        return self.backwardBucket  
#%% CROSS
class CROSS(object):
    def __init__(self, id_, north_, east_, south_, west_):
        # **** statistic parameters ****#
        self.id_ = id_
        self.roadIds = [north_, east_, south_, west_]
        self.carport = {}
        self.left=[]
        # absolute loc
        self.x, self.y = 0, 0
        self.mapX,self.mapY = 0,0
        # priorityMap
        self.directionMap = {north_: {east_: 1, south_: 2, west_: -1}, \
                             east_: {south_: 1, west_: 2, north_: -1}, \
                             south_: {west_: 1, north_: 2, east_: -1}, \
                             west_: {north_: 1, east_: 2, south_: -1}}
        # relationship with roads
        self.providerDirection, self.receiverDirection, self.validRoadDirecction = [], [], []
        for index, roadId in enumerate(self.roadIds):

            if roadId is not None and roadId != -1:
                self.validRoadDirecction.append(index)

        self.validRoad = [self.roadIds[direction] for direction in self.validRoadDirecction]
        self.done = False
        self.update = False
   
    def direction(self,providerId,receiverId):
        return self.directionMap[providerId][receiverId]
    def setDone(self,bool):
        self.done = bool
    def setLoc(self,x,y):
        self.x,self.y = x,y
    def setMapLoc(self,mapX,mapY):
        self.mapX,self.mapY = mapX,mapY
    def roadDirection(self,roadId):
        if self.roadIds[0]==roadId:
            return 0
        elif self.roadIds[1]==roadId:
            return 1
        elif self.roadIds[2]==roadId:
            return 2
        elif self.roadIds[3]==roadId:
            return 3
        else:
            return -1
    def __id__(self):
        return self.id_
    def __roadIds__(self):
        return self.roadIds
    def __validRoadDirection__(self):
        return self.validRoadDirection
    def __provider__(self):
        return self.provider
    def __receiver__(self):
        return self.receiver
    def __validRoad__(self):
        return self.validRoad
    def __x__(self):
        # 坐标系
        return self.x
    def __y__(self):
        return self.y
    def __mapX__(self):
        # 像素距离
        return self.mapX
    def __mapY__(self):
        return self.mapY
    def __done__(self):
        return self.done
    def __loc__(self):
        return self.x,self.y
    def __mapLoc__(self):
        return self.mapX,self.mapY
    
#%% 从文件中读取车、道路、路口信息，并组成字典
# @RunTime.total()
def buildDict(car_path,road_path,cross_path,preAns_path,startCrossId=None,computeCoordinate=1):
    carInfo = readTextFile(car_path)
    roadInfo = readTextFile(road_path)
    crossInfo = readTextFile(cross_path)
    preAnsInfo = readTextFile(preAns_path)
    
    # Create NameSpace And Dictionary
    CARNAMESPACE,ROADNAMESPACE,CROSSNAMESPACE = [],[],[]
    CROSSDICT,CARDICT,ROADDICT ={},{},{}
    COLORDICT = {}
    CROSSDICT_INFO = {}
    # create car objects
    # line = (id,from,to,speed,planTime)
    for line in carInfo:
        infos = line.replace(' ', '').replace('\t', '')[1:-1].split(',')
        id_, from_, to_, speed_, planTime_,  = infos[0:5]
        if len(infos) == 7:
            is_priority, is_preset = infos[5:7]
        else:
            is_priority, is_preset = False,False
        CARNAMESPACE.append(int(id_))
        CARDICT[int(id_)] = CAR(int(id_), int(from_), int(to_), int(speed_), int(planTime_),int(is_priority), int(is_preset))
        COLORDICT[int(id_)] = CARDICT[int(id_)].__carColor__()
    
    for line in preAnsInfo:
        infos = line.replace(' ','').replace('\t','')[1:-1].split(',')
        id_,startTime_ = infos[0:2]
        path_ = infos[2:]
        car = CARDICT[int(id_)]
        car.presetTime = int(startTime_)
        car.presetPath = [int(p) for p in path_]
    
    # create road objects
    # line = (id,length,speed,channel,from,to,isDuplex)
    for line in roadInfo:
        infos = line.replace(' ', '').replace('\t', '')[1:-1].split(',')
        id_, length_, speed_, channel_, from_, to_, isDuplex_ = infos[0:7]
        ROADNAMESPACE.append(int(id_))
        ROADDICT[int(id_)] = ROAD(int(id_), int(length_), int(speed_), int(channel_), int(from_), int(to_),
                                  int(isDuplex_))
    
    # create cross objects
    # line = (id,north,east,south,west)
    visitDone = {}
    for line in crossInfo:
        infos = line.replace(' ', '').replace('\t', '')[1:-1].split(',')
        id_, north_, east_, south_, west_ = infos[0:5]
        CROSSNAMESPACE.append(int(id_))
        visitDone[int(id_)] = False
        CROSSDICT_INFO[int(id_)] = [int(north_), int(east_), int(south_), int(west_)]
        CROSSDICT[int(id_)] = CROSS(int(id_),int(north_), int(east_), int(south_), int(west_))
    
    if computeCoordinate == 1:
        CROSSDICT.clear()
        def DFS(crossId,direction=None,preCrossId=None):
            if visitDone[crossId]:
                return
            visitDone[crossId] = True
            if preCrossId is not None:
                for i in range(4):
                    roadId = CROSSDICT_INFO[crossId][i]
                    if roadId!=-1:
                        pcId = ROADDICT[roadId].__from__() if ROADDICT[roadId].__from__()!= crossId else ROADDICT[roadId].__to__()
                        if pcId == preCrossId:
                            break
                shift=((i+2)%4-direction)%4
                for i in range(shift):
                    CROSSDICT_INFO[crossId]=[CROSSDICT_INFO[crossId][1],CROSSDICT_INFO[crossId][2],CROSSDICT_INFO[crossId][3],CROSSDICT_INFO[crossId][0]]
            for i in range(4):
                roadId = CROSSDICT_INFO[crossId][i]
                if roadId!=-1:
                    nextCrossId = ROADDICT[roadId].__from__() if ROADDICT[roadId].__from__()!= crossId else ROADDICT[roadId].__to__()
                    DFS(nextCrossId,i,crossId)
        DFS(CROSSNAMESPACE[0])
        for crossId in CROSSNAMESPACE:
            north_,east_,south_,west_ = CROSSDICT_INFO[crossId]
            CROSSDICT[crossId] = CROSS(crossId,north_,east_,south_,west_)
        directionDict,nebDict = None,None
    else:
        from CrossCoordinate import buildDirection
        if startCrossId is None:
            startCrossId = list(CROSSDICT.keys())[0]
        directionDict,nebDict = buildDirection(ROADDICT,CROSSDICT,startCrossId)
        CROSSDICT.clear()
        for crossId in CROSSNAMESPACE:
            north_,east_,south_,west_ = directionDict[crossId]
            CROSSDICT[crossId] = CROSS(crossId,north_,east_,south_,west_)
    
    return CARDICT,ROADDICT,CROSSDICT,CARNAMESPACE,ROADNAMESPACE,CROSSNAMESPACE,directionDict,nebDict

#%% Visualization
class Visualization(object):
    def __init__(self,car_path,road_path,cross_path,preAns_path,savePath,**kwargs):
        """
        Parameters
        ----------
        car_path : str
            car.txt 的路径. 如 "C:/car.txt"
        road_path : str
            road.txt 的路径.
        cross_path : str
            cross.txt 的路径.
        preAns_path : str
            presetAnswer.txt 的路径.
        savePath : str
            存放生成的图片的目录. 如 "C:/imgs/"
        **kwargs : dict
            其他控制参数，可不传递，使用默认即可。
            randomColor = False 参数控制普通车子是否使用随机颜色标色，默认为False，即不随机，普通车统一用绿色标色。
                普通车用绿色
                优先车用紫色
                预置车用蓝色
                优先预置车用红色
            sizeExpand = 1 参数，控制图的大小，默认为1倍，即原来的图，以及不同车标记不同色的方案。可选为2。
                若为2，则在旁边标记是否是特殊车辆（不建议使用该值）。
            showRoadInfo = True 参数，控制是否显示红色的道路情况信息，默认True
            reduceDraw = 0 参数，选择减少绘制的方式，默认为2（不建议使用其他值）。
                0: 原作者绘制方式，每500张图片100s。只在0时，sizeExpand参数有效。
                1：采用长条方案，减少18s。
                2：长条方案+预计算位置：比1方式再减少10s。
            computeCoordinate = 1 参数。默认为1，即原作者坐标计算方式。
                若为2，计算方式增强，可以计算道路跨坐标（如map-stange-*中的图）的图（要用到 CrossCoordinate.py 文件）。
        Returns
        -------
        self object.

        """
        self.maxX,self.maxY = 0,0
        if not os.path.exists(savePath):
            #@zj 自动新建可视化图片的保存文件夹
            print('新建文件夹:',savePath)
            os.makedirs(savePath)
        self.savePath = savePath
        self.preAnsPath = preAns_path
        
        self.randomColor = kwargs.get('randomColor',False)
        # 普通车颜色是否随机
        
        self.sizeExpand = kwargs.get('sizeExpand',1) 
        # 如果是1，则原图，标记方案用原方案
        # 如果是2，则新图，标记方案用新方案
        
        # reduceDraw = 0 参数，默认为2。只在0时，sizeExpand参数有效。
        #       选择减少绘制的方式。1：采用长条方案，每500张图片（原100s）减少18秒。2：长条方案+预计算位置：比1方式再减少10s。
        self.reduceDraw = kwargs.get('reduceDraw',2)
        
        # 减少绘制时间方案中，长条的颜色
        self.roadPosColor = (230,210,160) # 淡蓝色？
        
        # 是否裁切图片
        self.clipImg = kwargs.get('clipImg',True)
        
        # self.moreInfo = kwargs.get('moreInfo',None)
        self.showRoadInfo = kwargs.get('showRoadInfo',True)
        # 
        # self.commonCarColor = [25,225,0] # 普通车统一颜色，绿色
        self.commonCarColor = [50,225,50] # 普通车统一颜色，绿色，稍亮一点
      
        self.crossColor = [25,255,0] # 路口颜色，淡绿色
        
        if self.sizeExpand <= 1 or self.reduceDraw != 0:
            self.crossRadius = 14
            self.crossDistance = 150
            
            # B G R
            self.presetCarColor = [255,0,0] # 预置车辆，蓝色
            self.priorityCarColor = [255,0,255] # 优先车辆，紫色
            self.bothCarColor = [0,0,255] # 优先预置车辆，红色
            self.channelDistance = 3
            self.fontSize = 0.3
            
        else:
            # 扩大一倍采用新的标记法
            self.crossRadius = 14
            self.crossDistance = 300#150
            # B G R
            self.presetCarColor = [255,0,0] # 预置车辆，蓝色
            self.priorityCarColor = [255,0,255] # 优先车辆，紫色
            self.channelDistance = 5#3
            self.fontSize = 0.6
            
        # ** road param **#
        self.roadColor = [0,0,0] #black
        # self.roadLineType = 4
        self.channelWidth = 5
        
        self.lineWidth = 2
        
        computeCoordinate = kwargs.get('computeCoordinate',1)
        
        # self.time = 0
        self.CARDICT,self.ROADDICT,self.CROSSDICT,self.CARNAMESPACE,self.ROADNAMESPACE,self.CROSSNAMESPACE,self.directionDict,self.nebDict = buildDict(car_path,road_path,cross_path,preAns_path,computeCoordinate=computeCoordinate)
        
        self.carInRoadNums = 0

        if isinstance(computeCoordinate,str):
            # 从文件读取坐标
            self.crossLocGenFromFile(computeCoordinate)
        elif isinstance(computeCoordinate,int):
            if computeCoordinate == 1:
                # 原来方式
                self.crossLocGen()
            elif computeCoordinate == 2:
                # 可跨结点绘制
                self.crossLocGen2()
            else:
                assert False
        else:
            assert False
        
        jsonFileName = kwargs.get("jsonFileName",None);
        if jsonFileName is not None:
            self.drawFromJsonFile(jsonFileName)

    # @RunTime.total()
    def crossLocGen(self):
        #**** relative location ****#    
        # denote the first cross as the origin of coordinates
        for crossId in self.CROSSNAMESPACE:
            self.CROSSDICT[crossId].setDone(False)
        crossList = [self.CROSSNAMESPACE[0]]
        minX,minY = 0,0
        while(crossList.__len__()>0):
            nextCrossList = []
            for crossId in crossList:
                presentX,presntY = self.CROSSDICT[crossId].__loc__()
                validRoad = self.CROSSDICT[crossId].__validRoad__()
                for roadId in validRoad:
                    #next cross id   
                    nextCrossId = self.ROADDICT[roadId].__from__() if self.ROADDICT[roadId].__from__() != crossId \
                                                            else self.ROADDICT[roadId].__to__()
                    # if next cross is visited
                    if not self.CROSSDICT[nextCrossId].__done__():
                        # visit sets true
                        self.CROSSDICT[nextCrossId].setDone(True)
                        # relative location of nextcross
                        nextX,nextY = self.crossRelativeLoc(presentX,presntY,crossId,roadId)
                        # update location
                        self.CROSSDICT[nextCrossId].setLoc(nextX,nextY)
                        minX,minY,self.maxX,self.maxY=\
                                    min(nextX,minX),min(nextY,minY),max(nextX,self.maxX),max(nextY,self.maxY)
                        nextCrossList.append(nextCrossId)
            crossList = nextCrossList
        self.maxX,self.maxY = (self.maxX-minX+2)*self.crossDistance,(self.maxY-minY+2)*self.crossDistance
        for crossId in self.CROSSNAMESPACE:
            x,y = self.CROSSDICT[crossId].__loc__()
            self.CROSSDICT[crossId].setLoc(x-minX,y-minY)
            self.CROSSDICT[crossId].setMapLoc((x - minX+1)*self.crossDistance, (y - minY+1)*self.crossDistance)
        self.img = np.ones((self.maxY,self.maxX,3),np.uint8)*255
        
        self.drawBucketFun = None
        if self.sizeExpand <= 1:
            self.drawBucketFun = self.drawBucket
        else:
            self.drawBucketFun = self.drawBucket2
        if self.reduceDraw == 1:
            self.drawBucketFun = self.drawBucketWithReduceDraw
        elif self.reduceDraw == 2:
            self.drawBucketFun = self.drawBucketWithPrecal

        self.genRoadPos() # 预先计算位置
            
    # TODO 从自已生成的坐标 绘制地图 可跨节点绘制
    def crossLocGen2(self):
        from CrossCoordinate import computeMapXY,genMap
        startCrossId = self.CROSSNAMESPACE[0]
        # self.coordinateDict = buildCoordinate(self.ROADDICT,self.CROSSDICT,startCrossId)
        crossId_MapXY = computeMapXY(self.ROADDICT,self.CROSSDICT,self.directionDict,self.nebDict,startCrossId)
        self.coordinateDict = genMap(crossId_MapXY)
        
        crossId_MapXY = self.coordinateDict['crossId_MapXY']
        if len(crossId_MapXY) != len(self.CROSSDICT):
            raise Exception('Error: May be existed isolated point',len(crossId_MapXY),len(self.CROSSDICT))
        for crossId,crossXY in crossId_MapXY.items():
            self.CROSSDICT[crossId].setLoc(crossXY['x'],crossXY['y'])
        self.mapSize = self.coordinateDict['mapSize']
        self.maxX = (self.mapSize['x'] + 1) * self.crossDistance
        self.maxY = (self.mapSize['y'] + 1) * self.crossDistance
        for crossId,cross in self.CROSSDICT.items():
            # 这里指像素坐标
            pixelX = (cross.x + 1) * self.crossDistance
            pixelY = (cross.y + 1) * self.crossDistance            
            cross.setMapLoc(pixelX,pixelY)
        
        self.img = np.ones((self.maxY,self.maxX,3),np.uint8)*255
        
        self.drawBucketFun = None
        if self.sizeExpand <= 1:
            self.drawBucketFun = self.drawBucket
        else:
            self.drawBucketFun = self.drawBucket2
        if self.reduceDraw == 1:
            self.drawBucketFun = self.drawBucketWithReduceDraw
        elif self.reduceDraw == 2:
            self.drawBucketFun = self.drawBucketWithPrecal

        self.genRoadPos() # 预先计算位置
    
    def crossLocGenFromFile(self,coordinateFileName):
        # TODO 从文件读取坐标
        print('read CoordinateFile:',coordinateFileName)
        from CoordinateFileOper import readCoordinate,genMap
        crossId_MapXY = readCoordinate(coordinateFileName)
        self.coordinateDict = genMap(crossId_MapXY)
        
        crossId_MapXY = self.coordinateDict['crossId_MapXY']
        if len(crossId_MapXY) != len(self.CROSSDICT):
            raise Exception('Error: May be existed isolated point',len(crossId_MapXY),len(self.CROSSDICT))
        for crossId,crossXY in crossId_MapXY.items():
            self.CROSSDICT[crossId].setLoc(crossXY['x'],crossXY['y'])
        self.mapSize = self.coordinateDict['mapSize']
        self.maxX = (self.mapSize['x'] + 1) * self.crossDistance
        self.maxY = (self.mapSize['y'] + 1) * self.crossDistance
        
        for crossId,cross in self.CROSSDICT.items():
            # 这里指像素坐标
            pixelX = (cross.x + 1) * self.crossDistance
            pixelY = (cross.y + 1) * self.crossDistance            
            cross.setMapLoc(pixelX,pixelY)
        
        self.img = np.ones((self.maxY,self.maxX,3),np.uint8)*255
        
        self.drawBucketFun = None
        if self.sizeExpand <= 1:
            self.drawBucketFun = self.drawBucket
        else:
            self.drawBucketFun = self.drawBucket2
        if self.reduceDraw == 1:
            self.drawBucketFun = self.drawBucketWithReduceDraw
        elif self.reduceDraw == 2:
            self.drawBucketFun = self.drawBucketWithPrecal

        self.genRoadPos() # 预先计算位置
    
    def crossRelativeLoc(self,x,y,crossId,roadId):
        roadDirection = self.CROSSDICT[crossId].roadDirection(roadId)
        if roadDirection==0:
            return x,y-1
        elif roadDirection==1:
            return x+1,y
        elif roadDirection==2:
            return x,y+1
        elif roadDirection==3:
            return x-1,y
        else:
            print("Cross(%d) don't interact with road(%d)"%(self.id_,roadId))
    
    def buildCoordinate(self):
        crossDict = self.CROSSDICT
        crossNumsInEachRow = defaultdict(lambda :0)
        crossNumsInEachColumn = defaultdict(lambda :0)
        rowCrossNums = 0 # 横向结点个数
        columnCrossNums = 0
        
        for cross in crossDict.values():
            crossNumsInEachRow[cross.y] += 1
            crossNumsInEachColumn[cross.x] += 1
        # 长度和内容大小应该一样
        rowCrossNums = len(crossNumsInEachColumn)
        columnCrossNums = len(crossNumsInEachRow)
        mapXY_CrossIdNp = np.ones([rowCrossNums,columnCrossNums],int) * (-1)
        crossId_MapXY = dict() 
        for crossId,cross in crossDict.items():
            mapXY_CrossIdNp[cross.x,cross.y] = crossId
            crossId_MapXY[crossId] = {'x':cross.x,'y':cross.y}
        mapXY_CrossId = mapXY_CrossIdNp.tolist()
        res = {
                'mapXY_CrossId':mapXY_CrossId,      # list 格式: [x][y] -> crossId
                'crossId_MapXY':crossId_MapXY,      # crossId -> {'x':x,'y':y}
                'mapXY_CrossIdNp':mapXY_CrossIdNp,  # mapXY_CrossId 的 numpy 格式
                'mapSize': {'x':rowCrossNums,'y':columnCrossNums} # len(x) 与 len(y) 
            }
        return res
        
    
    # @RunTime.total()
    def genRoadPos(self):
        for roadId,road in self.ROADDICT.items():
            fromX, fromY = self.CROSSDICT[road.__from__()].__mapLoc__()
            toX, toY = self.CROSSDICT[road.__to__()].__mapLoc__()

            road.pos = (fromX,fromY,toX,toY)
            # ['forward'][channelNum]
            road.pos_channel = {}
            # pos_channel_car['forward'][i][j] = 
            road.pos_channel_car = dict()
            if self.sizeExpand <= 1:
                self.genRoadBucketPos(road,'forward')
                if road.__isDuplex__():
                    self.genRoadBucketPos(road,'backward')
            else:
                pass
            road.pos_info = {}
            self.genRoadInfoPos(road)
            
    # @RunTime.total()
    def genRoadBucketPos(self,road,lane):
        # print('genRoadBucketPos')
        # 用长条代替小格子，减少绘制时间
        # bucket = road.__forwardBucket__() if lane !='backward' else road.__backwardBucket__()
        length = road.__length__() 
        channel = road.__channel__()
        fromX, fromY = self.CROSSDICT[road.__from__()].__mapLoc__()
        toX, toY = self.CROSSDICT[road.__to__()].__mapLoc__()
        XY, intervalXY, rectangleSize, channel2XY, length2XY = self.bucketDrawInitial(fromX,fromY,toX,toY,lane,length)

        nXY = XY.copy()
        road.pos_channel[lane] = list()
        # 将原来绘制小格子的地方绘制成长条
        #@zj 你要问我，为什么这样绘制长条，我只能说，画图试出来的555。
        direction = self.bucketDirection(fromX,fromY,toX,toY,lane)
        if direction == 'north':
            for j in range(channel):
                channelSXY = (XY[0],XY[1])
                channelEXY = (XY[0] + rectangleSize[0], XY[1] + length * rectangleSize[1])
                XY[0] = XY[0] + intervalXY[0]
                road.pos_channel[lane].append( (int(channelSXY[0]), int(channelSXY[1]), int(channelEXY[0]), int(channelEXY[1])) )
        elif direction == 'south':
            for j in range(channel):
                channelSXY = (XY[0] + rectangleSize[0],XY[1] + rectangleSize[1])
                channelEXY = (XY[0], XY[1] - (length-1) * rectangleSize[1])
                XY[0] = XY[0] + intervalXY[0]
                road.pos_channel[lane].append( (int(channelSXY[0]), int(channelSXY[1]), int(channelEXY[0]), int(channelEXY[1])) )
        elif direction == 'east':
            for j in range(channel):
                channelSXY = (XY[0] + rectangleSize[0],XY[1] + rectangleSize[1])
                channelEXY = (XY[0] - (length-1) * rectangleSize[0], XY[1] )
                XY[1] = XY[1] + intervalXY[1]
                road.pos_channel[lane].append( (int(channelSXY[0]), int(channelSXY[1]), int(channelEXY[0]), int(channelEXY[1])) )
        elif direction == 'west':
            for j in range(channel):
                channelSXY = (XY[0],XY[1])
                channelEXY = (XY[0] + length * rectangleSize[0], XY[1] + rectangleSize[1])
                XY[1] = XY[1] + intervalXY[1]
                road.pos_channel[lane].append( (int(channelSXY[0]), int(channelSXY[1]), int(channelEXY[0]), int(channelEXY[1])) )
        XY = nXY
        
        # 车道中每个小格子的绘制坐标
        road.pos_channel_car[lane] = [None] * length
        for i in range(length):
            road.pos_channel_car[lane][i] = [None] * channel 
            for j in range(channel):
                xRD,yRD = int(XY[0]+rectangleSize[0]),int(XY[1]+rectangleSize[1])
                road.pos_channel_car[lane][i][j] = (int(XY[0]),int(XY[1]),xRD,yRD)
                XY[channel2XY] = XY[channel2XY] + intervalXY[channel2XY]
            XY[channel2XY] = XY[channel2XY] - intervalXY[channel2XY]*channel
            XY[length2XY] = XY[length2XY] + intervalXY[length2XY]
    
    def genRoadInfoPos(self,road):
        # 道路信息位置
        channel = road.__channel__()
        fromX, fromY = self.CROSSDICT[road.__from__()].__mapLoc__()
        toX, toY = self.CROSSDICT[road.__to__()].__mapLoc__()
        id_pos_x = (fromX + toX) / 2
        id_pos_y = (fromY + toY) / 2
        dire_pos_x = id_pos_x
        dire_pos_y = id_pos_y
        spee_pos_x = id_pos_x
        spee_pos_y = id_pos_y
        nums_pos_x = id_pos_x
        nums_pos_y = id_pos_y
        direction = self.bucketDirection(fromX,fromY,toX,toY,'forward')
        if direction == 'north' or direction == 'south':
            id_pos_x += channel * (self.channelWidth + self.channelDistance) # 8
            id_pos_y += 2 * self.channelWidth # 10 
            dire_pos_x = id_pos_x
            dire_pos_y = id_pos_y + 30 * self.fontSize # 10
            spee_pos_x = dire_pos_x
            spee_pos_y = dire_pos_y + 30 * self.fontSize #10
            nums_pos_x = spee_pos_x
            nums_pos_y = spee_pos_y + 30 * self.fontSize #13
        if direction ==  'east' or direction == 'west':
            id_pos_y += 30 * self.fontSize
            id_pos_y += channel * (self.channelWidth + self.channelDistance)
            id_pos_x  = min(fromX,toX) + 6 * (self.channelWidth + self.channelDistance)
            dire_pos_y = id_pos_y + 30 * self.fontSize
            dire_pos_x = id_pos_x
            spee_pos_y = dire_pos_y + 30 * self.fontSize
            spee_pos_x = id_pos_x
            nums_pos_y = spee_pos_y + 30 * self.fontSize
            nums_pos_x = spee_pos_x
        road.pos_info['id'] = (int(id_pos_x),int(id_pos_y))
        road.pos_info['dire'] = (int(dire_pos_x),int(dire_pos_y))
        road.pos_info['spee'] = (int(spee_pos_x),int(spee_pos_y))
        road.pos_info['nums'] = (int(nums_pos_x),int(nums_pos_y))
        
    # @RunTime.total()
    def drawBucketWithPrecal(self,road,lane,img):
        bucket = road.__forwardBucket__() if lane !='backward' else road.__backwardBucket__()
        length = road.__length__() 
        channel = road.__channel__()
        fromX, fromY = self.CROSSDICT[road.__from__()].__mapLoc__()
        toX, toY = self.CROSSDICT[road.__to__()].__mapLoc__()
        
        # print(road.pos_channel)
        
        # print(road.pos_channel)
        for j in range(channel):
            cv.rectangle(img,(road.pos_channel[lane][j][0],road.pos_channel[lane][j][1]),(road.pos_channel[lane][j][2],road.pos_channel[lane][j][3]),self.roadPosColor,1)

        for i in range(length):
            for j in range(channel):
                if bucket[i][j] is  None:
                    pass
                else:
                    currCar = self.CARDICT[bucket[i][j]]
                    color = self.commonCarColor
                    if self.randomColor:
                        color = currCar.__carColor__()
                    # 特殊车辆标识  
                    if currCar.isPreset() and currCar.isPriority():
                        color = self.bothCarColor
                    elif currCar.isPreset():
                        color = self.presetCarColor
                    elif currCar.isPriority():
                        color = self.priorityCarColor
                    pos = road.pos_channel_car[lane][i][j] 
                    cv.rectangle(img, (pos[0], pos[1]),(pos[2], pos[3]),color=color,thickness=-1)

    def setSavePath(self,savePath):
        self.savePath = savePath
        
    # @RunTime.total()
    def save(self,timeStamp,img):
        cv.imwrite(self.savePath+'/{0}.jpg'.format(timeStamp),img)
        print('生成图片：',self.savePath,'{0}.jpg'.format(timeStamp))

    # @RunTime.total()
    def drawMap(self,timeStamp=time(),moreInfo=None,**kwargs):
        img = self.img
        #draw road
        for roadId in self.ROADNAMESPACE:
            self.plotRoad(roadId,img,**kwargs)
        # draw cross
        for crossId in self.CROSSNAMESPACE:
            self.plotCross(crossId,img)
            
        # plot info
        self.plotInfo(img,timeStamp,**kwargs)
        # self.plotMoreInfo(img,moreInfo)
        
        if self.clipImg:
            cutX = (90*self.sizeExpand,self.maxX - 50*self.sizeExpand)
            cutY = (90*self.sizeExpand,self.maxY - 80*self.sizeExpand)
            cutImg = img[cutY[0]:cutY[1],cutX[0]:cutX[1]]
            self.save(timeStamp,cutImg) 
        else:
            self.save(timeStamp,img) 
        # self.save(timeStamp,img) 
        img.fill(255)
        
    # @RunTime.total()
    def plotCross(self,crossId,img):
        x, y = self.CROSSDICT[crossId].__mapLoc__()
        cv.circle(img,(x,y),self.crossRadius,color=self.crossColor,thickness=1,lineType=-1)
        if crossId>=10:
            xx, yy = int(x - 4*self.crossRadius/5), int(y + self.crossRadius / 2)
        else:
            xx, yy = int(x- self.crossRadius/2), int(y + self.crossRadius / 2)
        crossIdStr = str(crossId)
        xx -= 5
        if len(crossIdStr) >= 3:
            xx -= 5
        cv.putText(img,crossIdStr,(xx,yy ),cv.FONT_HERSHEY_SIMPLEX,0.6,[0,0,255],2)
        
    # @RunTime.total()
    def plotRoad(self,roadId,img,**kwargs):
        # get road info
        road = self.ROADDICT[roadId]
        fromX, fromY = self.CROSSDICT[road.__from__()].__mapLoc__()
        toX, toY = self.CROSSDICT[road.__to__()].__mapLoc__()
        # plot line
        cv.line(img,(fromX, fromY),(toX, toY),color=self.roadColor,thickness=1)
        # plot bucket

        self.drawBucketFun(road,'forward',img)
        
        if road.__isDuplex__():
            self.drawBucketFun(road,'backward',img)
        self.plotRoadInfo(road,img,**kwargs)
        
    # @RunTime.total()
    def drawBucket(self,road,lane,img):
        bucket = road.__forwardBucket__() if lane !='backward' else road.__backwardBucket__()
        length = road.__length__()
        channel = road.__channel__()
        fromX, fromY = self.CROSSDICT[road.__from__()].__mapLoc__()
        toX, toY = self.CROSSDICT[road.__to__()].__mapLoc__()
        XY, intervalXY, rectangleSize, channel2XY, length2XY = self.bucketDrawInitial(fromX,fromY,toX,toY,lane,length)
        
        for i in range(length):
            for j in range(channel):
                xRD,yRD = int(XY[0]+rectangleSize[0]),int(XY[1]+rectangleSize[1])
                if bucket[i][j] is  None:
                    pass
                    cv.rectangle(img,(int(XY[0]),int(XY[1])),(xRD,yRD),(0,0,0),1)
                else:
                    currCar = self.CARDICT[bucket[i][j]]
                    color = self.commonCarColor
                    if self.randomColor:
                        color = currCar.__carColor__()
                    # 特殊车辆标识  
                    if currCar.isPreset() and currCar.isPriority():
                        color = self.bothCarColor
                    elif currCar.isPreset():
                        color = self.presetCarColor
                    elif currCar.isPriority():
                        color = self.priorityCarColor
                    cv.rectangle(img, (int(XY[0]), int(XY[1])),(xRD, yRD),color=color,thickness=-1)
                XY[channel2XY] = XY[channel2XY] + intervalXY[channel2XY]
            XY[channel2XY] = XY[channel2XY] - intervalXY[channel2XY]*channel
            XY[length2XY] = XY[length2XY] + intervalXY[length2XY]
    
    # @RunTime.total()
    def drawBucketWithReduceDraw(self,road,lane,img):
        # 用长条代替小格子，减少绘制时间
        bucket = road.__forwardBucket__() if lane !='backward' else road.__backwardBucket__()
        length = road.__length__() 
        channel = road.__channel__()
        fromX, fromY = self.CROSSDICT[road.__from__()].__mapLoc__()
        toX, toY = self.CROSSDICT[road.__to__()].__mapLoc__()
        XY, intervalXY, rectangleSize, channel2XY, length2XY = self.bucketDrawInitial(fromX,fromY,toX,toY,lane,length)
        direction = self.bucketDirection(fromX,fromY,toX,toY,lane)

        nXY = XY.copy()
        
        # 将原来绘制小格子的地方绘制成长条
        #@zj 你要问我，为什么这样绘制长条，我只能说，画图试出来的555。
        if direction == 'north':
            for j in range(channel):
                channelSXY = (XY[0],XY[1])
                channelEXY = (XY[0] + rectangleSize[0], XY[1] + length * rectangleSize[1])
                XY[0] = XY[0] + intervalXY[0]
                cv.rectangle(img,(int(channelSXY[0]),int(channelSXY[1])),(int(channelEXY[0]),int(channelEXY[1])),self.roadPosColor,1)
        elif direction == 'south':
            for j in range(channel):
                channelSXY = (XY[0] + rectangleSize[0],XY[1] + rectangleSize[1])
                channelEXY = (XY[0], XY[1] - (length-1) * rectangleSize[1])
                XY[0] = XY[0] + intervalXY[0]
                cv.rectangle(img,(int(channelSXY[0]),int(channelSXY[1])),(int(channelEXY[0]),int(channelEXY[1])),self.roadPosColor,1)
        elif direction == 'east':
            for j in range(channel):
                channelSXY = (XY[0] + rectangleSize[0],XY[1] + rectangleSize[1])
                channelEXY = (XY[0] - (length-1) * rectangleSize[0], XY[1] )
                XY[1] = XY[1] + intervalXY[1]
                cv.rectangle(img,(int(channelSXY[0]),int(channelSXY[1])),(int(channelEXY[0]),int(channelEXY[1])),self.roadPosColor,1)
        elif direction == 'west':
            for j in range(channel):
                channelSXY = (XY[0],XY[1])
                channelEXY = (XY[0] + length * rectangleSize[0], XY[1] + rectangleSize[1])
                XY[1] = XY[1] + intervalXY[1]
                cv.rectangle(img,(int(channelSXY[0]),int(channelSXY[1])),(int(channelEXY[0]),int(channelEXY[1])),self.roadPosColor,1)
        
        XY = nXY
        xRD,yRD = int(XY[0]+rectangleSize[0]),int(XY[1]+rectangleSize[1])
        cv.rectangle(img,(int(XY[0]),int(XY[1])),(xRD,yRD),(0,0,0),1)
        for i in range(length):
            for j in range(channel):
                xRD,yRD = int(XY[0]+rectangleSize[0]),int(XY[1]+rectangleSize[1])
                if bucket[i][j] is  None:
                    pass
                    # cv.rectangle(img,(int(XY[0]),int(XY[1])),(xRD,yRD),(0,0,0),1)
                else:
                    currCar = self.CARDICT[bucket[i][j]]
                    color = self.commonCarColor
                    if self.randomColor:
                        color = currCar.__carColor__()
                    # 特殊车辆标识  
                    if currCar.isPreset() and currCar.isPriority():
                        color = self.bothCarColor
                    elif currCar.isPreset():
                        color = self.presetCarColor
                    elif currCar.isPriority():
                        color = self.priorityCarColor
                    cv.rectangle(img, (int(XY[0]), int(XY[1])),(xRD, yRD),color=color,thickness=-1)
                XY[channel2XY] = XY[channel2XY] + intervalXY[channel2XY]
            XY[channel2XY] = XY[channel2XY] - intervalXY[channel2XY]*channel
            XY[length2XY] = XY[length2XY] + intervalXY[length2XY]
    
    # @RunTime.total()
    def drawBucket2(self,road,lane,img):
        # 图片扩大一倍时采用的标记法
        bucket = road.__forwardBucket__() if lane !='backward' else road.__backwardBucket__()
        length = road.__length__()
        channel = road.__channel__()
        fromX, fromY = self.CROSSDICT[road.__from__()].__mapLoc__()
        toX, toY = self.CROSSDICT[road.__to__()].__mapLoc__()
        XY, intervalXY, rectangleSize, channel2XY, length2XY = self.bucketDrawInitial(fromX,fromY,toX,toY,lane,length)
        for i in range(length):
            for j in range(channel):
                xRD,yRD = int(XY[0]+rectangleSize[0]),int(XY[1]+rectangleSize[1])
                if bucket[i][j] is  None:
                    pass
                    cv.rectangle(img,(int(XY[0]),int(XY[1])),(xRD,yRD),(0,0,0),1)
                else:
                    currCar = self.CARDICT[bucket[i][j]]
                    isSpecial = False
                    color = currCar.__carColor__()
                    # 特殊车辆标识
                    if currCar.isPreset():
                        isSpecial = True
                        if channel2XY == 0:
                            # 南北走向
                            cv.rectangle(img, (int(XY[0]-3), yRD-4),(int(XY[0]),yRD-1),color=self.presetCarColor,thickness=-1)
                        else:
                            cv.rectangle(img, (int(XY[0])+1, int(XY[1])),(int(XY[0])+4, int(XY[1])-3),color=self.presetCarColor,thickness=-1)
                    if currCar.isPriority():
                        isSpecial = True
                        if channel2XY == 0:
                            # 南北走向
                            cv.rectangle(img, (int(XY[0]), int(XY[1])+1),(int(XY[0])-3, int(XY[1])+4),color=self.priorityCarColor,thickness=-1)
                        else:
                            cv.rectangle(img, (xRD-4, int(XY[1])-3),(xRD-1, int(XY[1])),color=self.priorityCarColor,thickness=-1)
                    if not isSpecial and not self.randomColor:
                        color = self.commonCarColor
                    cv.rectangle(img, (int(XY[0]), int(XY[1])),(xRD, yRD),color=color,thickness=-1)
                XY[channel2XY] = XY[channel2XY] + intervalXY[channel2XY]
            XY[channel2XY] = XY[channel2XY] - intervalXY[channel2XY]*channel
            XY[length2XY] = XY[length2XY] + intervalXY[length2XY]
    
    # @RunTime.total()
    def bucketDrawInitial(self,fromX,fromY,toX,toY,lane,length):
        direction = self.bucketDirection(fromX,fromY,toX,toY,lane)
        unitLength = (self.crossDistance - self.crossRadius * 4) / length
        if lane=='backward':
            toY=fromY
            toX=fromX
        if direction == 'north':
            XY = [fromX + self.channelDistance,toY + self.crossRadius * 2]
            intervalXY = self.channelDistance  + self.channelWidth , unitLength
            rectangleSize = self.channelWidth , unitLength
            channel2XY, length2XY = 0, 1
        elif direction == 'south':
            XY = [fromX - self.channelDistance - self.channelWidth,toY - self.crossRadius * 2 - unitLength]
            intervalXY = -(self.channelDistance  + self.channelWidth ), -unitLength
            rectangleSize = self.channelWidth , unitLength
            channel2XY, length2XY = 0, 1
        elif direction == 'east':
            XY = [toX - self.crossRadius * 2 - unitLength,fromY + self.channelDistance]
            intervalXY = -unitLength, self.channelDistance + self.channelWidth
            rectangleSize = unitLength, self.channelWidth
            channel2XY, length2XY = 1, 0
        elif direction == 'west':
            XY = [toX + self.crossRadius * 2, fromY - self.channelDistance - self.channelWidth]
            intervalXY = unitLength, -(self.channelDistance + self.channelWidth)
            rectangleSize = unitLength, self.channelWidth
            channel2XY, length2XY = 1, 0
        return XY,intervalXY,rectangleSize,channel2XY,length2XY
    
    def bucketDirection(self,fromX,fromY,toX,toY,lane):
        if fromY > toY:
            direction = 'north' if lane=='forward' else 'south'
        elif fromY < toY:
            direction = 'south' if lane == 'forward' else 'north'
        elif fromX < toX:
            direction = 'east' if lane == 'forward' else 'west'
        else:
            direction = 'west' if lane == 'forward' else 'east'
        return direction
    
    # @RunTime.total()
    def plotInfo(self,img,timeStamp=None,**kwargs):
        if timeStamp is not None:
            if self.clipImg:
                x = 90*self.sizeExpand+10
                y = 90*self.sizeExpand+20
            else:
                x = 30
                y = 30
            cv.putText(img, '{0}/ {1}.jpg / {2}'.format(self.savePath,timeStamp,self.carInRoadNums),\
                       (x,y), cv.FONT_HERSHEY_SIMPLEX, 0.6, [0, 0, 255], 1)
        pass
        # for crossId in self.CROSSNAMESPACE:
        #     cross = self.CROSSDICT[crossId]
        #     x,y = cross.__mapLoc__()
        #     cn,fn = cross.__carportCarNum__(),cross.__finishCarNum__()
        #     cv.putText(img,"%d,%d"%(cn,fn),(int(x),int(y-1.1*self.crossRadius)),\
        #                cv.FONT_HERSHEY_SIMPLEX,0.4,[0,0,255],1)
        # cv.putText(img, "in the carport:%d,on the road:%d,end of the trip:%d" % (CARDISTRIBUTION[0],CARDISTRIBUTION[1],CARDISTRIBUTION[2]),(30,30), \
        #            cv.FONT_HERSHEY_SIMPLEX, 0.6, [0, 0, 255], 2)
    
    # @RunTime.total()
    def plotMoreInfo(self,img,moreInfo:str=None):
        if moreInfo is not None and moreInfo != '':
            cv.putText(img, moreInfo,(30,70), cv.FONT_HERSHEY_SIMPLEX, 1.0, [0, 0, 255], 1)
            
    # @RunTime.total()
    def plotRoadInfo(self,road,img,**kwargs):
        # 绘制道路信息
        showRoadInfo = kwargs.get('showRoadInfo',self.showRoadInfo)
        if not showRoadInfo:
            return
        
        # 绘制道路编号
        cv.putText(img,"%d"%(road.__id__()),(road.pos_info['id'][0],road.pos_info['id'][1]),\
                        cv.FONT_HERSHEY_SIMPLEX,self.fontSize,[0,0,255],1)   
        
        # 绘制方向信息
        cv.putText(img,"%d->%d"%(road.__from__(),road.__to__()),(road.pos_info['dire'][0],road.pos_info['dire'][1]),\
                        cv.FONT_HERSHEY_SIMPLEX,self.fontSize,[0,0,255],1)
        # 绘制长度和速度信息
        cv.putText(img,"%d,%d"%(road.__length__(),road.__speed__()), \
                    (road.pos_info['spee'][0],road.pos_info['spee'][1]),\
                    cv.FONT_HERSHEY_SIMPLEX,self.fontSize,[0,0,255],1)    
        
        # 绘制每条道路上车数
        if hasattr(self,'carInEachRoadNums'):
            s = '{0},{1},{2}/{3},{4},{5}'.format(self.carInEachRoadNums[road.__id__()][road.__to__()],\
                 self.priorityCarInEachRoadNums[road.__id__()][road.__to__()],\
                 self.presetCarInEachRoadNums[road.__id__()][road.__to__()],\
                 self.carInEachRoadNums[road.__id__()][road.__from__()],\
                 self.priorityCarInEachRoadNums[road.__id__()][road.__from__()],\
                 self.presetCarInEachRoadNums[road.__id__()][road.__from__()],\
                 )
            cv.putText(img,s,\
                       (road.pos_info['nums'][0],road.pos_info['nums'][1]),cv.FONT_HERSHEY_SIMPLEX,self.fontSize,[0,0,255],1)
    # @RunTime.show()
    def drawImgsFromJsonFile(self,jsonFileName:str,**kwargs):
        # 读取json文件
        print('正在读取 JSON 文件：',jsonFileName)
        with open(jsonFileName,'r',encoding='utf-8') as f:
            jsonStr = f.read()
        jsonDict = self.covertJsonStrToDict(jsonStr)
        print('开始逐张生成图片')
        self.drawImgsFromJsonDict(jsonDict,**kwargs)
        
    # @RunTime.total()
    def covertJsonStrToDict(self,jsonStr):
        # 将json字符串，转为 dict
        newJsonDict = {}
        jsonDict = json.loads(jsonStr)
        for timeStamp,timeJsonStr in jsonDict.items():
            newTimeJsonDict = {}
            timeJson = timeJsonStr
            if isinstance(timeJsonStr,str):
                timeJson = json.loads(timeJsonStr)
            for roadId,roadJsonStr in timeJson.items():
                newRoadJsonDict = {}
                roadJson = roadJsonStr
                if isinstance(roadJsonStr,str):
                    roadJson = json.loads(roadJsonStr)
                # road = self.ROADDICT[roadId]
                for channelNum,channelJsonStr in roadJson.items():
                    newChannelJsonDict = {}
                    channelJson = channelJsonStr
                    if isinstance(channelJsonStr,str):
                        channelJson = json.loads(channelJsonStr)
                    for carId,pos in channelJson.items():
                        newChannelJsonDict[carId] = pos
                    newRoadJsonDict[channelNum] = newChannelJsonDict
                newTimeJsonDict[roadId] = newRoadJsonDict
            newJsonDict[timeStamp] = newTimeJsonDict
        return newJsonDict
    
    def drawImgsFromJsonDict(self,jsonDict:dict,**kwargs):
        """
        json文件/字典结构：
        jsonDict = {
            "timeStamp":{
                "roadId":{
                    "channelNum":{
                        "carId":pos,
                    },
                },
            },
        }
        channelNum：正向车道，则channelNum是正向车道的车道号 0 ~ channel-1
                对于逆向车道，则channelNum是逆向车道的车道号+车道数 channel ~ channel*2 -1
        """
        # sortName = sorted(list(jsonDict.keys()))
        # for name in sortName:
        #     timeJsonDict = jsonDict[name]
        #     self.drawImg(name,timeJsonDict,**kwargs)
        nameList = list(jsonDict.keys())
        namePairList = [(name.zfill(10),name) for name in nameList]
        namePairList.sort(key=lambda namePair:namePair[0])
        start = kwargs.get('start',None)
        end = kwargs.get('end',None)
        if start is None:
            start = 0
        if end is None:
            end = len(namePairList)
        print('图片总数：{0}'.format(len(namePairList)))
        print('range:[{0},{1}]'.format(start,end))
        namePairList = namePairList[start:end] 
        for namePair in namePairList:
            name = namePair[1]
            timeJsonDict = jsonDict[name]
            self.drawImg(name,timeJsonDict,**kwargs)
    
    # @RunTime.total()
    def drawInit(self):
        # 初始化道路状态
        if not hasattr(self,'carInEachRoadNums'):
            self.carInEachRoadNums = dict() 
            self.priorityCarInEachRoadNums = dict()
            self.presetCarInEachRoadNums = dict()
        for roadId,road in self.ROADDICT.items():
            # 统计清零
            carInRoad = self.carInEachRoadNums.get(roadId,None)
            if carInRoad is None: 
                carInRoad = {} # defaultdict(lambda :0)
                self.carInEachRoadNums[roadId] = carInRoad
            carInRoad[road.__to__()] = 0 
            carInRoad[road.__from__()] = 0
            
            priorityCarInRoad = self.priorityCarInEachRoadNums.get(roadId,None)
            if priorityCarInRoad is None: 
                priorityCarInRoad = {} # defaultdict(lambda :0)
                self.priorityCarInEachRoadNums[roadId] = priorityCarInRoad
            priorityCarInRoad[road.__to__()] = 0 
            priorityCarInRoad[road.__from__()] = 0
            
            presetCarInRoad = self.presetCarInEachRoadNums.get(roadId,None)
            if presetCarInRoad is None: 
                presetCarInRoad = {} # defaultdict(lambda :0)
                self.presetCarInEachRoadNums[roadId] = presetCarInRoad
            presetCarInRoad[road.__to__()] = 0 
            presetCarInRoad[road.__from__()] = 0
            
            # 每个位置上清零
            for pos in range(road.__length__()):
                for channelNum in range(road.__channel__()):
                    road.forwardBucket[pos][channelNum] = None
                    if road.isDuplex_:
                        road.backwardBucket[pos][channelNum] = None    
    
    # @RunTime.total()
    def drawImg(self,timeStamp,timeJsonDict,moreInfo=None,**kwargs):
        """
        与 drawImgsFromJsonDict 参数关系：
        jsonDict = {
            timeStamp:timeJsonDict,
            ...
        }
        """
        # 传递时间戳与该时间的内容字典
        carInRoadNums = 0
        self.drawInit()
        for roadId,roadJson in timeJsonDict.items():
            roadId = int(roadId)
            road = self.ROADDICT[roadId]
            length = road.__length__()
            for channelNum,channelJson in roadJson.items():
                channelNum = int(channelNum)
                direction = 'forward'
                if channelNum >= road.__channel__():
                    direction = 'back'
                    channelNum = channelNum - road.__channel__()
                for carId,pos in channelJson.items():
                    #@zj            起始点
                    #@zj          c=0, c=1
                    #@zj i = 0 : [None,None]
                    #@zj i = 1 : [100 ,None]
                    #@zj i = 2 : [None,None]
                    #@zj i = 3 : [None,None]
                    #@zj            终止点
                    carId = int(carId)
                    pos = int(pos)
                    car = self.CARDICT[carId]
                    # print('carId:',carId,'pos:',pos,'channelNum',channelNum)
                    if direction == 'forward':
                        road.forwardBucket[length-pos-1][channelNum] = carId
                        self.carInEachRoadNums[roadId][road.__to__()] += 1
                        if car.isPriority():
                            self.priorityCarInEachRoadNums[roadId][road.__to__()] += 1
                        if car.isPreset():
                            self.presetCarInEachRoadNums[roadId][road.__to__()] += 1
                    else:
                        road.backwardBucket[length-pos-1][channelNum] = carId
                        self.carInEachRoadNums[roadId][road.__from__()] += 1
                        if car.isPriority():
                            self.priorityCarInEachRoadNums[roadId][road.__from__()] += 1
                        if car.isPreset():
                            self.presetCarInEachRoadNums[roadId][road.__from__()] += 1
                    carInRoadNums += 1
        # 将结构绘制
        self.carInRoadNums = carInRoadNums # 总车数
        self.drawMap(timeStamp,**kwargs,moreInfo=moreInfo)
        
    
    def drawStatusMap(self,timeStamp=time(),moreInfo=None,**kwargs):
        img = np.ones((self.maxY,self.maxX,3),np.uint8)*255
        for roadId in self.ROADNAMESPACE:
            self.plotRoad(roadId,img,**kwargs)
            
        # draw cross
        for crossId in self.CROSSNAMESPACE:
            self.plotCross(crossId,img)
        # plot info
        self.plotInfo(img,timeStamp,**kwargs)
        self.plotCrossesInfo(img,**kwargs)
        self.plotMoreInfo(img,moreInfo)
        cv.imwrite(self.savePath+'/{0}.jpg'.format(timeStamp),img)

    def plotCrossesInfo(self,img,**kwargs):
        fromDict = kwargs.get('fromDict')
        toDict = kwargs.get('toDict')
        for crossId,cross in self.CROSSDICT.items():
            x, y = cross.__mapLoc__()
            from_pos_x = x - 25
            from_pos_y = y - 18
            #@zj 修复可能没有数据的BUG
            info = '{0},{1}'.format(fromDict.get(crossId,0),toDict.get(crossId,0))
            cv.putText(img,info,(from_pos_x,from_pos_y),cv.FONT_HERSHEY_SIMPLEX,0.4,[0,255,0],1)
    
#%% main test
if __name__ == '__main__':
    
    config = '../2-map-training-1/'
    car_path    = config + 'car.txt'
    road_path   = config + 'road.txt'
    cross_path  = config + 'cross.txt'
    preAns_path = config + 'presetAnswer.txt' 
    savePath    = config + 'imgs'       #@zj 可视化图片的保存路径

    # 初始化
    # 注意此处传递的路径参数个数和顺序，其他接口不变
    # randomColor = False 参数控制普通车子是否使用随机颜色标色，默认为False，即不随机，普通车统一用绿色标色。
    #   普通车用绿色
    #   优先车用紫色
    #   预置车用蓝色
    #   优先预置车用红色
    visual = Visualization(car_path,road_path,cross_path,preAns_path,savePath,\
                            # randomColor = True, \
                            # sizeExpand = 2, \
                            # showRoadInfo = False,\
                            # reduceDraw = 1, \
                            # clipImg = False, \
                            # computeCoordinate = 2
                            )
    visual.drawMap('empty') # 只调用此接口绘制一张空图，图名称为empty。绘制空图时，presetAnswer文件和car.txt文件可以为空。

    # 3-map-training-2 地图下，附带一个json文件
    # visual.drawImgsFromJsonFile(config + 'result_java.json') 
    
    #%%
    # json的示例数据，drawImgsFromJsonFile 接口传递的json文件内容即是这种json格式
    # 此示例数据仅对 2-map-training-1 地图有效。
    # 注意，所有内容均是字符串。
    jsonDict = {
        "1":{  # "1" 是当前调度时刻，如 1,2,3 等。
            "5689":{  # "5689" 是某条道路
                "2":{ # "2" 是 "5689" 这条路的某条车道号
                      # 这里车道号规则，以 双向3车道为例
                      # 正向道路，靠近中间的就是0，外侧是2
                      # 反向道路，靠近中间的是3，外侧是5
                      # 其排列应该是 5 4 3 || 0 1 2 (向上的方向是正向方向)
                    "20556":"0", 
                      # id="20556"的车，离车道起始点的位置（从0开始）
                      # 正向车道起始点就是1764，反向车道起始点是790
                    "37819":"10", # 预置
                    "45938":"12", # 优先
                    "55541":"19", # 优先预置
                },
                "4":{
                    "20556":"0",
                    "37819":"10", # 预置
                    # "45938":"12", # 优先
                    "55541":"19", # 优先预置
                },
            },
            "6097":{
                "1":{
                    "20556":"9",    
                    "37819":"10", # 预置
                    "45938":"12", # 优先
                    "55541":"14", # 优先预置
                },
            },  
        },
        "2":{ 
            "5689":{
                "1":{
                    "20556":"9",
                    "37819":"10", # 预置
                    "45938":"12", # 优先
                    "55541":"14", # 优先预置
                },
                "5":{
                    "20556":"9",
                    "37819":"10", # 预置
                    # "45938":"12", # 优先
                    "55541":"14", # 优先预置
                },
            },
            "6097":{
                "2":{
                    "20556":"9",    
                    "37819":"10", # 预置
                    "45938":"12", # 优先
                    "55541":"14", # 优先预置
                },
            },  
        },

    }
    # visual.drawImgsFromJsonDict(jsonDict)