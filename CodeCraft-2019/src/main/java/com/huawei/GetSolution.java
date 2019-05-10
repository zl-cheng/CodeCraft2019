package com.huawei;

import com.huawei.CONSTANT.TrafficData;
import com.huawei.domain.Car;
import com.huawei.domain.Cross;
import com.huawei.domain.Road;
import com.huawei.traffic.TrafficCar;
import com.huawei.traffic.TrafficCross;
import com.huawei.traffic.TrafficRoad;

import java.io.FileWriter;
import java.io.IOException;
import java.util.*;
import java.util.stream.Collectors;

/**
 * @author 程智凌
 * @date 2019/3/17 22:00
 */
public class GetSolution {

    //程序主体
    public static Map<Integer, TrafficCar> getSolution(String ansPath) throws Exception {
        Map<String ,String> map = new HashMap<>();

        //生成树，作为解锁时的参考，防止震荡
        generateTree(new LinkedList<>());

        //建立坐标系
        TrafficCross.createCrossCoordinate();

        //记录每个路口的静态距离
        for(TrafficCross cross : TrafficData.trafficCrossMap.values()){
            cross.saveDistance();
            cross.saveDistanceWithSpeed();
        }

        Set<Integer> waitStartList = new HashSet<>();
        List<Integer> priorityCarList = new LinkedList<>();
        for(Car car : TrafficData.carMap.values())
            if(!car.isPreset)
                if(car.isPrioriry)
                    priorityCarList.add(car.id);
                else
                    waitStartList.add(car.id);
        //路口登记优先车辆发车列表和普通车辆发车列表
        for(Car car : TrafficData.carMap.values()){
            if(!car.isPreset){
                if(car.isPrioriry)
                    TrafficData.trafficCrossMap.get(car.from).priorityCarWaitStartList.add(car.id);
                else
                    TrafficData.trafficCrossMap.get(car.from).waitStartCar.add(car.id);
            }
        }
        for(TrafficCross cross : TrafficData.trafficCrossMap.values()){
            Collections.sort(cross.waitStartCar, crossWaitStartCarComparator);
            Collections.sort(cross.priorityCarWaitStartList, crossWaitStartCarComparator);
        }

        //判断优先预置车辆的是否存在绕路
        List<Integer> presetPriorityCarList = new LinkedList<>();
        for(TrafficCar car : TrafficData.presetCarMap.values()){
            if(car.info.isPrioriry && car.info.isPreset)
                presetPriorityCarList.add(car.info.id);
        }
        Collections.sort(presetPriorityCarList, (c1, c2) -> {
            return TrafficData.presetCarMap.get(c2).starTime - TrafficData.presetCarMap.get(c2).starTime;
        });
        for(Integer carId : presetPriorityCarList){
            TrafficCar car = TrafficData.presetCarMap.get(carId);
            if(TrafficData.changedPresetCarNum < TrafficData.presetCarMap.size() * TrafficData.BLOCKING_CHANGE_PRESET_CAR_RATE && SearchSolution.getSolutionDistance(car.solution)
                    > (int)((double)TrafficData.trafficCrossMap.get(car.info.from).distanceMap.get(car.info.to) * 1.3)){
                SearchSolution.searchSolution(car);
                TrafficData.carMap.get(car.info.id).isPreset = false;
                TrafficData.presetCarMap.get(car.info.id).info.isPreset = false;
//                TrafficData.presetCarMap.remove(car.info.id);
                TrafficData.changedPresetCarNum ++;
            }
        }

        Map<Integer, TrafficCar> resMap = new HashMap<>(TrafficData.carMap.size());
        Set<Integer> drivingSet = new HashSet<>();

        //因为发车时间和路线都是固定的，就先登记那些预置但是不是优先级的车
        TrafficData.presetCarList = new LinkedList<>(TrafficData.presetCarMap.keySet());
        Collections.sort(TrafficData.presetCarList, (i1, i2) -> {
            return TrafficData.presetCarMap.get(i1).starTime - TrafficData.presetCarMap.get(i2).starTime;
        });

        //登记每时间要发车的预置车辆
        for(TrafficCar car : TrafficData.presetCarMap.values()){
            if(TrafficData.presetCarTimeMap.containsKey(car.starTime))
                TrafficData.presetCarTimeMap.get(car.starTime).add(car.info.id);
            else{
                List<Integer> list = new LinkedList<>();
                list.add(car.info.id);
                TrafficData.presetCarTimeMap.put(car.starTime, list);
            }
        }

        Collections.sort(priorityCarList, crossWaitStartCarComparator);

        int startTime = 0;
        while(!TrafficData.trafficCarMap.isEmpty() || !waitStartList.isEmpty()){
            //运行时间超时
            if(System.currentTimeMillis() - TrafficData.systemStartTime > TrafficData.MAX_RUNNING_TIME)
                return null;

            //更新道路动态信息 （车辆、预计到达车辆）
            for(TrafficRoad road : TrafficData.trafficRoadMap.values())
                road.updateInfo();
            //
            for(TrafficRoad road : TrafficData.trafficRoadMap.values()){
                if(road.waitRoad == null)
                    continue;
                if(road.isLock && (double)road.carNum - road.lastTimeLeaveCarNum > TrafficData.BLOCK_PARAM * (double)road.info.length * (double)road.info.channel)
                    road.waitRoad.isWaited = true;
                if(road.waitRoad.isLock && (double)road.waitRoad.carNum > TrafficData.BLOCK_PARAM * (double)road.waitRoad.info.length * (double)road.waitRoad.info.channel)
                    road.isWaiting = true;
            }
            //预置车辆未来路径的道路增加权重
            //优先车辆规划路线并未来路径的道路权重
            for(Integer carId : TrafficData.drivingSet){
                TrafficCar car = TrafficData.trafficCarMap.get(carId);
                if(car.info.isPrioriry && !car.info.isPreset){
                    if(SearchSolution.needChangeSolution(car))
                        SearchSolution.searchSolution(car);
                    if(car.solution.size() > 1)
                        TrafficData.trafficRoadMap.get(car.solution.get(0) + "_" + car.solution.get(1)).willArrivedPrirotyCarNum ++;
                }
            }
            //提前将预置车辆路径占用
            for(int i = startTime + 1; i < startTime + TrafficData.PREDICT_PRESET_NUM_TIME; i++){
                if(TrafficData.presetCarTimeMap.containsKey(i)){
                    List<Integer> list = TrafficData.presetCarTimeMap.get(i);
                    for(Integer carId : list){
                        SearchSolution.registRoadWillArrivedCarNum(TrafficData.presetCarMap.get(carId), i);
                        addPresetSolutionCost(TrafficData.presetCarMap.get(carId).solution);
                    }
                }
            }
            //更新路口之间的静态权重
            for(TrafficCross cross : TrafficData.trafficCrossMap.values())
                cross.updateCrossCostMap();

            /*调整路径*/
            //正在行驶的车辆
            for(Integer carId : drivingSet){
                TrafficCar car = TrafficData.trafficCarMap.get(carId);
                if(car.isLock || car.info.isPrioriry)
                    continue;
                //未来路线发生拥堵时，改变路径
                if(SearchSolution.needChangeSolution(car) || (!car.info.isPreset && waitStartList.isEmpty() && car.solution.size() != car.planSolution.size())){
                    SearchSolution.searchSolution(car);
                }
                if(car.solution.size() > 1){
                    TrafficData.trafficRoadMap.get(car.solution.get(0) + "_" + car.solution.get(1)).willArrivedNormalCarNum ++;
                }
            }
            //登记车辆路线
            for(Integer carId : drivingSet){
                TrafficCar car = TrafficData.trafficCarMap.get(carId);
                if(car.info.isPreset)
                    SearchSolution.registRoadWillArrivedCarNum(car, 0);
                else
                    SearchSolution.registRoadWillArrivedCarNum(car, 0);
            }
            //预置车辆上路
            Iterator<Integer> iterator = TrafficData.presetCarList.iterator();
            while(iterator.hasNext()){
                Integer carId = iterator.next();
                if(TrafficData.presetCarMap.get(carId).starTime > startTime)
                    break;
                TrafficCar trafficCar = new TrafficCar(TrafficData.presetCarMap.get(carId).info
                        , TrafficData.presetCarMap.get(carId).starTime);
                //之前优先预置车辆太绕路，会导致info.isPreset = false.
                //预置车辆未来路径发生拥塞
                if(trafficCar.info.isPreset && TrafficData.changedPresetCarNum <= TrafficData.presetCarMap.size() * TrafficData.CHANGE_PRESET_MAX_CAR_RATE * TrafficData.BLOCKING_CHANGE_PRESET_CAR_RATE
                        && SearchSolution.needChangeSolution(TrafficData.presetCarMap.get(carId))){
                    SearchSolution.searchSolutionWithStaticInfo(trafficCar);
                    trafficCar.info.isPreset = false;
                    TrafficData.changedPresetCarNum ++;
//                    System.out.println("发车  预置车辆路径改变! 当前已改变预置车辆数量: " + TrafficData.changedPresetCarNum);
                }else{
                    trafficCar.solution = new ArrayList<>(TrafficData.presetCarMap.get(carId).solution);
                    trafficCar.planSolution = new ArrayList<>(TrafficData.presetCarMap.get(carId).solution);
                }
                SearchSolution.registRoadWillArrivedCarNum(trafficCar, 0);
                TrafficData.trafficRoadMap.get(trafficCar.solution.get(0) + "_" + trafficCar.solution.get(1)).startCarList.add(carId);
                TrafficData.trafficCarMap.put(carId, trafficCar);
                iterator.remove();
            }

            try {
                //跑一秒并解死锁
                runAndDealWithDealLock(waitStartList, drivingSet, priorityCarList, startTime);
            }catch (Exception e){
                e.printStackTrace();
                System.out.println("死锁了");
                return null;
            }
            //除去已经到达终点车辆并保存answer
            TrafficData.lastTimeArrivedCarNum = 0;
            for(Integer carId : TrafficData.arrivedCar){
                TrafficCar car = TrafficData.trafficCarMap.get(carId);
                if(!car.info.isPreset)
                    resMap.put(carId, TrafficData.trafficCarMap.get(carId));
                if(car.info.isPrioriry)
                    TrafficData.priorityEndTime = startTime;
                TrafficData.trafficCarMap.remove(carId);
                drivingSet.remove(carId);
                TrafficData.lastTimeArrivedCarNum ++;
            }
            // System.out.print("待发车数： " + (waitStartList.size() + priorityCarList.size() )
                    // + " 地图上车数:" + TrafficData.drivingSet.size()
                    // + " 时间为：");
            startTime ++;
            System.out.println(startTime);
        }
        return resMap;
    }

    private static void runAndDealWithDealLock(Set<Integer> waitStartCar, Set<Integer> drivingCar, List<Integer> priorityStartCarList, int timeCount) throws Exception {
        //回溯点更新
        roadMapUpdate(TrafficData.trafficRoadMap);
        carMapUpdate(TrafficData.trafficCarMap);
        crossMapUpdate();

        Set<Integer> copyWaitStartCar = new HashSet<>(waitStartCar);
        Set<Integer> copyDrivingCar = new HashSet<>(drivingCar);
        List<Integer> copyPriorityStartCarList = new LinkedList<>(priorityStartCarList);
        //出现死锁
        List<Integer> deadLockList = oneStep(copyWaitStartCar, copyDrivingCar, copyPriorityStartCarList, timeCount);
        int tryTimeCount = 0;
        while(deadLockList != null){
            //回溯
            crossMapBackUp();
            roadMapBackUp(TrafficData.trafficRoadMap);
            carMapBackUp(TrafficData.trafficCarMap);
            if(tryTimeCount > 50){
                for(Integer carId : deadLockList)
                    System.out.println("carId:" + carId + " isPriorty:" + TrafficData.trafficCarMap.get(carId).info.isPrioriry
                            + " isPreset:" + TrafficData.trafficCarMap.get(carId).info.isPreset
                            + " isLock:" + TrafficData.trafficCarMap.get(carId).isLock
                            + " roadId: " + TrafficData.trafficCarMap.get(carId).road.id +" 发生了死锁");
                throw new Exception();
            }
            for(Integer carId : deadLockList){
                TrafficCar car = TrafficData.trafficCarMap.get(carId);
                if(car.isLock || car.solution.size() < 2)
                    continue;
                //尝试解锁25次后，才开始用预置车辆解死锁
                if(tryTimeCount <= 25 && car.info.isPreset)
                    continue;
                if(car.info.isPreset && TrafficData.changedPresetCarNum > (int)(TrafficData.presetCarMap.size() * TrafficData.CHANGE_PRESET_MAX_CAR_RATE) - 2)
                    continue;
                if(car.info.isPreset){
                    TrafficData.changedPresetCarNum ++;
                    car.info.isPreset = false;
//                    System.out.println("Deadlock! Preset car change soluton ! Now changed preset car num is " + TrafficData.changedPresetCarNum);
                }
                //除去之前的路线，重新搜索新的路径
                Set<String> noAllowedWalkRoad = new HashSet<>();
                noAllowedWalkRoad.add(car.road.id.split("_")[1] + "_" + car.road.id.split("_")[0]);
                noAllowedWalkRoad.add(car.solution.get(0) + "_" + car.solution.get(1));
                SearchSolution.searchSolution(car, noAllowedWalkRoad);
                car.updateSolutionBackUp(car.solution);
            }
            //再次尝试
            copyWaitStartCar = new HashSet<>(waitStartCar);
            copyDrivingCar = new HashSet<>(drivingCar);
            deadLockList = oneStep(copyWaitStartCar, copyDrivingCar, copyPriorityStartCarList, timeCount);
            tryTimeCount ++;
        }
        //回溯
        roadMapBackUp(TrafficData.trafficRoadMap);
        carMapBackUp(TrafficData.trafficCarMap);
        crossMapBackUp();
        oneStep(waitStartCar, drivingCar, priorityStartCarList, timeCount);
    }

    //跑一秒
    private static List<Integer> oneStep( Set<Integer> waitStartCar, Set<Integer> drivingCar,
                                          List<Integer> priorityCarList,
                                          int timeCount){
        TrafficData.arrivedCar = new HashSet<>();
        TrafficData.drivingSet = drivingCar;
        TrafficData.timeCount = timeCount;
        TrafficData.arrivedCar = new HashSet<>();
        //初始化状态
        for(TrafficRoad road : TrafficData.trafficRoadMap.values()){
            road.isLock = false;
            road.isWaiting = false;
            road.waitRoad = null;
            road.isWaited = false;
        }

        List<Integer> crossList = new LinkedList<>(TrafficData.trafficCrossMap.keySet());
        Collections.sort(crossList);

        //上轮还没发完的车
        int willStartCarNum = updateWillStartCarNum();

        //登记本时间内出发的优先车并规划好路径
        uniformStartCar(waitStartCar
                , priorityCarList
                , true
                , TrafficData.MAX_CAR_NUM_MAX - drivingCar.size() - willStartCarNum
                , priorityCarList.size());

        //每个道路发车顺序重新排序
        for(TrafficRoad road : TrafficData.trafficRoadMap.values())
            Collections.sort(road.startCarList, roadStartCarListComparator);

        //登记所有车的状态
        for(TrafficRoad road : TrafficData.trafficRoadMap.values())
            road.regist();

        //优先车上路
        for(TrafficRoad road : TrafficData.trafficRoadMap.values())
            road.priorityCarStartInRoad();

        //十字路口调度
        int oneStepDispatchCount;
        do{
            oneStepDispatchCount = 0;
            for(Integer crossId : crossList){
                oneStepDispatchCount += TrafficData.trafficCrossMap.get(crossId).crossPriority(TrafficData.trafficRoadMap);
            }
        }while (oneStepDispatchCount > 0);

        //查看是否出现死锁
        List<Integer> deadLockList = new LinkedList<>();
        for(TrafficRoad road : TrafficData.trafficRoadMap.values())
            if(!road.priorityQueue.isEmpty())
                deadLockList.add(road.priorityQueue.peek().info.id);

        if(!deadLockList.isEmpty())
            return deadLockList;

        //除去到达终点的车
        for(Integer carId : TrafficData.arrivedCar){
            drivingCar.remove(carId);
        }

        int maxStartCarNum = !priorityCarList.isEmpty() ? TrafficData.MAX_CAR_NUM_MIN - drivingCar.size() - willStartCarNum
                : TrafficData.MAX_CAR_NUM_MAX - drivingCar.size() - willStartCarNum;
        //发车登记
        uniformStartCar(waitStartCar
                , null
                , false
                , maxStartCarNum
                , waitStartCar.size());

        //统一发车
        //每个道路发车顺序重新排序
        for(TrafficRoad road : TrafficData.trafficRoadMap.values()){
            Collections.sort(road.startCarList, roadStartCarListComparator);
            road.normalCarStartInRoad();
        }
        return null;
    }

    //均匀发车
    private static void uniformStartCar(Set<Integer> waitStartCarList, List<Integer> priorityStartCarList, boolean isPriority, int maxStartCarNum, int restWaitStartCarNum){
        int startCarNum = 0;
        //路口按照剩余未上路车辆数量由大到小顺序优先发车
        PriorityQueue<TrafficCross> startPriorityQueue = new PriorityQueue<>(startCarCrossComparator);
        startPriorityQueue.addAll(TrafficData.trafficCrossMap.values());
        while(!startPriorityQueue.isEmpty()){
            if(startCarNum > maxStartCarNum)
                break;
            TrafficCross cross = startPriorityQueue.poll();
            int crossStartCarNum = (int)(TrafficData.UNIFORM_START_CAR_PARAM
                    * (double)(maxStartCarNum * cross.waitStartCar.size() / (restWaitStartCarNum + 1)));
            //本路口的发车数量要算上预置车辆发车数量
            int willStartPresetCarNum = 0;
            for(String roadId : cross.outRoad){
                willStartPresetCarNum += TrafficData.trafficRoadMap.get(roadId).willStartCarNum;
            }
            crossStartCarNum = crossStartCarNum - willStartPresetCarNum > 0 ? crossStartCarNum - willStartPresetCarNum : 0;

            int startCarCount = 0;
            List<Integer> crossWaitStartCarList = null;
            if(isPriority)
                crossWaitStartCarList = cross.priorityCarWaitStartList;
            else
                crossWaitStartCarList = cross.waitStartCar;
            List<Integer> startCarList = new LinkedList<>();
            for(Integer carId : crossWaitStartCarList){
                if(startCarCount >= (int)(TrafficData.START_CAR_CHOOSE_NUM_PARAM * (double)crossStartCarNum))
                    break;
                Car car = TrafficData.carMap.get(carId);
                if(car.time > TrafficData.timeCount)
                    continue;
                TrafficCar trafficCar = new TrafficCar(car, TrafficData.timeCount);
                SearchSolution.searchSolutionWithStaticInfo(trafficCar);
                if(!car.isPrioriry && !SearchSolution.isAllowedStart(trafficCar.planSolution, car.speed)
                        && TrafficData.drivingSet.size() + waitStartCarList.size() > 2.0 * TrafficData.MAX_CAR_NUM_MAX)
                    continue;
                if(car.isPrioriry && SearchSolution.getSolutionBlockRate(trafficCar.planSolution) > TrafficData.START_CAR_THRESHOLD_PARAM)
                    continue;
                trafficCar.starTime = TrafficData.timeCount;
                TrafficData.trafficRoadMap.get(trafficCar.solution.get(0) + "_" + trafficCar.solution.get(1)).startCarList.add(carId);
                TrafficData.trafficCarMap.put(carId, trafficCar);
                startCarCount ++;
                startCarNum ++;
                startCarList.add(carId);
                SearchSolution.registRoadWillArrivedCarNum(trafficCar, 0);
            }
            for(Integer carId : startCarList){
                if(isPriority){
                    cross.priorityCarWaitStartList.remove(carId);
                    priorityStartCarList.remove(carId);
                }else{
                    cross.waitStartCar.remove(carId);
                }
                waitStartCarList.remove(carId);
            }
        }
    }

    //预测未来时间的将要发车的预置车辆个数
    private static int predictPresetCarNum(int startTime){
        int res = 0;
        for(int i = startTime + 1; i <= startTime + TrafficData.PREDICT_PRESET_NUM_TIME; i++){
            res += TrafficData.presetCarTimeMap.getOrDefault(i , new LinkedList<>()).size();
        }
        return res;
    }
    //更新道路本时间的发车数量（包括上个时间没有发完的车辆）
    private static int updateWillStartCarNum(){
        int willStartCarNum = 0;
        for(TrafficRoad road : TrafficData.trafficRoadMap.values()){
            road.willStartCarNum = 0;
            for(Integer carId : road.startCarList){
                TrafficCar car = TrafficData.trafficCarMap.get(carId);
                if(car.starTime > TrafficData.timeCount)
                    if(!car.info.isPrioriry)
                        break;
                    else continue;
                willStartCarNum ++;
                road.willStartCarNum ++;
            }
        }
        return willStartCarNum;
    }
    //增加预置车辆的未来路线的权重
    private static void addPresetSolutionCost(List<Integer> solution){
        for(int i = 0; i < solution.size() - 1 && i <= TrafficData.PREDICT_PRESET_STEP_NUM; i ++){
            TrafficData.trafficRoadMap.get(solution.get(i) + "_" + solution.get(i + 1)).willArrivedPresetCarNum ++;
        }
    }
    //生成树
    private static void generateTree(List<Integer> drivingCarList){
        List<TrafficCross> noArrived = new LinkedList<>(TrafficData.trafficCrossMap.values());
        Set<Integer> arrived = new HashSet<>();

        PriorityQueue<TrafficRoad> priorityQueue = new PriorityQueue<>(roadComparator);
        TrafficCross startCross = noArrived.get(0);
        for(String roadId : startCross.map.keySet()){
            if(TrafficData.trafficRoadMap.get(roadId).info.isDuplex
                    && TrafficData.trafficRoadMap.get(roadId).id.startsWith(startCross.info.id + ""))
                priorityQueue.add(TrafficData.trafficRoadMap.get(roadId));
        }
        arrived.add(startCross.info.id);
        noArrived.remove(0);
        while(!priorityQueue.isEmpty()){
            TrafficRoad tempRoad = priorityQueue.poll();
            TrafficCross endCross = TrafficData.trafficCrossMap
                    .get(Integer.valueOf(tempRoad.id.split("_")[1]));
            if(arrived.contains(endCross.info.id))
                continue;
            List<Integer> nextLink = hdfs(endCross, priorityQueue, arrived);
            TrafficCross preCross =  TrafficData.trafficCrossMap
                    .get(Integer.valueOf(tempRoad.id.split("_")[0]));
            for(Integer indexCrossId : nextLink){
                TrafficCross indexCross = TrafficData.trafficCrossMap.get(indexCrossId);
                noArrived.remove(indexCross);
                if(preCross != null){
                    preCross.nextStep.add(indexCross.info.id);
                    indexCross.nextStep.add(preCross.info.id);
                }
                for(String roadId : indexCross.map.keySet()){
                    TrafficRoad road = TrafficData.trafficRoadMap.get(roadId);
                    if(road.info.isDuplex
                            && road.id.startsWith(endCross.info.id + "")
                            && !arrived.contains(Integer.valueOf(road.id.split("_")[1]))){
                        priorityQueue.add(road);
                    }
                }
                preCross = null;
            }
        }
    }

    private static List<Integer> hdfs(TrafficCross cross, PriorityQueue<TrafficRoad> priorityQueue, Set<Integer> arrived){
        List<Integer> res = new LinkedList<>();
        Queue<TrafficCross> queue = new LinkedList<>();
        queue.offer(cross);

        while(!queue.isEmpty()){
            TrafficCross indexCross = queue.poll();
            if(arrived.contains(indexCross.info.id))
                continue;
            arrived.add(indexCross.info.id);
            res.add(indexCross.info.id);
            for(Integer nextCrossId : indexCross.nextStep)
                if(!arrived.contains(nextCrossId))
                    queue.offer(TrafficData.trafficCrossMap.get(nextCrossId));
        }
        return res;
    }
    
    //车辆信息回溯
    private static void carMapBackUp(Map<Integer, TrafficCar> carMap){
        for(TrafficCar car : carMap.values())
            car.backUp();
    }
    //车辆信息回溯点更新
    private static void carMapUpdate(Map<Integer, TrafficCar> carMap){
        for(TrafficCar car : carMap.values())
            car.update();
    }
    //道路信息回溯
    private static void roadMapBackUp(Map<String, TrafficRoad> roadMap){
        for(TrafficRoad road : roadMap.values())
            road.backUp();
    }
    //道路信息回溯点更新
    private static void roadMapUpdate(Map<String, TrafficRoad> roadMap){
        for(TrafficRoad road : roadMap.values())
            road.update();
    }
    //路口信息回溯
    private static void crossMapBackUp(){
        for(TrafficCross cross : TrafficData.trafficCrossMap.values())
            cross.backUp();
    }
    //路口信息回溯点更新
    private static void crossMapUpdate(){
        for(TrafficCross cross : TrafficData.trafficCrossMap.values())
            cross.update();
    }

    private static Comparator<TrafficRoad> roadComparator = new Comparator<TrafficRoad>() {
        @Override
        public int compare(TrafficRoad c1, TrafficRoad c2) {
            return c1.info.length - c2.info.length;
        }
    };
    //路口登记发车车辆 发车优先排序
    private static Comparator<Integer> crossWaitStartCarComparator = new Comparator<Integer>() {
        @Override
        public int compare(Integer i1, Integer i2) {
            Car car1 = TrafficData.carMap.get(i1);
            Car car2 = TrafficData.carMap.get(i2);
            if (car1.speed != car2.speed)
                return car1.speed - car2.speed;
            return car1.id - car2.id;
        }
    };

    private static double[] getVec(int[] point1, int[] point2){
        int dx = point1[0] - point2[0];
        int dy = point1[1] - point2[1];
        double dirLength = Math.sqrt(dx * dx + dy * dy) + 1;
        return new double[]{ (double)dx / dirLength, (double)dy / dirLength };
    }

    private static double getCos(double[] vec1, double[] vec2){
        if(vec1[0] * vec1[0] + vec1[1] * vec1[1] == 0
                || vec2[0] * vec2[0] + vec2[1] * vec2[1] == 0)
            return 0;
        return (vec1[0] * vec2[0] + vec1[1] * vec2[1])
                / Math.sqrt(vec1[0] * vec1[0] + vec1[1] * vec1[1])
                / Math.sqrt(vec2[0] * vec2[0] + vec2[1] * vec2[1]);
    }
    //均匀发车 发车的路口顺序 排序
    private static Comparator<TrafficCross> startCarCrossComparator = new Comparator<TrafficCross>() {
        @Override
        public int compare(TrafficCross c1, TrafficCross c2) {
            return c2.waitStartCar.size() + c2.priorityCarWaitStartList.size()
                    - c1.waitStartCar.size() - c1.priorityCarWaitStartList.size();
        }
    };
    //路口发车顺序排序
    private static Comparator<Integer> roadStartCarListComparator = new Comparator<Integer>() {
        @Override
        public int compare(Integer i1, Integer i2) {
            TrafficCar c1 = TrafficData.trafficCarMap.get(i1);
            TrafficCar c2 = TrafficData.trafficCarMap.get(i2);
            if(c1.info.isPrioriry ^ c2.info.isPrioriry)
                return c1.info.isPrioriry ? -1 : 1;
            if(c1.starTime != c2.starTime)
                return c1.starTime - c2.starTime;
            else
                return c1.info.id - c2.info.id;
        }
    };
}
