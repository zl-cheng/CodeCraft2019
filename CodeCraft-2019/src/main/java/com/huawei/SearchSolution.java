package com.huawei;

import com.huawei.CONSTANT.TrafficData;
import com.huawei.struct.IndexMinHeap;
import com.huawei.traffic.TrafficCar;
import com.huawei.traffic.TrafficCross;
import com.huawei.traffic.TrafficRoad;

import java.util.*;

/**
 * @author 程智凌
 * @date 2019/3/27 22:16
 */
public class SearchSolution {

    public static double getSolutionBlockRate(List<Integer> solution){
        double cost = 0.0, distance = 0.0;
        for(int i = 0; i < solution.size() - 1; i++){
            TrafficRoad road = TrafficData.trafficRoadMap.get(solution.get(i) + "_" + solution.get(i + 1));
            double crowdParam = ((double)road.carNum - (double)road.lastTimeLeaveCarNum
                    + road.willArrivedPresetCarNum * TrafficData.PRIORITY_CAR_PREDICT_SOLUTION_ADD)
                    / (double)(road.info.length * road.info.channel);
            int val = (int)((double)road.info.length / (double)road.info.speed
                    * (1.0 + TrafficData.CAR_NUM_PARAM * crowdParam)
                    * (1.0 - TrafficData.BLOCK_CHANNEL_PARAM * road.info.channel));
            if(road.isLock && (double)road.carNum  > TrafficData.BLOCK_PARAM * (double)road.info.length * (double)road.info.channel)
                val *= TrafficData.LOCK_AND_BLOCK_PARAM ;
            distance += ((double)road.info.length / (double)road.info.speed);
            cost += val;
        }
        return cost / distance;
    }

    public static void searchSolutionWithStaticInfo(TrafficCar car){
        //已经在去终点的最近的那条路上了
        if(car.road != null && car.solution.get(0).equals(car.info.to))
            return;
        //刚发车 还没上路
        if(car.road == null && car.solution.isEmpty())
            car.solution.add(car.info.from);

        TrafficCross startCross = TrafficData.trafficCrossMap.get(car.solution.get(0));
        int minCostCrossId = Integer.MIN_VALUE, minCostVal = Integer.MAX_VALUE;
        for(String roadId : startCross.outRoad){
            if(car.road != null && roadId.split("_")[1].equals(car.road.id.split("_")[0]))
                continue;
            TrafficRoad road = TrafficData.trafficRoadMap.get(roadId);
            TrafficCross nextCross = TrafficData.trafficCrossMap.get(Integer.valueOf(roadId.split("_")[1]));
            //检测出有调头
            Integer indexCross = car.info.to;
            boolean isDeadEnd = false;
            while(!indexCross.equals(nextCross.info.id)){
                Integer nextStep = nextCross.costfrom.get(indexCross);
                if(roadId.equals(indexCross + "_" + nextStep)){
                    isDeadEnd = true;
                    break;
                }
                indexCross = nextStep;
            }
            if(isDeadEnd){
                continue;
            }
            int val = (int)road.getRoadVal(car);
            val += nextCross.costTo.get(car.info.to);
            if(val < minCostVal){
                minCostCrossId = nextCross.info.id;
                minCostVal = val;
            }
        }
        //出现使用静态路径信息计算都是死胡同,只能实时计算
        if(minCostCrossId == Integer.MIN_VALUE){
            SearchSolution.searchSolution(car);
            return;
        }
        if(!startCross.costTo.containsKey(car.info.to))
            return ;

        List<Integer> solution = new ArrayList<>();
        int index = car.info.to;
        while(!startCross.costfrom.get(index).equals(car.solution.get(0))){
            solution.add(index);
            index = startCross.costfrom.get(index);
        }
        solution.add(index);
        solution.add(car.solution.get(0));
        Collections.reverse(solution);
        car.planSolution = new ArrayList<>(solution);
        car.solution = new ArrayList<>(solution);
    }

    public static void searchSolution(TrafficCar car){
        searchSolution(car, new HashSet<>());
    }

    public static void searchSolution(TrafficCar car, Set<String> noAllowedWalkRoad){
        //刚发车 还没上路
        if(car.road == null && car.solution.isEmpty())
            car.solution.add(car.info.from);
        //已经在去终点的最近的那条路上了
        if(car.solution.get(0).equals(car.info.to))
            return;

        Set<Integer> marked = new HashSet<>(TrafficData.trafficCrossMap.size());
        Map<Integer, Integer> distTo = new HashMap<>(TrafficData.trafficCrossMap.size());
        Map<Integer, Integer> from = new HashMap<>(TrafficData.trafficCrossMap.size());
        marked.add(TrafficData.trafficCrossMap.get(car.solution.get(0)).info.id);
        from.put(TrafficData.trafficCrossMap.get(car.solution.get(0)).info.id, null);
        distTo.put(TrafficData.trafficCrossMap.get(car.solution.get(0)).info.id, 0);
        IndexMinHeap indexMinHeap = new IndexMinHeap(TrafficData.trafficCrossMap.size());
        indexMinHeap.insert(new int[]{TrafficData.trafficCrossMap.get(car.solution.get(0)).info.id, 0});
        while(!indexMinHeap.isEmpty()){
            int[] item = indexMinHeap.poll();
            if(item[0] == car.info.to)
                break;
            marked.add(item[0]);
            TrafficCross cross = TrafficData.trafficCrossMap.get(item[0]);
            for(String roadId : cross.outRoad){
                if(roadId.split("_")[0].equals(cross.info.id.toString())){
                    Integer nextCross = Integer.valueOf(roadId.split("_")[1]);
                    if(car.road != null && nextCross.equals(Integer.valueOf(car.road.id.split("_")[0])))
                            continue;
                    if(noAllowedWalkRoad.contains(roadId))
                        continue;
                     if(!marked.contains(nextCross)){
                        TrafficRoad road =  TrafficData.trafficRoadMap.get(item[0] + "_" + nextCross);
                        int val = (int)road.getRoadVal(car);
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
        //不能到终点
        if(!distTo.containsKey(car.info.to))
            return ;
        List<Integer> solution = new ArrayList<>();
        int index = car.info.to;
        while(!from.get(index).equals(car.solution.get(0))){
            solution.add(index);
            index = from.get(index);
        }

        solution.add(index);
        solution.add(car.solution.get(0));
        Collections.reverse(solution);
        car.planSolution = new ArrayList<>(solution);
        car.solution = new ArrayList<>(solution);
    }

    public static void registRoadWillArrivedCarNum(TrafficCar car, int startTime){
        int timeCount = startTime;
        if(car.solution == null)
            return;
        for(int i = 0; i < car.solution.size() - 1; i++){
            TrafficRoad road = TrafficData.trafficRoadMap.get(car.solution.get(i) + "_" + car.solution.get(i + 1));
            int speedTime = road.info.length / Math.min(car.info.speed, road.info.speed);
            for(int j = 0; j <= speedTime && j + timeCount < 200; j++){
                road.willArrivedCarNum[j + timeCount] ++;
            }
            timeCount += speedTime;
        }
    }

    public static boolean isAllowedStart(List<Integer> solution, int speed){
        int timeCount = 0;
        for(int i = 0; i < solution.size() - 1; i++){
            TrafficRoad road = TrafficData.trafficRoadMap.get(solution.get(i) + "_" + solution.get(i + 1));
            int speedTime = road.info.length / Math.min(road.info.speed, speed);
            for(int j = 0; j <= speedTime && j + timeCount < 200; j++)
                if(road.willArrivedCarNum[j + timeCount] >= (int)(TrafficData.PREDICT_FUTURE_TIME_BLOCK_PARAM * (double)road.info.length * (double)road.info.channel))
                    return false;
            timeCount += speedTime;
        }
        return true;
    }

    public static boolean needChangeSolution(TrafficCar car){
        if(car.isLock)
            return false;
        for(int i = 0; i < car.solution.size() - 1 && i < TrafficData.CHANGE_SOLUTION_PREDICT_STEP; i ++){
            TrafficRoad road = TrafficData.trafficRoadMap.get(car.solution.get(i) + "_" + car.solution.get(i + 1));
            if((road.isWaited && !car.info.isPrioriry)
                    || road.isWaiting
                    || (road.isLock && road.carNum - road.lastTimeLeaveCarNum >= (int)(TrafficData.BLOCK_PARAM * (double)road.info.length * (double)road.info.channel))){
                if(car.info.isPreset){
                    if(TrafficData.changedPresetCarNum < (int)(TrafficData.BLOCKING_CHANGE_PRESET_CAR_RATE * (double)TrafficData.presetCarMap.size() * TrafficData.CHANGE_PRESET_MAX_CAR_RATE)){
                        car.info.isPreset = false;
                        TrafficData.changedPresetCarNum ++;
//                        System.out.println("blocking! Change preset car solution! Now changed preset car num is " + TrafficData.changedPresetCarNum);
                        return true;
                    }else
                        return false;
                }
                return true;
            }
        }
        return false;
    }

    public static int getSolutionDistance(List<Integer> solution){
        int distance = 0;
        for(int i = 0; i < solution.size() - 1; i ++){
            distance += TrafficData.trafficRoadMap.get(solution.get(i) + "_" + solution.get(i + 1)).info.length;
        }
        return distance;
    }
}
