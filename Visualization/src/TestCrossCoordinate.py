# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 17:21:25 2019

@Author: And-ZJ

@Content:
    
    MapVisualization.py 的测试文件。
    
@Edited:
    
"""

#%%
import numpy as np

from CrossCoordinate import buildCoordinate,genMap

def check(car_path,road_path,cross_path,preAns_path,rightAnswerList):
    # print('rightAnswer:\n',rightAnswer)
    
    from MapVisualization import buildDict    
    CARDICT,ROADDICT,CROSSDICT,CARNAMESPACE,ROADNAMESPACE,CROSSNAMESPACE,_,_ = buildDict(car_path,road_path,cross_path,preAns_path)
    roadDict = ROADDICT
    crossDict = CROSSDICT
    
    
    for i in range(len(CROSSNAMESPACE)):   
        # 从第i点开始建立坐标
        startCrossId = CROSSNAMESPACE[i]
        
        crossId_MapXY = buildCoordinate(roadDict,crossDict,startCrossId=startCrossId)
        res = genMap(crossId_MapXY)
        mapXY_CrossId = res['mapXY_CrossId']
        mapXY_CrossIdNp = res['mapXY_CrossIdNp']
        mapSize = res['mapSize']
        crossId_MapXY = res['crossId_MapXY']
        
        mapXY_CrossIdNp_T = np.transpose(mapXY_CrossIdNp)
        
        RIGHT = False
        for j in range(4):
            roted = np.rot90(mapXY_CrossIdNp,j)
            for rightAnswer in rightAnswerList:
                if roted.shape == rightAnswer.shape:
                    if np.all(roted == rightAnswer):
                        RIGHT = True
                        break
                if roted.T.shape == rightAnswer.shape:
                    if np.all(roted.T == rightAnswer):
                        RIGHT = True
                        break
        if RIGHT:
            print('Index:',i,'CECK OK')
            # print()
            # print('answer:',mapXY_CrossIdNp)

        else:
            print('\nIndex:',i,'CHECK ERROR!')
            # print()
            print('answer:\n',mapXY_CrossIdNp.__repr__())

def test_1():
    config = '../map-strange-1/'
    car_path    = config + 'car.txt'
    road_path   = config + 'road.txt'
    cross_path  = config + 'cross.txt'
    preAns_path = config + 'presetAnswer.txt' 
    
    rightAnswer = np.array([[58, 171, -1, -1],
         [1968, -1, -1, -1],
         [1519, 1897, -1, 1852],
         [1764, 790, 176, 1442]])
    print('\nCHECK test_1')
    check(car_path,road_path,cross_path,preAns_path,[rightAnswer,])
    
    
    

def test_2():     
    config = '../map-strange-2/'
    car_path    = config + 'car.txt'
    road_path   = config + 'road.txt'
    cross_path  = config + 'cross.txt'
    preAns_path = config + 'presetAnswer.txt' 
    
    rightAnswer = np.array([[1, -1, 6], [2, 4, -1], [-1, 5, 7], [3, -1, 8]])
    print('\nCHECK test_2')
    check(car_path,road_path,cross_path,preAns_path,[rightAnswer,])

def test_3():     
    # 这张图的自由度有点多，不止一种画法
    config = '../map-strange-3/'
    car_path    = config + 'car.txt'
    road_path   = config + 'road.txt'
    cross_path  = config + 'cross.txt'
    preAns_path = config + 'presetAnswer.txt' 

    rightAnswerList = [
        np.array([[101,  -1, 102,  -1, 103],
                [109, 110, 104, 105,  -1], 
                [106, 111,  -1, 107, 108]]),
        np.array([[103,  -1,  -1, 108],
                [ -1, 105,  -1, 107],
                [ -1,  -1, 110, 111],
                [102, 104,  -1,  -1],
                [101,  -1, 109, 106]]),
        np.array([[101, -1, 109, 106],
                [102, 104, 110, 111],
                [ -1, 105,  -1, 107],
                [103,  -1,  -1, 108]]),
        np.array([[103,  -1, 102,  -1, 101],
                [ -1, 105, 104,  -1,  -1],
                [ -1,  -1,  -1, 110, 109],
                [108, 107,  -1, 111, 106]]),
    ] 
    print('\nCHECK test_3')
    check(car_path,road_path,cross_path,preAns_path,rightAnswerList)
    
def test_4():     
    # 这张图的自由度有点多，不止一种画法
    config = '../map-strange-4/'
    car_path    = config + 'car.txt'
    road_path   = config + 'road.txt'
    cross_path  = config + 'cross.txt'
    preAns_path = config + 'presetAnswer.txt' 
    
    rightAnswerList = [
        np.array([[101,  -1, 102,  -1, 103],
                [109, 110, 104, 105,  -1],
                [106, 111,  -1, 107, 108]]), 
    ] 
    print('\nCHECK test_3')
    check(car_path,road_path,cross_path,preAns_path,rightAnswerList)
    
def test_5():     
    # 这张图的自由度有点多，不止一种画法
    config = '../map-strange-5/'
    car_path    = config + 'car.txt'
    road_path   = config + 'road.txt'
    cross_path  = config + 'cross.txt'
    preAns_path = config + 'presetAnswer.txt' 
    
    rightAnswerList = [
        np.array([[101, 102,  -1, 103],
                [ -1, 104, 105,  -1],
                [109, 110,  -1,  -1],
                [106, 111, 107, 108]]), 
    ] 
    print('\nCHECK test_3')
    check(car_path,road_path,cross_path,preAns_path,rightAnswerList)

    #%%
    
if __name__ == '__main__':
    test_1()
    test_2()
    test_3()
    test_4()
    test_5()
    
    
    

