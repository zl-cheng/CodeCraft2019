package com.huawei;

import com.huawei.CONSTANT.TrafficData;
import com.huawei.domain.Car;
import com.huawei.domain.Cross;
import com.huawei.domain.Road;
import com.huawei.traffic.TrafficCar;
import com.huawei.traffic.TrafficCross;
import com.huawei.traffic.TrafficRoad;

import java.util.*;

public class PleaseGetAnswer {

    private static final int map1Sha = -720935047;

    private static final int map2Sha = 596815477;

    public static void getSolutionOnce(String carPath, String roadPath, String crossPath, String presetCarPath, String ansPath) throws Exception {
        TrafficData.systemStartTime = System.currentTimeMillis();
        inputTrafficData(carPath, roadPath, crossPath, presetCarPath);
        double[] resParams = initResultParam();
        int priorityStartTime = (int) resParams[1];
        Map<Integer, TrafficCar> res = GetSolution.getSolution(ansPath);
        if (res == null)
            System.out.println("死锁了 发生在" + TrafficData.timeCount + " 时刻");
        else
            System.out.println("成绩为 " + Math.round((double) (TrafficData.timeCount - 1)
                    + resParams[0] * (TrafficData.priorityEndTime - priorityStartTime))
                    + " 当前计算时间为：  " + (System.currentTimeMillis() - TrafficData.systemStartTime) / 1000);
        OutputTxt.output(res, ansPath);
    }

    public static void getSolution(String carPath, String roadPath, String crossPath, String presetCarPath, String ansPath) throws Exception {
        TrafficData.systemStartTime = System.currentTimeMillis();
        inputTrafficData(carPath, roadPath, crossPath, presetCarPath);
        int mapSha = getMapHash();
        System.out.println("地图sha值为: " + mapSha);
        if (mapSha == map1Sha) {
            System.out.println("成功识别map1");
            TrafficData.UNIFORM_START_CAR_PARAM = 1.1;          //均匀发车系数
            TrafficData.MAX_CAR_NUM_MIN = 16200;                     //地图上最多的在跑的车辆总数
            TrafficData.MAX_CAR_NUM_MAX = 16500;
            TrafficData.BLOCK_CHANNEL_PARAM = 0.03;             //0.03 0.02-0.05 损失函数中 道路宽度的系数
            TrafficData.CAR_NUM_PARAM = 3.9;                     //建议为5 一般4-6 损失函数中 道路车辆的系数
            TrafficData.FLOW_NUM_PARAM = 0.0;
            TrafficData.SPEED_PARAM = 0.0;                       //损失函数中 车速度与道路匹配的系数（暂时没用上）
            TrafficData.BLOCK_PARAM = 0.7f;                       //建议为0.7 0.6-0.7 容忍道路拥堵的占用比 channel* length * 本参数 = 道路最多容忍的车辆数量
            TrafficData.LOCK_AND_BLOCK_PARAM = 1.5;                  //道路拥堵时 惩罚系数
            TrafficData.START_CAR_THRESHOLD_PARAM = 5.0;         //发车时规划的损失最小路线的损失值 如果超过该系数*静态最短路径 就不发车
            TrafficData.PREDICT_PRESET_NUM_TIME = 80;               //预测未来预置车辆发车数量的时间
            TrafficData.PREDICT_PRESET_STEP_NUM = 3;                //建议为3 预置车辆预测的步数
            TrafficData.START_CAR_CHOOSE_NUM_PARAM = 5.0;        //发车选择的范围系数
            TrafficData.PRIORITY_CAR_PREDICT_SOLUTION_ADD = 3.0;      //优先车辆未来路径加权
            TrafficData.PRESET_CAR_PREDICT_SOLUTION_ADD = 1.5;   //预置车辆未来路径加权
            TrafficData.NORMAL_CAR_PREDICT_SOLUTION_ADD = 0.2;
            TrafficData.PREDICT_FUTURE_TIME_BLOCK_PARAM = 1.0;
            TrafficData.CHANGE_SOLUTION_PREDICT_STEP = 2;
            TrafficData.CHANGE_PRESET_MAX_CAR_RATE = 0.1;
            TrafficData.BLOCKING_CHANGE_PRESET_CAR_RATE = 0.6;
//            getSolutionOnce(carPath, roadPath, crossPath, presetCarPath, ansPath);
        } else if (mapSha == map2Sha) {
            System.out.println("成功识别map2");
            TrafficData.UNIFORM_START_CAR_PARAM = 1.1;          //均匀发车系数
            TrafficData.MAX_CAR_NUM_MIN = 13500;                     //地图上最多的在跑的车辆总数
            TrafficData.MAX_CAR_NUM_MAX = 14000;
            TrafficData.BLOCK_CHANNEL_PARAM = 0.032;             //0.03 0.02-0.05 损失函数中 道路宽度的系数
            TrafficData.CAR_NUM_PARAM = 3.7;                     //建议为5 一般4-6 损失函数中 道路车辆的系数
            TrafficData.FLOW_NUM_PARAM = 0.0;
            TrafficData.SPEED_PARAM = 0.0;                       //损失函数中 车速度与道路匹配的系数（暂时没用上）
            TrafficData.BLOCK_PARAM = 0.7f;                       //建议为0.7 0.6-0.7 容忍道路拥堵的占用比 channel* length * 本参数 = 道路最多容忍的车辆数量
            TrafficData.LOCK_AND_BLOCK_PARAM = 1.5;                  //道路拥堵时 惩罚系数
            TrafficData.START_CAR_THRESHOLD_PARAM = 5.0;         //发车时规划的损失最小路线的损失值 如果超过该系数*静态最短路径 就不发车
            TrafficData.PREDICT_PRESET_NUM_TIME = 80;               //预测未来预置车辆发车数量的时间
            TrafficData.PREDICT_PRESET_STEP_NUM = 3;                //建议为3 预置车辆预测的步数
            TrafficData.START_CAR_CHOOSE_NUM_PARAM = 5.0;        //发车选择的范围系数
            TrafficData.PRIORITY_CAR_PREDICT_SOLUTION_ADD = 3.0;      //优先车辆未来路径加权
            TrafficData.PRESET_CAR_PREDICT_SOLUTION_ADD = 1.5;   //预置车辆未来路径加权
            TrafficData.NORMAL_CAR_PREDICT_SOLUTION_ADD = 0.2;
            TrafficData.PREDICT_FUTURE_TIME_BLOCK_PARAM = 1.0;
            TrafficData.CHANGE_SOLUTION_PREDICT_STEP = 2;
            TrafficData.CHANGE_PRESET_MAX_CAR_RATE = 0.1;
            TrafficData.BLOCKING_CHANGE_PRESET_CAR_RATE = 0.6;
//            getSolutionOnce(carPath, roadPath, crossPath, presetCarPath, ansPath);
        }
        double[] resParams = initResultParam();
        int priorityStartTime = (int) resParams[1];
        long bestAns = Integer.MAX_VALUE;
        while (System.currentTimeMillis() - TrafficData.systemStartTime < TrafficData.MAX_RUNNING_TIME) {
            System.out.println("当前车辆数为： " + TrafficData.MAX_CAR_NUM_MAX);
            clearTrafficData();
            inputTrafficData(carPath, roadPath, crossPath, presetCarPath);
            Map<Integer, TrafficCar> res = GetSolution.getSolution(ansPath);
            if (res != null
                    && Math.round((double) (TrafficData.timeCount - 1)
                    + resParams[0] * (TrafficData.priorityEndTime - priorityStartTime))
                    < bestAns) {
                bestAns = Math.round((double) (TrafficData.timeCount - 1)
                        + resParams[0] * (TrafficData.priorityEndTime - priorityStartTime));
                OutputTxt.output(res, ansPath);
            }
            if (res != null)
                System.out.println(" 调度时间为: " + TrafficData.timeCount
                        + "成绩为: " + Math.round((double) (TrafficData.timeCount - 1)
                        + resParams[0] * (TrafficData.priorityEndTime - priorityStartTime))
                        + " 当前计算时间为：  " + (System.currentTimeMillis() - TrafficData.systemStartTime) / 1000);
            TrafficData.MAX_CAR_NUM_MAX -= (int) ((double) TrafficData.MAX_CAR_NUM_MAX * 0.20);
            TrafficData.MAX_CAR_NUM_MIN = TrafficData.MAX_CAR_NUM_MAX - 300;
            if (TrafficData.MAX_CAR_NUM_MIN < 0)
                TrafficData.MAX_CAR_NUM_MIN = 0;
        }
    }

    private static int getMapHash() {
        int[] mapData = new int[6];
        int sumRoadLength = 0, sumRoadChannel = 0, sumCarSpeed = 0;
        for (TrafficRoad road : TrafficData.trafficRoadMap.values()) {
            sumRoadLength += road.info.length;
            sumRoadChannel += road.info.channel;
        }
        for (Car car : TrafficData.carMap.values())
            sumCarSpeed += car.speed;
        mapData[0] = TrafficData.trafficRoadMap.size();
        mapData[1] = sumRoadLength;
        mapData[2] = sumRoadChannel;
        mapData[3] = TrafficData.carMap.size();
        mapData[4] = sumCarSpeed;
        mapData[5] = TrafficData.trafficCrossMap.size();
        return Arrays.hashCode(mapData);
    }

    private static void clearTrafficData() {
        TrafficData.priorityEndTime = 0;

        TrafficData.carMap = new HashMap<>();
        TrafficData.trafficCarMap = new HashMap<>();
        TrafficData.trafficCrossMap = new HashMap<>();
        TrafficData.trafficRoadMap = new HashMap<>();
        TrafficData.arrivedCar = new HashSet<>();
        TrafficData.drivingSet = new HashSet<>();
        TrafficData.presetCarMap = new HashMap<>();
        TrafficData.presetCarTimeMap = new HashMap<>();
        TrafficData.presetCarList = new LinkedList<>();
        TrafficData.lastTimeArrivedCarNum = 0;
        TrafficData.timeCount = 0;
        TrafficData.changedPresetCarNum = 0;
    }

    private static void inputTrafficData(String carPath, String roadPath, String crossPath, String presetCarPath) {
        //输入参数
        TrafficData.carMap = ImportData.importCarData(carPath);
        Map<Integer, Road> roadMap = ImportData.importRoadData(roadPath);
        Map<Integer, Cross> crossMap = ImportData.importCrossData(crossPath, roadMap);
        TrafficData.presetCarMap = ImportData.importPresetCarData(TrafficData.carMap, presetCarPath, roadMap);

        Map<String, TrafficRoad> trafficRoadMap = new HashMap<>();
        for (Integer roadKey : roadMap.keySet()) {
            String from = roadMap.get(roadKey).from.toString();
            String to = roadMap.get(roadKey).to.toString();
            trafficRoadMap.put(from + "_" + to, new TrafficRoad(roadMap.get(roadKey), from + "_" + to));
            if (roadMap.get(roadKey).isDuplex)
                trafficRoadMap.put(to + "_" + from, new TrafficRoad(roadMap.get(roadKey), to + "_" + from));
        }
        TrafficData.trafficRoadMap = new HashMap<>(trafficRoadMap);

        for (Integer crossKey : crossMap.keySet()) {
            TrafficData.trafficCrossMap.put(crossKey, new TrafficCross(crossMap.get(crossKey)));
        }
        roadMap.clear();
        crossMap.clear();
    }

    private static double[] initResultParam() {
        double[] res = new double[2];
        double[] resParams = new double[6];
        List<Car> priorityCar = new ArrayList<>();
        for (Car car : TrafficData.carMap.values())
            if (car.isPrioriry)
                priorityCar.add(car);

        int maxSpeed = Integer.MIN_VALUE, minSpeed = Integer.MAX_VALUE;
        int minStartTime = Integer.MAX_VALUE, maxStartTime = 0;
        Set<Integer> startPointSet = new HashSet<>();
        Set<Integer> endPointSet = new HashSet<>();
        for (Car car : TrafficData.carMap.values()) {
            maxSpeed = Math.max(car.speed, maxSpeed);
            minSpeed = Math.min(car.speed, minSpeed);
            minStartTime = Math.min(minStartTime, car.time);
            maxStartTime = Math.max(maxStartTime, car.time);
            startPointSet.add(car.from);
            endPointSet.add(car.to);
        }

        int priorityMaxSpeed = Integer.MIN_VALUE, priorityMinSpeed = Integer.MAX_VALUE;
        int priorityMinStartTime = Integer.MAX_VALUE, priorityMaxStartTime = 0;
        int priorityMinRealTime = Integer.MAX_VALUE, priorityMaxRealTime = Integer.MIN_VALUE;
        Set<Integer> priorityStartPointSet = new HashSet<>();
        Set<Integer> priorityEndPointSet = new HashSet<>();
        for (Car car : priorityCar) {
            priorityMaxSpeed = Math.max(priorityMaxSpeed, car.speed);
            priorityMinSpeed = Math.min(priorityMinSpeed, car.speed);
            priorityMaxStartTime = Math.max(priorityMaxStartTime, car.time);
            priorityMinStartTime = Math.min(priorityMinStartTime, car.time);
            priorityStartPointSet.add(car.from);
            priorityEndPointSet.add(car.to);
        }
        System.out.println("优先车辆预期最早发车时间: " + priorityMinStartTime);
        System.out.println("优先车辆预期最晚发车时间: " + priorityMaxStartTime);

        resParams[0] = (double) TrafficData.carMap.size() / (double) priorityCar.size() * 0.05;
        resParams[1] = (double) maxSpeed / (double) minSpeed / (double) priorityMaxSpeed * (double) priorityMinSpeed * 0.2375;
        resParams[2] = (double) maxStartTime / (double) minStartTime / (double) priorityMaxStartTime * (double) priorityMinStartTime * 0.2375;
        resParams[3] = (double) startPointSet.size() / (double) priorityStartPointSet.size() * 0.2375;
        resParams[4] = (double) endPointSet.size() / (double) priorityEndPointSet.size() * 0.2375;
        resParams[5] = (double) priorityMinStartTime;
        res[0] = resParams[0] + resParams[1] + resParams[2] + resParams[3] + resParams[4];
        res[1] = resParams[5];
        return res;
    }
}
