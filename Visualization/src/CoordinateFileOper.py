# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 21:07:18 2019

@Author: And-ZJ

@Content:

@Edited:

"""

#%%
def genMap(crossId_MapXY):
    minXY = {'x':len(crossId_MapXY),'y':len(crossId_MapXY)}
    maxXY = {'x':0,'y':0}
    for crossId,mapXY in crossId_MapXY.items():
        minXY['x'] = min(mapXY['x'],minXY['x'])
        minXY['y'] = min(mapXY['y'],minXY['y'])   
        maxXY['x'] = max(mapXY['x'],maxXY['x'])
        maxXY['y'] = max(mapXY['y'],maxXY['y'])
    
    # 计算图大小
    mapSize = {'x':maxXY['x']-minXY['x'] + 1, # 最大坐标值-最小坐标值+1==该轴长度
               'y':maxXY['y']-minXY['y'] + 1}
    
    # x,y -> crossId
    import numpy as np
    mapXY_CrossIdNp = np.ones([mapSize['x'],mapSize['y']],int) * (-1)
    
    # 用于将坐标修正。 左上角变成(0,0)
    offsetXY = {'x':-minXY['x'],'y':-minXY['y']}
    for crossId in crossId_MapXY:
        positiveX = crossId_MapXY[crossId]['x'] + offsetXY['x']
        positiveY = crossId_MapXY[crossId]['y'] + offsetXY['y']
        # print()
        # print(positiveX,positiveY)
        crossId_MapXY[crossId]['x'] = positiveX
        crossId_MapXY[crossId]['y'] = positiveY
        if mapXY_CrossIdNp[positiveX,positiveY] != -1:
            # 如果进入了这里，说明得到了同样坐标的其他点，显然是不对的。
            print('assert False')
            print(crossId,positiveX,positiveY,mapXY_CrossIdNp[positiveX,positiveY],)
        mapXY_CrossIdNp[positiveX,positiveY] = crossId
    # 组合结果，返回数据
    mapXY_CrossId = mapXY_CrossIdNp.tolist()
    res = {
       'mapXY_CrossId':mapXY_CrossId,
       'crossId_MapXY':crossId_MapXY,
       'mapSize': mapSize,
       'mapXY_CrossIdNp':mapXY_CrossIdNp
       }
    return res

def readCoordinate(filePath='coordinate.txt'):
    crossId_MapXY = {}
    textLines = list()
    with open(filePath,'r',encoding='UTF-8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.rstrip()
            if line != '' and line[0] != '#':
                textLines.append(line)
    print(textLines)
    for i in range(len(textLines)):
        line = textLines[i]
        crossIdList = line.replace(' ', '').split(',')
        for j in range(len(crossIdList)):
            crossId = int(crossIdList[j])
            if crossId == -1:
                continue
            crossId_MapXY[crossId] = {'x':i,'y':j}
    return crossId_MapXY

def writeCoordinate(filePath='coordinate1.txt',mapXY_CrossId=None):
    with open(filePath,'w',encoding='UTF-8') as f:
        for i in range(len(mapXY_CrossId)):
            strList = ['{0:>6}'.format(crossId) for crossId in mapXY_CrossId[i]]
            s = ','.join(strList)
            print(strList,s)
            f.write(s)
            f.write('\n')

if __name__ == '__main__':
    crossId_MapXY = readCoordinate('coordinate.txt')
    coordinateDict = genMap(crossId_MapXY)
    mapXY_CrossId = coordinateDict['mapXY_CrossId']
    writeCoordinate('coordinate1.txt',mapXY_CrossId)

