package com.huawei.traffic;

import com.huawei.CONSTANT.TrafficData;
import com.huawei.domain.Car;
import com.huawei.enums.StatusEnum;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;

/**
 * @author 程智凌
 * @date 2019/3/9 15:53
 */
public class TrafficCar {
    public Car info;                        //车辆静态信息
    public TrafficRoad road;                //车辆所在道路

    public int speed = 0;                   //车辆当前速度
    public int pos = 0;                     //车辆当前位置
    public int channel = 0;                 //车辆当前所处的车道序号
    public int starTime = 0;                //实际发车时间
    public List<Integer> solution;          //拟定路线  会随着车的移动更新
    public List<Integer> solutionBackUp;    //已经走过的路径
    public List<Integer> planSolution;      //计划的路径
    public StatusEnum status;               //调度时的车辆状态
    public String nextRoadId;               //过路口时候 到的下一个路口id
    public int predictPos = 0;              //调度时的预期位置
    public boolean isArrived;               //是否达到终点
    public boolean isLock = false;          //强死锁状态
    private BackUp backUp;                  //回溯点

    class BackUp{
        public TrafficRoad roadB;
        public int speedB;
        public int posB;
        public int channelB ;
        public List<Integer> solutionB; //拟定路线 不会更新
        public List<Integer> solutionBackUpB;
        public int predictPosB ;
        public String nextRoadIdB;
        public boolean isLockB;
        public int startTimeB;

        public BackUp(){
            this.roadB = road;
            this.speedB = speed;
            this.posB = pos;
            this.channelB = channel;
            this.solutionB = new LinkedList<>(solution);
            this.solutionBackUpB = new LinkedList<>(solutionBackUp);
            this.predictPosB = predictPos;
            this.nextRoadIdB = nextRoadId;
            this.isLockB = isLock;
            this.startTimeB = starTime;
        }
    }

    public TrafficCar(Car info, Integer starTime) {
        this.info = info;
        this.solution = new LinkedList<>();
        this.status = StatusEnum.INROAD;
        this.isArrived = false;
        this.starTime = starTime;
        solution = new LinkedList<>();   //拟定路线  会随着车的移动更新
        solutionBackUp = new LinkedList<>();
        backUp = new BackUp();
    }

    public boolean move(){
        if(status == StatusEnum.FINISH)
            return false;
        TrafficCar headCar = getHeadCar();
        //能到终点
        if(solution.size() <= 1 && status == StatusEnum.INROAD){
            if(headCar == null) {
                status = StatusEnum.FINISH;
                TrafficCross.arrive(this);
                return true;
            }else{
                if(headCar.status == StatusEnum.FINISH){
                    pos = headCar.pos - 1;
                    status = StatusEnum.FINISH;
                    isLock = false;
                    return true;
                }else
                    return false;
            }
            //没车堵着
        }else if(headCar == null){
            if(status == StatusEnum.INROAD){
                if(predictPos <= 0){
                    pos = road.info.length;
                    status = StatusEnum.FINISH;
                    isLock = true;
                    return true;
                } else if(TrafficData.trafficRoadMap
                        .get(solution.get(0)+"_"+solution.get(1))
                        .getHeadCarStatus(this)){
                    //路口拥堵 没过去
                    if(!TrafficData.trafficRoadMap
                            .get(solution.get(0)+"_"+solution.get(1))
                            .carIntoRoad(this)){
                        return false;
                    }
                    status = StatusEnum.FINISH;
                    return true;
                }else
                    return false;
            }else{
                pos = predictPos;
                status = StatusEnum.FINISH;
                isLock = false;
                return true;
            }
        }else{
            if(headCar.status != StatusEnum.FINISH && (status == StatusEnum.INROAD || predictPos >= headCar.pos))
                return false;
            if(status != StatusEnum.INROAD)
                pos = Math.min(headCar.pos - 1, predictPos);
            else
                pos = headCar.pos - 1;
            status = StatusEnum.FINISH;
            isLock = false;
            return true;
        }
    }

    private TrafficCar getHeadCar(){
        List<TrafficCar> list = road.queues.get(channel);
        for(int i = list.size() - 1; i >= 0 ; i --){
            if(list.get(i).info.id.equals(info.id)){
                if(i == list.size() - 1)
                    return null;
                else
                    return list.get(i + 1);
            }
        }
        return null;
    }

    public void showPos(){
        if(road == null)
            System.out.println("id=" + info.id +" 车辆还没发车");
        else if(isArrived)
            System.out.println("id=" + info.id + " 已经到达目的地了");
        else
            System.out.println("id=" + info.id + " roadId=" + road.id + " channel=" + channel + " pos=" + pos);
    }

    public void update(){
        backUp = new BackUp();
    }

    public void updateSolutionBackUp(List<Integer> solution){
        backUp.solutionB = new LinkedList<>(solution);
    }

    public void backUp(){
        status = StatusEnum.FINISH;
        road = backUp.roadB;
        speed = backUp.speedB;
        pos = backUp.posB;
        channel = backUp.channelB;
        solution = new LinkedList<>(backUp.solutionB);
        solutionBackUp = new LinkedList<>(backUp.solutionBackUpB);
        predictPos = backUp.predictPosB;
        nextRoadId = backUp.nextRoadIdB;
        isLock = backUp.isLockB;
        starTime = backUp.startTimeB;
    }
}
