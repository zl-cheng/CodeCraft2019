package com.huawei.traffic;

import com.huawei.CONSTANT.TrafficData;
import com.huawei.domain.Car;
import com.huawei.domain.Cross;
import com.huawei.domain.Road;
import com.huawei.enums.DirEnum;
import com.huawei.enums.StatusEnum;
import com.huawei.struct.IndexMinHeap;

import java.util.*;

/**
 * @author 程智凌
 * @date 2019/3/9 15:54
 */
public class TrafficCross {
    public Cross info;
    public Map<String, Integer> map;
    public PriorityQueue<Integer> waitStartCarQueue;
    public List<Integer> waitStartCar;
    public List<Integer> priorityCarWaitStartList;
    public List<Integer> waitStartCarB;
    public List<Integer> priorityCarWaitStartListB;
    public List<Integer> nextStep;

    public List<String> inRoad;
    public List<String> outRoad;
    public Map<Integer, Integer> distanceMapWithSpeed;
    public Map<Integer, Integer> distanceMap;

    public Map<Integer, Integer> costTo;
    public Map<Integer, Integer> costfrom;

    public int[] point = new int[2];

    private static int[][] dir = new int[][]{{-1, 0}, {0, 1}, {1, 0}, {0, -1}};

    public TrafficCross(Cross info) {
        this.info = info;
        map = new HashMap<>();
        waitStartCarQueue = new PriorityQueue<>(startCarComparator);
        waitStartCar = new LinkedList<>();
        waitStartCarB = new LinkedList<>();
        priorityCarWaitStartList = new LinkedList<>();
        priorityCarWaitStartListB = new LinkedList<>();
        nextStep = new LinkedList<>();
        costTo = new HashMap<>(TrafficData.trafficCrossMap.size());
        costfrom = new HashMap<>(TrafficData.trafficCrossMap.size());

        inRoad = new LinkedList<>();
        outRoad = new LinkedList<>();
        distanceMapWithSpeed = new HashMap<>();
        distanceMap = new HashMap<>();

        for(int i = 0; i < info.rIds.size(); i++){
            if(info.rIds.get(i) == null)
                continue;
            if(info.rIds.get(i).isDuplex) {
                map.put(info.rIds.get(i).to + "_" + info.rIds.get(i).from, i);
            }
            map.put(info.rIds.get(i).from + "_" + info.rIds.get(i).to, i);
        }
        for(String roadId : map.keySet()){
            //道路为进入方向
            if(roadId.split("_")[1].equals(info.id + ""))
                inRoad.add(roadId);
            else outRoad.add(roadId);
        }
    }

    //车抵达目的地
    public static void arrive(TrafficCar car){
        TrafficData.arrivedCar.add(car.info.id);
        car.road.queues.get(car.channel).remove(car);
        car.isArrived = true;
        car.solutionBackUp.add(car.solution.get(0));
    }

    public static Integer getCross(Road road1, Road road2){
        if(road1.from.equals(road2.to) || road1.from.equals(road2.from))
            return road1.from;
        else
            return road1.to;
    }

    public DirEnum getDir(String roadId ,Integer from, Integer to){
        String r1 = roadId;
        String r2 = this.info.id + "_" + to;
        switch (((map.get(roadId) -  map.get(r2)) +4) % 4){
            case 3:
                return DirEnum.LEFT;
            case 2:
                return DirEnum.STRAIGHT;
            case 1:
                return DirEnum.RIGHT;
            default:
                return DirEnum.STRAIGHT;
        }
    }

    public void saveDistanceWithSpeed(){
        int size = TrafficData.trafficCrossMap.size();
        Set<Integer> marked = new HashSet<>(size);
        Map<Integer, Integer> from = new HashMap<>(size);

        marked.add(TrafficData.trafficCrossMap.get(info.id).info.id);
        from.put(TrafficData.trafficCrossMap.get(info.id).info.id, null);
        distanceMapWithSpeed.put(TrafficData.trafficCrossMap.get(info.id).info.id, 0);
        IndexMinHeap indexMinHeap = new IndexMinHeap(size);
        indexMinHeap.insert(new int[]{TrafficData.trafficCrossMap.get(info.id).info.id, 0});
        while(!indexMinHeap.isEmpty()){
            int[] item = indexMinHeap.poll();
            marked.add(item[0]);
            TrafficCross cross = TrafficData.trafficCrossMap.get(item[0]);
            //通用道路
            for(String road : cross.outRoad){
                TrafficCross nextCross = TrafficData.trafficCrossMap.get(Integer.valueOf(road.split("_")[1]));
                if(!marked.contains(nextCross.info.id)){
                    int distance = TrafficData.trafficRoadMap.get(road).info.length / TrafficData.trafficRoadMap.get(road).info.speed + item[1];
                    if(!from.containsKey(nextCross.info.id) || distance < distanceMapWithSpeed.get(nextCross.info.id)){
                        distanceMapWithSpeed.put(nextCross.info.id, distance);
                        from.put(nextCross.info.id, item[0]);
                        if(indexMinHeap.contains(nextCross.info.id))
                            indexMinHeap.change(nextCross.info.id, distance);
                        else
                            indexMinHeap.insert(new int[]{nextCross.info.id, distance} );
                    }
                }
            }
        }
    }

    public void saveDistance(){
        int size = TrafficData.trafficCrossMap.size();
        Set<Integer> marked = new HashSet<>(size);
        Map<Integer, Integer> from = new HashMap<>(size);

        marked.add(info.id);
        from.put(info.id, null);
        distanceMap.put(info.id, 0);
        IndexMinHeap indexMinHeap = new IndexMinHeap(size);
        indexMinHeap.insert(new int[]{info.id, 0});
        while(!indexMinHeap.isEmpty()){
            int[] item = indexMinHeap.poll();
            marked.add(item[0]);
            TrafficCross cross = TrafficData.trafficCrossMap.get(item[0]);
            //通用道路
            for(String road : cross.outRoad){
                TrafficCross nextCross = TrafficData.trafficCrossMap.get(Integer.valueOf(road.split("_")[1]));
                if(!marked.contains(nextCross.info.id)){
                    int distance = TrafficData.trafficRoadMap.get(road).info.length + item[1];
                    if(!from.containsKey(nextCross.info.id) || distance < distanceMap.get(nextCross.info.id)){
                        distanceMap.put(nextCross.info.id, distance);
                        from.put(nextCross.info.id, item[0]);
                        if(indexMinHeap.contains(nextCross.info.id))
                            indexMinHeap.change(nextCross.info.id, distance);
                        else
                            indexMinHeap.insert(new int[]{nextCross.info.id, distance} );
                    }
                }
            }
        }
    }

    public void updateCrossCostMap(){
        Set<Integer> marked = new HashSet<>(TrafficData.trafficCrossMap.size());
        Map<Integer, Integer> distTo = new HashMap<>(TrafficData.trafficCrossMap.size());
        Map<Integer, Integer> from = new HashMap<>(TrafficData.trafficCrossMap.size());
        marked.add(info.id);
        from.put(info.id, null);
        distTo.put(info.id, 0);
        IndexMinHeap indexMinHeap = new IndexMinHeap(TrafficData.trafficCrossMap.size());
        indexMinHeap.insert(new int[]{info.id, 0});
        while(!indexMinHeap.isEmpty()){
            int[] item = indexMinHeap.poll();
            marked.add(item[0]);
            TrafficCross cross = TrafficData.trafficCrossMap.get(item[0]);
            for(String roadId : cross.map.keySet()){
                if(roadId.split("_")[0].equals(cross.info.id.toString())){
                    Integer nextCross = Integer.valueOf(roadId.split("_")[1]);
                    if(!marked.contains(nextCross)){
                        TrafficRoad road =  TrafficData.trafficRoadMap.get(item[0] + "_" + nextCross);

                        double crowdParam = ((double)road.carNum
                                - TrafficData.FLOW_NUM_PARAM *  (double)road.lastTimeLeaveCarNum
                                + (double)road.willArrivedNormalCarNum * TrafficData.NORMAL_CAR_PREDICT_SOLUTION_ADD
                                + (double)road.willArrivedPresetCarNum * TrafficData.PRESET_CAR_PREDICT_SOLUTION_ADD
                                + (double)road.willArrivedPrirotyCarNum * TrafficData.PRIORITY_CAR_PREDICT_SOLUTION_ADD
                                )/ (double)(road.info.length * road.info.channel);
                        crowdParam = crowdParam < 0 ? 0 : crowdParam;
                        int val = (int)((double)road.info.length / (double)road.info.speed
                                * (1.0 + TrafficData.CAR_NUM_PARAM * crowdParam)
                                * (1.0 - TrafficData.BLOCK_CHANNEL_PARAM * road.info.channel));
                        if(road.isLock && (double)road.carNum > TrafficData.BLOCK_PARAM * (double)road.info.length * (double)road.info.channel)
                            val = (int)(TrafficData.LOCK_AND_BLOCK_PARAM * (double)val);
                        val += item[1];
                        if(!from.containsKey(nextCross) || val < distTo.get(nextCross)){
                            distTo.put(nextCross, val);
                            from.put(nextCross, item[0]);
                            if(indexMinHeap.contains(nextCross))
                                indexMinHeap.change(nextCross, val);
                            else
                                indexMinHeap.insert(new int[]{nextCross, val} );
                        }
                    }
                }
            }
        }
        costfrom.clear();
        costTo.clear();
        costTo.putAll(distTo);
        costfrom.putAll(from);
    }

    //十字调度
    public int crossPriority(Map<String, TrafficRoad> roadMap){
        //从小到大排序
        Collections.sort(inRoad, (i1, i2)->{
            return roadMap.get(i1).info.id - roadMap.get(i2).info.id;
        });

        for(String roadId : inRoad){
            TrafficRoad road = roadMap.get(roadId);
            road.updateDispatchPriority();
            if(road.priorityQueue.isEmpty())
                continue;
            TrafficCar car = road.priorityQueue.peek();
            if(car.status == StatusEnum.INROAD){
                if(car.nextRoadId == null)
                    continue;
                if(!roadMap.get(car.nextRoadId).in.contains(car))
                    roadMap.get(car.nextRoadId).in.add(car);
            }
        }

        int dispatchNum = 0;
        for(String roadId : inRoad){
            dispatchNum += roadMap.get(roadId).dispatch();
        }
        return dispatchNum;
    }

    public void update(){
        waitStartCarB = new LinkedList<>(waitStartCar);
        priorityCarWaitStartListB = new LinkedList<>(priorityCarWaitStartList);
    }

    public void backUp(){
        waitStartCar = new LinkedList<>(waitStartCarB);
        priorityCarWaitStartList = new LinkedList<>(priorityCarWaitStartListB);
    }

    public static String getStraightRoad(TrafficRoad road){
        TrafficCross center = TrafficData.trafficCrossMap.get(Integer.valueOf(road.id.split("_")[1]));
        int dir = center.map.get(road.id);
        for(String roadId : center.outRoad){
            if(Math.abs(center.map.get(roadId) - dir) == 2)
                return roadId;
        }
        return null;
    }

    public static void createCrossCoordinate(){
        TrafficCross startCross = null;
        Set<Integer> arrived = new HashSet<>(TrafficData.trafficCrossMap.size());

        //找个起点
        for(TrafficCross cross : TrafficData.trafficCrossMap.values()){
            if(cross.outRoad.size() == 4){
                startCross = cross;
                break;
            }
        }
        startCross.point = new int[]{0, 0};
        arrived.add(startCross.info.id);
        //
        for(String roadId : startCross.outRoad){
            TrafficCross cross = TrafficData.trafficCrossMap.get(Integer.valueOf(roadId.split("_")[1]));
            cross.point = dir[startCross.map.get(roadId)];
            if(arrived.contains(cross.info.id))
                continue;
            createCrossRecursion(cross, startCross, arrived);
            arrived.add(cross.info.id);
        }
    }

    private static void createCrossRecursion(TrafficCross startCross, TrafficCross preCross, Set<Integer> arrived){
        int preCrossDirIndex = startCross.map.get(preCross.info.id + "_" + startCross.info.id);
        int[] preCrossMove = new int[]{preCross.point[0] - startCross.point[0], preCross.point[1] - startCross.point[1]};
        int dirIndex = 0;
        for(; dirIndex < 4; dirIndex ++)
            if(preCrossMove[0] == dir[dirIndex][0] && preCrossMove[1] == dir[dirIndex][1])
                break;
        for(String roadId : startCross.outRoad){
            TrafficCross cross = TrafficData.trafficCrossMap.get(Integer.valueOf(roadId.split("_")[1]));
            if(arrived.contains(cross.info.id))
                continue;
            int[] move = dir[((startCross.map.get(roadId) - preCrossDirIndex + 4) % 4 + dirIndex) % 4];
            cross.point[0] = startCross.point[0] + move[0];
            cross.point[1] = startCross.point[1] + move[1];
            arrived.add(cross.info.id);
            createCrossRecursion(cross, startCross, arrived);
        }
    }

    private static Comparator<Integer> startCarComparator = new Comparator<Integer>() {
        @Override
        public int compare(Integer i1, Integer i2) {
            Car car1 = TrafficData.trafficCarMap.get(i1).info;
            Car car2 = TrafficData.trafficCarMap.get(i2).info;
            if(car1.speed != car2.speed)
                return car2.speed - car1.speed;
            return car1.id - car2.id;
        }
    };
}
