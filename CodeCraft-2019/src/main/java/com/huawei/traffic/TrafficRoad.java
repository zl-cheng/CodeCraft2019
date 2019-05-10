package com.huawei.traffic;

import com.huawei.CONSTANT.TrafficData;
import com.huawei.SearchSolution;
import com.huawei.domain.Road;
import com.huawei.enums.DirEnum;
import com.huawei.enums.StatusEnum;

import java.util.*;

/**
 * @author 程智凌
 * @date 2019/3/9 15:54
 */
public class TrafficRoad {
    public String id;                                   //因为存在双向 uid为 from路口_to路口
    public Road info;                                   //车道静态信息
    public List<List<TrafficCar>> queues;               //车道情况
    public PriorityQueue<TrafficCar> in;                //路口调度时 进方向的优先队列
    public PriorityQueue<TrafficCar> priorityQueue;     //道路道路时 道路调度优先队列
    public List<Integer> startCarList;                  //从本道路发车的车辆
    public int val = 1;                                 //用于路径优化的 权重
    public int carNum = 0;                              //当前车辆数
    public int willStartCarNum = 0;                     //本时刻等待发车的车辆
    public double willArrivedPresetCarNum = 0;          //将要到本路的预置车辆数量
    public double willArrivedPrirotyCarNum = 0;         //将要到本路的优先车辆数量
    public double willArrivedNormalCarNum = 0;          //将要到本路的普通车辆数量
    public int lastTimeLeaveCarNum = 0;                 //上个单位时间道路流量
    public int thisTimeLeaveCarNum = 0;                 //本单位时间道路流量

    public TrafficRoad waitRoad;                        //导致本道路堵塞的道路
    public boolean isWaiting;                           //堵塞状态
    public boolean isWaited;

    public double[] willArrivedCarNum = new double[200];//未来200时刻本道路的到达车数

    private BackUp backUp;                              //回溯点
    public boolean isLock = false;                      //堵塞锁状态

    class BackUp{
        List<List<TrafficCar>> queuesB;
        List<Integer> startCarListB;
        public double[] willArrivedCarNumB;
        public double willArrivedPresetCarNumB = 0;   //(当前只预测预置车辆的数量)将要到这条路的车辆
        public double willArrivedPrirotyCarNumB = 0;   //(当前只预测预置车辆的数量)将要到这条路的车辆
        public double willArrivedNormalCarNumB = 0;
        public BackUp(){
            willArrivedPresetCarNumB = willArrivedPresetCarNum;
            willArrivedPrirotyCarNumB = willArrivedPrirotyCarNum;
            willArrivedNormalCarNumB = willArrivedNormalCarNum;
            queuesB = new ArrayList<>(queues);
            startCarListB = new LinkedList<>();
            willArrivedCarNumB = Arrays.copyOf(willArrivedCarNum, willArrivedCarNum.length);
        }
    }

    public TrafficRoad(Road road, String id){
        info = road;
        this.id = id;
        queues = new ArrayList<>();
        in = new PriorityQueue<>(inComparator);
        priorityQueue = new PriorityQueue<>(outComparator);
        startCarList = new LinkedList<>();
        for(int i = 0; i < info.channel; i++){
            queues.add(new ArrayList<>());
        }
        backUp = new BackUp();
    }

    public void updateRoadCar(){
        for(int i = 0; i < info.channel; i++){
            TrafficCar headCar = null;
            for(int j = queues.get(i).size() - 1; j >= 0; j--){
                TrafficCar car = queues.get(i).get(j);
                if(headCar == null && car.status == StatusEnum.WAIT){
                    car.pos = car.predictPos;
                    car.status = StatusEnum.FINISH;
                }else if(car.status != StatusEnum.FINISH && headCar != null && headCar.status == StatusEnum.FINISH){
                    if(car.status == StatusEnum.INROAD)
                        car.pos = headCar.pos - 1;
                    else
                        car.pos = Math.min(car.predictPos, headCar.pos - 1);
                    car.status = StatusEnum.FINISH;
                }
                headCar = car;
            }
        }
    }

    //登记与更新道路上所有车的信息
    public void regist(){
        for(int i = 0; i < info.channel; i++){
            TrafficCar headCar = null;
            for(int j = queues.get(i).size() - 1; j >= 0; j--){
                TrafficCar car = queues.get(i).get(j);
                //能到路口而且前面没车挡着 或者 前车也能到路口
                if(car.pos + car.speed > info.length && (headCar == null || headCar.status == StatusEnum.INROAD)){
                    if(car.solution.size() > 1){
                        TrafficRoad nextRoad = TrafficData.trafficRoadMap
                                .get(car.solution.get(0) + "_" + car.solution.get(1));
                        int nextSpeed = Math.min(car.info.speed, nextRoad.info.speed);
                        car.predictPos =
                                nextSpeed + car.pos > info.length ? nextSpeed + car.pos - info.length : 0;
                        car.nextRoadId = nextRoad.id;
                        car.status = StatusEnum.INROAD;
                    } else{//到终点了
                        car.status = StatusEnum.INROAD;
                        car.predictPos = car.road.info.length;
                        car.nextRoadId = TrafficCross.getStraightRoad(this);
                    }
                }
                //前车挡住了
                else{
                    if(headCar != null && car.pos + car.speed >= headCar.pos){
                        if(headCar.status == StatusEnum.FINISH){
                            car.status = StatusEnum.FINISH;
                            car.pos = headCar.pos - 1;
                        }else {
                            car.status = StatusEnum.WAIT;
                            car.predictPos = Math.min(car.pos + car.speed, car.road.info.length);
                        }
                    }else{
                        car.pos = car.pos + car.speed;
                        car.status = StatusEnum.FINISH;
                    }
                }
                headCar = car;
            }
        }
    }

    //所有车辆正常发车  里面包括没发的优先车辆
    public void normalCarStartInRoad(){
        if (startCarList.isEmpty())
            return;
        Iterator<Integer> iterator = startCarList.iterator();
        while(iterator.hasNext()){
            Integer carId = iterator.next();
            TrafficCar car = TrafficData.trafficCarMap.get(carId);
            if(car.starTime > TrafficData.timeCount)
                if(!car.info.isPrioriry)
                    break;
                else continue;
            car.predictPos = Math.min(car.info.speed, info.speed);
            car.speed = Math.min(car.info.speed, info.speed);
            if(carIntoRoad(car)){
                iterator.remove();
                TrafficData.drivingSet.add(carId);
            }
        }
    }

    //优先车发车
    public void priorityCarStartInRoad() {
        if (startCarList.isEmpty())
            return;
        Iterator<Integer> iterator = startCarList.iterator();
        while(iterator.hasNext()){
            Integer carId = iterator.next();
            TrafficCar car = TrafficData.trafficCarMap.get(carId);
            if(car.starTime > TrafficData.timeCount || !car.info.isPrioriry)
                break;
            car.predictPos = Math.min(car.info.speed, info.speed);
            car.speed = Math.min(car.info.speed, info.speed);
            if(carIntoRoad(car)){
                iterator.remove();
                TrafficData.drivingSet.add(carId);
            }
        }
    }

    private void carInRoadChangeInfo(TrafficCar car){
        car.speed = Math.min(car.info.speed, info.speed);
        car.status = StatusEnum.FINISH;
        car.solutionBackUp.add(car.solution.get(0));
        car.solution.remove(0);

        //可能是刚发车的车辆
        if(car.road != null){
            car.road.queues.get(car.channel).remove(car);
        }
        car.road = this;
        car.isLock = false;
    }

    //更新道路调度优先级
    public void updateDispatchPriority(){
        for(int i = 0; i < queues.size(); i++){
            if(queues.get(i).isEmpty())
                continue;
            for(int j = queues.get(i).size() - 1; j >= 0; j--){
                TrafficCar car = queues.get(i).get(j);
                if(car.status == StatusEnum.FINISH)
                    break;
                if(!priorityQueue.contains(car)){
                    priorityQueue.add(car);
                }
                break;
            }
        }
    }

    //道路调度
    public int dispatch(){
        updateDispatchPriority();
        if(priorityQueue.isEmpty())
            return 0;
        int dispatchNum = 0;
        while(!priorityQueue.isEmpty()){
            TrafficCar car = priorityQueue.peek();
            if(car.status == StatusEnum.INROAD){
                ///// 到终点的车也可能会与优先车辆冲突
                if (car.nextRoadId != null) {
                    TrafficRoad nextRoad = TrafficData.trafficRoadMap.get(car.nextRoadId);
                    if (!nextRoad.in.contains(car))
                        nextRoad.in.add(car);
                    if (car.info.id.equals(nextRoad.in.peek().info.id) && car.move()) {
                        priorityQueue.poll();
                        nextRoad.in.poll();
                        updateRoadCar();
                        updateDispatchPriority();
                        priorityCarStartInRoad();
                        dispatchNum++;
                    } else break;
                } else {
                    if (car.move()) {
                        priorityQueue.poll();
                        dispatchNum++;
                        updateRoadCar();
                        updateDispatchPriority();
                        priorityCarStartInRoad();
                        continue;
                    } else break;
                }
            }else{
                if(car.move()){
                    priorityQueue.poll();
                    updateDispatchPriority();
                    dispatchNum ++;
                }else break;
            }
        }
        return dispatchNum;
    }

    //判断挡住的车是否为FINISH 状态
    public boolean getHeadCarStatus(TrafficCar car){
        if(car.predictPos <= 0)
            return true;
        for(int i = 0; i < queues.size(); i++){
            if(!queues.get(i).isEmpty()
                    && queues.get(i).get(0).pos == 1
                    && queues.get(i).get(0).status == StatusEnum.FINISH)
                continue;
            return queues.get(i).isEmpty()
                    || queues.get(i).get(0).pos > car.predictPos
                    || queues.get(i).get(0).status == StatusEnum.FINISH;
        }
        return true;
    }

    //返回false 表明道路已满
    public boolean carIntoRoad(TrafficCar car){
        if(car.predictPos <= 0){
            car.isLock = true;
            return false;
        }
        for(int i = 0; i < queues.size(); i++){
            if(!queues.get(i).isEmpty()
                    && queues.get(i).get(0).pos == 1
                    && queues.get(i).get(0).status == StatusEnum.FINISH)
                continue;
            if(!queues.get(i).isEmpty()
                    && queues.get(i).get(0).status != StatusEnum.FINISH
                    && queues.get(i).get(0).pos <= car.predictPos){
                return false;
            }
            if(queues.get(i).isEmpty() || queues.get(i).get(0).pos > 1) {
                //车道没车
                if (queues.get(i).isEmpty()) {
                    car.pos = car.predictPos;
                } else {
                    car.pos = Math.min(queues.get(i).get(0).pos - 1, car.predictPos);
                }
                queues.get(i).add(0, car);
                carInRoadChangeInfo(car);
                car.channel = i;
                return true;
            }
        }
        //刚发车
        if(car.road == null)
            return false;
        car.road.isLock = true;
        car.pos = car.road.info.length;
        car.isLock = true;
        car.road.thisTimeLeaveCarNum ++;
        car.road.waitRoad = this;
        return true;
    }

    public void updateInfo(){
        willArrivedPresetCarNum = 0;
        willArrivedPrirotyCarNum = 0;
        willArrivedNormalCarNum = 0;
        willArrivedCarNum = new double[200];
        lastTimeLeaveCarNum = thisTimeLeaveCarNum;
        thisTimeLeaveCarNum = 0;
        carNum = 0;
        val = 0;
        for(List<TrafficCar> list : queues)
            carNum += list.size();
        for(List<TrafficCar> list : queues)
            if(list.isEmpty())
                val += info.length;
            else
                val += list.get(0).pos - 1;
    }

    public int getRoadCarNum(){
        int sum = 0;
        for(List<TrafficCar> list : queues)
            sum += list.size();
        return sum;
    }

    private static Comparator<TrafficCar> inComparator = new Comparator<TrafficCar>() {
        @Override
        public int compare(TrafficCar c1, TrafficCar c2) {
            if(c1.info.isPrioriry ^ c2.info.isPrioriry)
                return c1.info.isPrioriry ? -1 : 1;
            //判断方向
            DirEnum d1, d2;
            d1 = getTurnDir(c1);
            d2 = getTurnDir(c2);
            if (d1.val > d2.val)
                return -1;
            else if (d1.val < d2.val)
                return 1;
            else return outComparator.compare(c1,c2);
        }
    };

    private static Comparator<TrafficCar> outComparator = new Comparator<TrafficCar>() {
        @Override
        public int compare(TrafficCar c1, TrafficCar c2) {
            if(c1.info.isPrioriry ^ c2.info.isPrioriry)
                return c1.info.isPrioriry ? -1 : 1;
            //离入口的距离
            if(c1.road.info.length - c1.pos < c2.road.info.length - c2.pos)
                return -1;
            else if(c1.road.info.length - c1.pos > c2.road.info.length - c2.pos)
                return 1;
            else{
                //判断车道
                return c1.channel - c2.channel;
            }
        }
    };

    private static DirEnum getTurnDir(TrafficCar car){
        if(car.solution.size()== 1)
            return DirEnum.STRAIGHT;
        else
            return TrafficData.trafficCrossMap
                    .get(car.solution.get(0))
                    .getDir(car.road.id ,car.solution.get(0), car.solution.get(1));
    }

    public void update(){
        backUp = new BackUp();
        backUp.queuesB = new LinkedList<>();
        backUp.startCarListB = new LinkedList<>(startCarList);
        for(List<TrafficCar> list : queues){
            List<TrafficCar> tempList = new LinkedList<>();
            tempList.addAll(list);
            backUp.queuesB.add(tempList);
        }
    }

    public void backUp(){
        thisTimeLeaveCarNum = 0;
        priorityQueue = new PriorityQueue<>(outComparator);
        in = new PriorityQueue<>(inComparator);
        queues = new LinkedList<>();
        startCarList = new LinkedList<>(backUp.startCarListB);
        willArrivedPrirotyCarNum = backUp.willArrivedPrirotyCarNumB;
        willArrivedNormalCarNum = backUp.willArrivedPrirotyCarNumB;
        willArrivedPresetCarNum = backUp.willArrivedPresetCarNumB;
        willArrivedCarNum = Arrays.copyOf(backUp.willArrivedCarNumB, willArrivedCarNum.length);
        for(List<TrafficCar> list : backUp.queuesB){
            List<TrafficCar> tempList = new LinkedList<>();
            tempList.addAll(list);
            queues.add(tempList);
        }
    }

    public static void priorityCarAllInRoad(){
        for(TrafficRoad road : TrafficData.trafficRoadMap.values())
            road.priorityCarStartInRoad();
    }

    public double getRoadVal(TrafficCar car){
        double crowdParam = 0.0;
        if(car.info.isPrioriry)
            crowdParam = ((double)carNum
                    - TrafficData.FLOW_NUM_PARAM *  (double)lastTimeLeaveCarNum
                    + TrafficData.PRESET_CAR_PREDICT_SOLUTION_ADD * (double)willArrivedPresetCarNum
                    + TrafficData.NORMAL_CAR_PREDICT_SOLUTION_ADD * (double)willArrivedPrirotyCarNum)
                    / (double)(info.length * info.channel);
        else
            crowdParam = ((double)carNum
                    - TrafficData.FLOW_NUM_PARAM * (double)lastTimeLeaveCarNum
                    + TrafficData.NORMAL_CAR_PREDICT_SOLUTION_ADD * (double)willArrivedNormalCarNum
                    + TrafficData.PRESET_CAR_PREDICT_SOLUTION_ADD * (double)willArrivedPresetCarNum
                    + TrafficData.PRIORITY_CAR_PREDICT_SOLUTION_ADD * (double)willArrivedPrirotyCarNum
            )/ (double)(info.length * info.channel);
        crowdParam = crowdParam < 0 ? 0 : crowdParam;
        val = (int)((double)info.length / (double)Math.min(info.speed, car.info.speed)
                * (1.0 + TrafficData.CAR_NUM_PARAM * crowdParam)
                * (1.0 - TrafficData.BLOCK_CHANNEL_PARAM * info.channel));
        if(isLock && (double)carNum > TrafficData.BLOCK_PARAM * (double)info.length * (double)info.channel)
            val = (int)(TrafficData.LOCK_AND_BLOCK_PARAM * (double)val);
        if(isWaiting)
            val = (int)(TrafficData.LOCK_AND_BLOCK_PARAM * (double)val);
        return val;
    }
}
