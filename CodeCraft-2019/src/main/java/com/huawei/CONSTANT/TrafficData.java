package com.huawei.CONSTANT;

import com.huawei.domain.Car;
import com.huawei.traffic.TrafficCar;
import com.huawei.traffic.TrafficCross;
import com.huawei.traffic.TrafficRoad;

import java.util.*;

/**
 * @author 程智凌
 * @date 2019/3/10 17:31
 */
public class TrafficData {
    public static long systemStartTime = 0;
    public static long MAX_RUNNING_TIME = 14 * 60  * 1000;
    public static int priorityEndTime = 0;

    public static Map<Integer, Car> carMap = new HashMap<>();
    public static Map<Integer, TrafficCar> trafficCarMap = new HashMap<>();
    public static Map<Integer, TrafficCross> trafficCrossMap = new HashMap<>();
    public static Map<String, TrafficRoad> trafficRoadMap = new HashMap<>();
    public static Set<Integer> arrivedCar = new HashSet<>();
    public static Set<Integer> drivingSet = new HashSet<>();
    public static Map<Integer, TrafficCar> presetCarMap = new HashMap<>();
    public static Map<Integer, List<Integer>> presetCarTimeMap = new HashMap<>();
    public static List<Integer> presetCarList = new LinkedList<>();
    public static int lastTimeArrivedCarNum = 0;
    public static int timeCount;
    public static int changedPresetCarNum = 0;

    //调参部分
    public static double UNIFORM_START_CAR_PARAM = 1.1;          //均匀发车系数
    public static int MAX_CAR_NUM_MIN = 13700;                     //地图上最多的在跑的车辆总数
    public static int MAX_CAR_NUM_MAX = 14000;
    public static double BLOCK_CHANNEL_PARAM = 0.032;             //0.03 0.02-0.05 损失函数中 道路宽度的系数
    public static double CAR_NUM_PARAM = 3.7;                     //建议为5 一般4-6 损失函数中 道路车辆的系数
    public static double FLOW_NUM_PARAM = 0.0;
    public static double SPEED_PARAM = 0.0;                       //损失函数中 车速度与道路匹配的系数（暂时没用上）
    //阈值参数(一般都不怎么改)
    public static float BLOCK_PARAM = 0.7f;                       //建议为0.7 0.6-0.7 容忍道路拥堵的占用比 channel* length * 本参数 = 道路最多容忍的车辆数量
    public static double LOCK_AND_BLOCK_PARAM = 1.5;              //道路拥堵时 惩罚系数
    public static double START_CAR_THRESHOLD_PARAM = 5.0;         //发车时规划的损失最小路线的损失值 如果超过该系数*静态最短路径 就不发车
    public static int PREDICT_PRESET_NUM_TIME = 80;               //预测未来预置车辆发车数量的时间
    public static int PREDICT_PRESET_STEP_NUM = 3;                //建议为3 预置车辆预测的步数
    public static double START_CAR_CHOOSE_NUM_PARAM = 5.0;        //发车选择的范围系数
    public static double PRIORITY_CAR_PREDICT_SOLUTION_ADD = 3.0; //优先车辆未来路径加权
    public static double PRESET_CAR_PREDICT_SOLUTION_ADD = 1.5;   //预置车辆未来路径加权
    public static double NORMAL_CAR_PREDICT_SOLUTION_ADD = 0.2;   //普通车辆未来路径加权  
    public static double PREDICT_FUTURE_TIME_BLOCK_PARAM = 1.0;   //发车路径中判断未来200时刻超过道路容量 * 本系数
    public static int CHANGE_SOLUTION_PREDICT_STEP = 2;           //未来路径发生拥堵时，改变路径      

    public static double CHANGE_PRESET_MAX_CAR_RATE = 0.1;
    public static double BLOCKING_CHANGE_PRESET_CAR_RATE = 0.6;
}
