# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 17:43:58 2019

@Author: And-ZJ

@Content:

@Edited:

"""


import numpy as np
from collections import defaultdict,deque

DEBUG_LEVEL = 0
if __name__ == '__main__':
    DEBUG_LEVEL = 1

# 重建上下左右关系时，由上一个确定方位的，来确定当前道路方位
def deduceOffset(direction):
    if direction == 1:
        offset = 1
    elif direction == 2:
        offset = 0
    elif direction == 3:
        offset = 3
    elif direction == 0:
        offset = 2
    else:
        assert False
    return offset

"""
DFS遍历 修正节点坐标上下左右道路位置关系
"""
def DFS_Direction(currCrossId,passRoadId,direction,roadDict,crossDict,directionDict,nebDict,visitedDict):
    if visitedDict[currCrossId] is True:
        return
    visitedDict[currCrossId] = True
    currCross = crossDict[currCrossId] 
    currRoadIdList = list(currCross.roadIds) # 属性，四条道路的列表 
    if passRoadId == -1:
        # 说明是第一个节点
        sortedRoadIdList = currRoadIdList
    else:
        # 修正当前路口四条道路上下左右的顺序
        tripleCurrRoadList = currRoadIdList + currRoadIdList + currRoadIdList
        index = currRoadIdList.index(passRoadId)
        offset = deduceOffset(direction)
        sortedRoadIdList = tripleCurrRoadList[index+offset:index+offset+4]
    directionDict[currCrossId] = sortedRoadIdList
    nebCrossIdList = []
    nebDict[currCrossId] = nebCrossIdList
    
    for i in range(4):
        passRoadId = sortedRoadIdList[i]
        if passRoadId == -1:
            nebCrossIdList.append(-1)
            continue
        else:
            passRoad = roadDict[passRoadId]
            nextCrossId = passRoad.from_ if passRoad.from_ != currCrossId else passRoad.to_ # 属性，起始终点路口 id
            nebCrossIdList.append(nextCrossId)
            DFS_Direction(nextCrossId,passRoadId,i,roadDict,crossDict,directionDict,nebDict,visitedDict)

"""
修正节点坐标上下左右道路位置关系
directionDict [crossId]->[northRoadId,eastRoadId,southRoadId,westRoadId]
nebDict     [crossId]->[northCrossId,eastCrossId,...]
如果id不存在则为-1
"""
def buildDirection(roadDict,crossDict,startCrossId=None):
    if startCrossId is None:
        # 设置起始搜索结点
        startCrossId = list(crossDict.keys())[0]
    
    # 是否已遍历    
    visitedDict = defaultdict(lambda :False)
    directionDict = {} 
    nebDict = {}
    # DFS 遍历
    DFS_Direction(startCrossId,-1,0,roadDict,crossDict,directionDict,nebDict,visitedDict)
    return directionDict,nebDict

"""
方法：检查自己是否和已有实点和虚拟点冲突
    判定已有点，判定虚拟点
    冲突判定：点坐标相等即为冲突。
    可优化。
"""
def isConflict(deduceX,deduceY,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY):
    for crossId,mapXY in crossId_MapXY.items():
        if mapXY['x'] == deduceX and mapXY['y'] == deduceY:
            if DEBUG_LEVEL >= 1:
                print('isConflict: conflict with actual {0} at coor ({1},{2})'.format(crossId,deduceX,deduceY))
            return True
    for roadId,virtualList in virtualDict.items():
        for virtualPoint in virtualList:
            if virtualPoint['x'] == deduceX and virtualPoint['y'] == deduceY:
                if DEBUG_LEVEL >= 1:
                    print('isConflict: conflict with virtual {0} at coor ({1},{2}) on raod {3}'.format(virtualPoint,deduceX,deduceY,roadId))
                return True
    return False

"""
方法，检查自己推断坐标是否和邻居坐标冲突
    东西方向，只要求y坐标一致，南北方向，只要求x坐标一致，就不算冲突。
    这里只考虑了一个方向，事实上，若东西方向上，y坐标一致，但若邻居在左边，却可能存在推断点y坐标小于邻居y坐标的情况
"""
def isNebConflict(deduceX,deduceY,i,nebCrossId,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY):
    nebMapXY = crossId_MapXY[nebCrossId]
    if i == 0 or i == 2: # 南北方向
        step = nebMapXY['x']-deduceX
    elif i == 1 or i == 3:
        step = nebMapXY['y']-deduceY
    if DEBUG_LEVEL >= 1:
        if step == 0:
            print('isNebConflict: deduce:({0},{1}), direction:{2}, no conflict with neb cross {3}, neb ({4},{5})'.format(deduceX,deduceY,\
                i, nebCrossId, nebMapXY['x'],nebMapXY['y']))
        else:
            print('isNebConflict: deduce:({0},{1}), direction:{2}, Conflict with neb cross {3}, neb ({4},{5}), step {6}!'.format(deduceX,deduceY,\
                i, nebCrossId, nebMapXY['x'],nebMapXY['y'],step))
    return step

"""
BFS 推理当前点坐标，解决当前点坐标冲突，该函数返回时，则确定了该点坐标。
"""        
def BFS_Coordinate(currCrossId,B,W,R,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY):
    if visitedDict[currCrossId]:
        return
    if DEBUG_LEVEL >= 1:
        print('BFS_Coordinate: currCrossId:',currCrossId)

    nebCrossIdList = nebDict[currCrossId] 
    
    record = []
    
    for i,nebCrossId in enumerate(nebCrossIdList):
        if nebCrossId != -1 and nebCrossId in B:
            record.append((i,nebCrossId))            
    
    if DEBUG_LEVEL >= 1:
        print('BFS_Coordinate: record:{0}'.format(record))
    
    if len(record) == 0:
        # 第一个点
        deduceX = 0
        deduceY = 0
        if DEBUG_LEVEL >= 1:
            print('\nBFS_Coordinate: FirstCrossId:{0}, deduce:({1},{2})'.format(currCrossId,deduceX,deduceY))
    else:
        # 使用第一个邻居进行坐标推断
        i1 = record[0][0]
        nebCrossId1 = record[0][1]
        nebMapXY = crossId_MapXY[nebCrossId1]
        deduceX,deduceY = deduceCoordiante(i1,nebMapXY['x'],nebMapXY['y'])
        if DEBUG_LEVEL >= 1:
                print('\nBFS_Coordinate: deduce:({0},{1}), direction:{2}, neb:{3} at ({4},{5})  '.format(deduceX,deduceY,\
                      i1,nebCrossId1,nebMapXY['x'],nebMapXY['y']))  
        # 判断推断出的点有没有在地图上冲突，若冲突，解决冲突，重新推断
        if isConflict(deduceX,deduceY,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY):
            coordinateFix(deduceX,deduceY,1,i1,nebCrossId1,B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
            nebMapXY = crossId_MapXY[nebCrossId1]
            deduceX,deduceY = deduceCoordiante(i1,nebMapXY['x'],nebMapXY['y'])
            if DEBUG_LEVEL >= 1:
                print('\nBFS_Coordinate: newDeduce:({0},{1})'.format(deduceX,deduceY))  
            flushVirtualCross(B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
        # 检查所有邻居，判断推理坐标是否和它们冲突，并且解决冲突
        for nebRecord in record:
            nebCrossId = nebRecord[1]
            nebMapXY = crossId_MapXY[nebCrossId]
            if True:
                # 解决方位冲突，例如在左边的点的x坐标却比自己x大
                direction = nebRecord[0]
                if direction == 0:
                    if nebMapXY['y'] >= deduceY:
                        stepTurn = abs(nebMapXY['y'] - deduceY) + 1
                        if DEBUG_LEVEL >= 1:
                            print('\ndeduce:({0},{1}), direction:{2}, neb:{3} at ({4},{5}), Y fiexed stepTurn:{6}'.format(deduceX,deduceY,\
                                  direction,nebCrossId,nebMapXY['x'],nebMapXY['y'],stepTurn))
                        coordinateFix(deduceX,deduceY,stepTurn,direction,nebRecord[1],B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
                        flushVirtualCross(B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
                
                elif direction == 1:
                    # dire = 0 if step > 0 else 2
                    if nebMapXY['x'] <= deduceX:
                        stepTurn = abs(nebMapXY['x'] - deduceX) + 1
                        if DEBUG_LEVEL >= 1:
                            print('\ndeduce:({0},{1}), direction:{2}, neb:{3} at ({4},{5}), X fiexed stepTurn:{6}'.format(deduceX,deduceY,\
                                  direction,nebCrossId,nebMapXY['x'],nebMapXY['y'],stepTurn))
                        coordinateFix(deduceX,deduceY,stepTurn,direction,nebRecord[1],B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
                        flushVirtualCross(B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
                
                elif direction == 2:
                    # dire = 3 if step > 0 else 1
                    if nebMapXY['y'] <= deduceY:
                        stepTurn = abs(nebMapXY['y'] - deduceY) + 1
                        if DEBUG_LEVEL >= 1:
                            print('\ndeduce:({0},{1}), direction:{2}, neb:{3} at ({4},{5}), Y fiexed stepTurn:{6}'.format(deduceX,deduceY,\
                                  direction,nebCrossId,nebMapXY['x'],nebMapXY['y'],stepTurn))
                        coordinateFix(deduceX,deduceY,stepTurn,direction,nebRecord[1],B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
                        flushVirtualCross(B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
                
                elif direction == 3:
                    # dire = 0 if step > 0 else 2
                    if nebMapXY['x'] >= deduceX:
                        stepTurn = abs(nebMapXY['x'] - deduceX) + 1
                        if DEBUG_LEVEL >= 1:
                            print('\ndeduce:({0},{1}), direction:{2}, neb:{3} at ({4},{5}), X fiexed stepTurn:{6}'.format(deduceX,deduceY,\
                                  direction,nebCrossId,nebMapXY['x'],nebMapXY['y'],stepTurn))
                        coordinateFix(deduceX,deduceY,stepTurn,direction,nebRecord[1],B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
                        flushVirtualCross(B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
            # 方位冲突解决后，下一步才好解决坐标没对齐的问题。    
            step = isNebConflict(deduceX,deduceY,nebRecord[0],nebRecord[1],roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
            if step != 0:
                # 坐标没对齐
                if DEBUG_LEVEL >= 1:
                    print('\ndeduce:({0},{1}), direction:{2}, neb:{3} at ({4},{5}), step:{6}'.format(deduceX,deduceY,\
                      direction,nebCrossId,nebMapXY['x'],nebMapXY['y'],step))
                if direction == 0:
                    dire = 3 if step > 0 else 1
                elif direction == 1:
                    dire = 0 if step > 0 else 2
                elif direction == 2:
                    dire = 3 if step > 0 else 1
                elif direction == 3:
                    dire = 0 if step > 0 else 2   
                step = abs(step)
                # 尝试强行对齐，将所有需移动的点向dire方向移动，即可对齐
                rst,fixcp = coordinateFix(deduceX,deduceY,step,dire,nebRecord[1],B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
                while rst == False:
                    # 出现False原因，上一步只解决了邻居点方位冲突，在对齐过程中，有可能其他要移动的点会产生方位冲突
                    # 因此，这里解决产生方位冲突的点
                    if not fixcp['isVirtual']:
                        fixCrossId = fixcp['crossId']
                        coordinateFix(deduceX,deduceY,1,direction,fixCrossId,B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)     
                    else:
                        fixCrossId1 = fixcp['crossId1']
                        fixCrossId2 = fixcp['crossId2']
                        fixNebCrossIdList = nebDict[fixCrossId1]
                        if fixCrossId2 == fixNebCrossIdList[direction]:
                            coordinateFix(deduceX,deduceY,1,direction,fixCrossId1,B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)     
                        else:
                            coordinateFix(deduceX,deduceY,1,direction,fixCrossId2,B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)     
                    rst,fixcp = coordinateFix(deduceX,deduceY,step,dire,nebRecord[1],B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
                    if DEBUG_LEVEL >= 1:
                        print('coordinateFix',rst)
                flushVirtualCross(B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
    
    if DEBUG_LEVEL >= 1:
        print('\nBFS_Coordinate: {0} add neb'.format(currCrossId))
    # 添加邻居
    for i,nebCrossId in enumerate(nebCrossIdList):
        if DEBUG_LEVEL >= 1:
            if nebCrossId != -1:
                if nebCrossId in W or nebCrossId in B:
                    print('neb {0} have been added.'.format(nebCrossId))
                elif nebCrossId in R:
                    print('neb add {0} .'.format(nebCrossId))
                else:
                    assert False
        if nebCrossId != -1 and nebCrossId in R:
            W.append(nebCrossId)
            R.remove(nebCrossId)   
    
    # 标记自己        
    crossId_MapXY[currCrossId] = {'x':deduceX,'y':deduceY}
    visitedDict[currCrossId] = True
    
""" 
方法：根据已有坐标的邻居点推断自己坐标
    确定自己在某个邻居的哪个方位，然后通过邻居的坐标，即可算出自己的坐标。
    例如，如果，自己在邻居的上边，则自己坐标横轴与邻居一样，纵轴比邻居纵轴少1
"""
def deduceCoordiante(i,nebX,nebY,step=1):
    # step 是推断步长
    if i == 1:
        deduceX = nebX - step
        deduceY = nebY
    elif i == 2: 
        deduceX = nebX
        deduceY = nebY - step
    elif i == 3:
        deduceX = nebX + step
        deduceY = nebY
    elif i == 0:
        deduceX = nebX
        deduceY = nebY + step
    else:
        assert False
    return deduceX,deduceY


"""
方法：建立虚拟点坐标
    虚拟点，边上跨过了本应有节点的位置，简单理解，边长大于1，给对应整数坐标位置加上虚拟点，用于冲突判定。
    遍历所有已有坐标的点。
        对其四条边进行遍历。如果边被遍历过了，跳过。
        如果边对面的点有坐标了，计算这条边上的虚拟点。
        否则，不计算
virtualDict [roadId]-> [virtualCrossId_1,...]
"""
def flushVirtualCross(B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY):
    roadVisitedDict = defaultdict(lambda : False)
    # nebVirtualDict = defaultdict(lambda : list())
    # virtualList = []
    virtualDict.clear()
    # mapXY_virtual = defaultdict(lambda : dict())
    for crossId in B:
        roadIdList = directionDict[crossId]
        nebCrossIdList = nebDict[crossId]
        for i,roadId in enumerate(roadIdList):
            if roadId == -1 or roadVisitedDict[roadId]:
                continue
            roadVisitedDict[roadId] = True
            nebCrossId = nebCrossIdList[i]
            if not visitedDict[nebCrossId]:
                continue
            virtualList = calVirtualCrossList(roadId,crossId,i,nebCrossId,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
            virtualDict[roadId] = virtualList
    if DEBUG_LEVEL >= 1:
        print('\nflushVirtualCross:',virtualDict)

"""
计算某条边上虚拟点列表，如果边长==1，则空列表
虚拟点也有crossId，不过是字符串
"""    
def calVirtualCrossList(roadId,crossId1,direction,crossId2,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY):
    # cross1 = crossDict[crossId1]
    # cross2 = crossDict[crossId2]
    mapXY1 = crossId_MapXY[crossId1]
    mapXY2 = crossId_MapXY[crossId2]
    virtualList = []
    
    if direction == 0 or direction == 2: # 南北
        x = mapXY1['x']
        minY = min(mapXY1['y'],mapXY2['y'])
        maxY = max(mapXY1['y'],mapXY2['y'])
        for i in range(minY+1,maxY):
            virtualCrossId = 'v' + str(roadId) + str(i)
            virtualList.append({'x':x,'y':i,'crossId':virtualCrossId,'crossId1':crossId1,'crossId2':crossId2,'roadId':roadId})
    else:
        y = mapXY1['y']
        minX = min(mapXY1['x'],mapXY2['x'])
        maxX = max(mapXY1['x'],mapXY2['x'])
        for i in range(minX+1,maxX):
            virtualCrossId = 'v' + str(roadId) + str(i)
            virtualList.append({'x':i,'y':y,'crossId':virtualCrossId,'crossId1':crossId1,'crossId2':crossId2,'roadId':roadId})
    return virtualList


# 将实体点和虚拟点，提供统一的操作接口，
# 推断坐标时，就可以将实体点和虚拟点统一使用
class Point:
    def __init__(self):
        self.actualPoints = {}
        self.virtualPoints = {}
    def addPoint(self,key,x,y,crossId1=-1,crossId2=-1,roadId=-1):
        if isinstance(key,int):
            self.actualPoints[key] = {'isVirtual':False,'x':x,'y':y,'crossId':key}
        elif isinstance(key,str):
            self.virtualPoints[key] = {'isVirtual':True,'x':x,'y':y,'crossId':key,'crossId1':crossId1,'crossId2':crossId2,'roadId':roadId}
        else:
            assert False
        return self.getPoint(key)
    
    def isVirtualPoint(self,key):
        if isinstance(key,int):
            return False
        return True
    def getPoint(self,key,):
        if isinstance(key,int):
            return self.actualPoints.get(key,None)
        return self.virtualPoints.get(key,None)

"""        
方法：坐标修正方法
    例，向x轴负方向进行修正。
    首先找到所有需要修正的点。待搜索列表 S，需修正列表 F。将起始点放入到S中。
        从S取一个元素e.
        若e是实体点，将其上邻居和下邻居（已有坐标的邻居）加入到S中（要求不能已近存在于S或F），
            以及上下路线上的所有虚拟点都加入S。检查实体点前方是否存在实体点或虚拟点，若存在，若不在S或F中，则加入S。
        若e是虚拟点，将虚拟点的左右所在的路口两点都加入S，检查虚拟点前方是否存在实体点或虚拟点，若存在，若不在S或F中，则点加入S。
        将e放到F中，直到S为空。
    将F中的所有点x坐标减掉相应的值即可。
可优化
"""      
def coordinateFix(deduceX,deduceY,step,direction,startCrossId,B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY):
    F = []
    S = deque()
    S.append(startCrossId)
    
    if DEBUG_LEVEL >= 1:
        print('\ncoordinateFix: startCrossId:{0}, direction:{1}, step:{2}'.format(startCrossId,direction,step))
    points = Point() # 

    inS = defaultdict(lambda : False)
    inF = defaultdict(lambda : False)

    for roadId,virtualList in virtualDict.items():
        for virtualPoint in virtualList:
            points.addPoint(virtualPoint['crossId'],virtualPoint['x'],virtualPoint['y'],\
                            virtualPoint['crossId1'],virtualPoint['crossId2'],virtualPoint['roadId'])
    
    for crossId,mapXY in crossId_MapXY.items():
        points.addPoint(crossId,mapXY['x'],mapXY['y'])
    
    virtualMarked = []
    while len(S) != 0:
        # crossId 可能是实体，也可能是虚拟点
        crossId = S.popleft()
        cp = points.getPoint(crossId)
        rst,fixcp = searchCross(deduceX,deduceY,step,cp,direction,points,S,F,inS,inF,B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
        if rst == False:
            return False,fixcp
        inF[crossId] = True
        inS[crossId] = False
        F.append(crossId)
        if cp['isVirtual']:
            virtualMarked.append(crossId)
    # 去掉存储在F中的虚拟点
    for crossId in virtualMarked:
        F.remove(crossId)
    if DEBUG_LEVEL >= 1:
        print('\ncoordinateFix: all fixed point:{0}'.format(F))

    # 找到了所有需要修正坐标的点，统一修正。
    for crossId in F:
        mapXY = crossId_MapXY[crossId]
        if DEBUG_LEVEL >= 2:
            print(crossId,'BeforeFix:',mapXY)
        if direction == 0:
            mapXY['y'] -= step
        elif direction == 1:
            mapXY['x'] += step
        elif direction == 2:
            mapXY['y'] += step
        elif direction == 3:
            mapXY['x'] -= step
        if DEBUG_LEVEL >= 2:
            print(crossId,'afterFix:',crossId_MapXY[crossId])    
    return True,None
"""
所有需要修正坐标的点的搜索方法
从S取一个元素e，若是实体点，将其上邻居和下邻居加入到S中（要求不能已近存在于S或F），
        以及上下路线上的虚拟点都加入S。检查实体点前方是否存在实体点或虚拟点。若存在，则点加入S。 
    若e是虚拟点，将虚拟点的左右所在的路口两点都加入S，检查虚拟点前方是否存在实体点或虚拟点，若存在，则点加入S。
    将e放到F中，直到S为空。
"""
def searchCross(deduceX,deduceY,step,cp,direction,points,S,F,inS,inF,B,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY):
    if DEBUG_LEVEL >= 1:
        print('searchCross: direction:{0}, currPoint:{1}'.format(direction,cp)) 
    
    if not cp['isVirtual']:
        lDirection = (direction + 1) % 4
        rDirection = (direction + 3) % 4
        crossId = cp['crossId']
        roadIdList = directionDict[crossId]
        nebCrossIdList = nebDict[crossId]
        
        lNebCrossId = nebCrossIdList[lDirection]
        if lNebCrossId != -1 and not inF[lNebCrossId] and not inS[lNebCrossId] and lNebCrossId in B:
            # lNebMapXY = crossId_MapXY[lNebCrossId]
            S.append(lNebCrossId)
            if DEBUG_LEVEL >= 1:
                print('searchCross: add lNebCrossId:{0}'.format(lNebCrossId)) 
            inS[lNebCrossId] = True
            lRoadId = roadIdList[lDirection]
            virtualCrossList = virtualDict.get(lRoadId,None)
            if virtualCrossList is not None:
                for virtualPoint in virtualCrossList:
                    virtualCrossId = virtualPoint['crossId']
                    S.append(virtualCrossId)
                    if DEBUG_LEVEL >= 1:
                        print('searchCross: roadId {0} add virtualCrossId:{1}'.format(lRoadId,virtualCrossId)) 
            
        rNebCrossId = nebCrossIdList[rDirection]
        if rNebCrossId != -1 and not inF[rNebCrossId] and not inS[rNebCrossId] and rNebCrossId in B:
            S.append(rNebCrossId)
            if DEBUG_LEVEL >= 1:
                print('searchCross: add rNebCrossId:{0}'.format(rNebCrossId)) 
            inS[rNebCrossId] = True
            rRoadId = roadIdList[rDirection]
            virtualCrossList = virtualDict.get(rRoadId,None)
            if virtualCrossList is not None:
                for virtualPoint in virtualCrossList:
                    virtualCrossId = virtualPoint['crossId']
                    S.append(virtualCrossId)
                    if DEBUG_LEVEL >= 1:
                        print('searchCross: roadId {0} add virtualCrossId:{1}'.format(rRoadId,virtualCrossId)) 
    else: # 虚拟点
        crossId1 = cp['crossId1']
        crossId2 = cp['crossId2']
        if crossId1 != -1 and not inF[crossId1] and not inS[crossId1]:
            S.append(crossId1)
            inS[crossId1] = True
            if DEBUG_LEVEL >= 1:
                print('searchCross: add crossId1:{0}'.format(crossId1)) 
            # print('add crossId1:',crossId1)
        if crossId2 != -1 and not inF[crossId2] and not inS[crossId2]:
            S.append(crossId2)
            inS[crossId2] = True
            # print('add crossId2:',crossId2)
            if DEBUG_LEVEL >= 1:
                print('searchCross: add crossId2:{0}'.format(crossId2)) 
    
    # 搜索前行方向上
    straight = []     
    for dis in range(1,step+1):
        sX,sY = deduceCoordiante((direction+2)%4,cp['x'],cp['y'],dis)
    
        if DEBUG_LEVEL >= 1:
            print('searchCross: org:({0},{1}), dis:{2}, straight:({3},{4})'.format(cp['x'],cp['y'],dis,sX,sY,)) 
        
        if sX == deduceX and sY == deduceY:
            if dis == step:
                if DEBUG_LEVEL >= 1:
                    print('orientation conflict when fix align.')
                return False,cp
            straight.clear() 
            continue
        for crossId,mapXY in crossId_MapXY.items():
            if mapXY['x'] == sX and mapXY['y'] == sY:
                if not inS[crossId] and not inF[crossId]:
                    inS[crossId] = True
                    straight.append(crossId)
                break
        findFlag = False
        for roadId,virtualPointList in virtualDict.items():
            for virtualPoint in virtualPointList:
                if virtualPoint['x'] == sX and virtualPoint['y'] == sY:
                    findFlag = True
                    virtualCrossId = virtualPoint['crossId']
                    if not inS[virtualCrossId] and not inF[virtualCrossId]:
                        inS[virtualCrossId] = True
                        straight.append(virtualCrossId)
                    break
            if findFlag:
                break
    if DEBUG_LEVEL >= 1:
        print('searchCross: straight crossId:{0}'.format(straight))
    
    S.extend(straight)  
    return True,None

def genMap(crossId_MapXY):
    # 将得到的点坐标映射进行坐标建立，修正左上角为0,0
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
            print('Same Coor more then one point. assert False')
            print(crossId,positiveX,positiveY,mapXY_CrossIdNp[positiveX,positiveY],)
        mapXY_CrossIdNp[positiveX,positiveY] = crossId
    
    # 上一步生成的地图可能有些地方可以缩短边长
    mapXY_CrossIdNp = removeRedundancyMap(mapXY_CrossIdNp)
    
    mapSize = {'x':mapXY_CrossIdNp.shape[0],
               'y':mapXY_CrossIdNp.shape[1]}
    crossId_MapXY = {}
    for i in range(mapSize['x']):
        for j in range(mapSize['y']):
            crossId = mapXY_CrossIdNp[i,j]
            if crossId != -1:
                crossId_MapXY[crossId] = {'x':i,'y':j} 

    # 组合结果，返回数据
    mapXY_CrossId = mapXY_CrossIdNp.tolist()
    coordinateDict = {
       'mapXY_CrossId':mapXY_CrossId,
       'crossId_MapXY':crossId_MapXY,
       'mapSize': mapSize,
       'mapXY_CrossIdNp':mapXY_CrossIdNp
       }
    return coordinateDict

def removeRedundancyMap(mapXY_CrossIdNp):
    mark = []
    for i in range(mapXY_CrossIdNp.shape[0]):
        if np.all(mapXY_CrossIdNp[i,:] == -1):
            mark.append(i)
    newMapNp = np.delete(mapXY_CrossIdNp,mark,axis=0)
    mark = []
    for i in range(mapXY_CrossIdNp.shape[1]):
        if np.all(mapXY_CrossIdNp[:,i] == -1):
            mark.append(i)
    newMapNp = np.delete(newMapNp,mark,axis=1)
    return newMapNp

# 接口
def computeMapXY(roadDict,crossDict,directionDict,nebDict,startCrossId=None):
    # global directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY
    if startCrossId is None:
        startCrossId = list(crossDict.keys())[0]
     # 是否已遍历    
    visitedDict = defaultdict(lambda :False)
    virtualDict = {} # 以边为key

    crossId_MapXY = dict()
    B = list()
    W = deque()
    R = list(crossDict.keys())
    
    R.remove(startCrossId)
    W.append(startCrossId)
    count = 0
    while len(W) != 0:
        currCrossId = W.popleft()
        count += 1
        if DEBUG_LEVEL >= 1:
            print('\n###################################################################################')
            print('buildCoordinate: count:{0}, currentCrossId:{1}'.format(count,currCrossId))
        BFS_Coordinate(currCrossId,B,W,R,roadDict,crossDict,directionDict,nebDict,visitedDict,virtualDict,crossId_MapXY)
        B.append(currCrossId)

    return crossId_MapXY

"""
BFS搜索建立稀疏坐标。要求不能出现三角形路况。

已建立坐标集合:B
待选列表集合  :W
剩余集合     :R
初始：B 0个，W：0个，R：所有点。
从待选列表W里选一个点。
    检查上下左右4个点，是否存在已在集合B中的点。
        没有，推断是第一个点，赋予坐标0,0。
        有，则根据已有坐标的第一个邻居点（或任意一个）推断自己坐标。
            如果推断坐标和已有点坐标冲突，向着该邻居方向移动一步，可以去掉坐标冲突，然后重新由该邻居推断自己坐标。
            再检查是否和已有坐标的邻居冲突（即坐标对不上），若冲突，进行坐标强制修正。
            记录自己的坐标，标记已访问。
    将该点上下左右4个点中还在R中的点，加入到集合W中来。
    将该点加入到B中去。
"""

def buildCoordinate(roadDict,crossDict,startCrossId=None):
    if startCrossId is None:
        startCrossId = list(crossDict.keys())[0]

    directionDict,nebDict = buildDirection(roadDict,crossDict,startCrossId)
    crossId_MapXY = computeMapXY(roadDict,crossDict,directionDict,nebDict,startCrossId)
    return crossId_MapXY

#%%
if __name__ == '__main__':
    
    config = '../map-strange-5/'
    # config = '../map-2/'
    car_path    = config + 'car.txt'
    road_path   = config + 'road.txt'
    cross_path  = config + 'cross.txt'
    preAns_path = config + 'presetAnswer.txt' 
    
    from MapVisualization import buildDict    
    CARDICT,ROADDICT,CROSSDICT,CARNAMESPACE,ROADNAMESPACE,CROSSNAMESPACE,_,_ = buildDict(car_path,road_path,cross_path,preAns_path)
    startCrossId = CROSSNAMESPACE[0]
    roadDict = ROADDICT
    crossDict = CROSSDICT
    #%%
    
    crossId_MapXY = buildCoordinate(roadDict,crossDict,startCrossId=startCrossId)
    
    coordinateDict = genMap(crossId_MapXY)
    
    mapXY_CrossId = coordinateDict['mapXY_CrossId']
    mapXY_CrossIdNp = coordinateDict['mapXY_CrossIdNp']
    mapSize = coordinateDict['mapSize']
    crossId_MapXY = coordinateDict['crossId_MapXY']

    if np.sum(mapXY_CrossIdNp != -1) != len(crossDict):
        print('Error: cross nums not equal.')

    import numpy as np
    mapXY_CrossIdNp_T = np.transpose(mapXY_CrossIdNp)

