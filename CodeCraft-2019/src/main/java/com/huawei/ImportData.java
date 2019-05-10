package com.huawei;

import com.huawei.CONSTANT.TrafficData;
import com.huawei.domain.Car;
import com.huawei.domain.Cross;
import com.huawei.domain.Road;
import com.huawei.traffic.TrafficCar;
import com.huawei.traffic.TrafficCross;
import com.huawei.traffic.TrafficRoad;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

/**
 * @author 程智凌
 * @date 2019/3/8 16:13
 */
public class ImportData {
    public static Map<Integer, Car> importCarData(String path){
        Map<Integer, Car> map = new HashMap<>();
        try{
            FileReader reader = new FileReader(path);
            BufferedReader br = new BufferedReader(reader);
            String line = null;
            while((line = br.readLine()) != null){
                if(line.isEmpty() || line.startsWith("#"))
                    continue;
                line = line.replace(" ","");
                line = line.substring(1, line.length()-1);
                String[] items = line.split(",");
                Car car = new Car(line);
                map.put(Integer.valueOf(items[0]), car);
            }
            reader.close();
        }catch (Exception e){
            e.printStackTrace();
        }
        return map;
    }

    public static Map<Integer, Cross> importCrossData(String path, Map<Integer, Road> roadMap){
        Map<Integer, Cross> map = new HashMap<>();
        try{
            FileReader reader = new FileReader(path);
            BufferedReader br = new BufferedReader(reader);
            String line = null;
            while((line = br.readLine()) != null){
                if(line.isEmpty() || line.startsWith("#"))
                    continue;
                String[] items = line2Strings(line);
                map.put(Integer.valueOf(items[0]), new Cross(items, roadMap));
            }
            reader.close();
        }catch (Exception e){
            e.printStackTrace();
        }
        return map;
    }

    public static Map<Integer, Road> importRoadData(String path){
        Map<Integer, Road> map = new HashMap<>();
        try{
            FileReader reader = new FileReader(path);
            BufferedReader br = new BufferedReader(reader);
            String line = null;
            while((line = br.readLine()) != null){
                if(line.isEmpty() || line.startsWith("#"))
                    continue;
                String[] items = line2Strings(line);
                Road road = new Road(items);
                map.put(Integer.valueOf(items[0]), road);
            }
            reader.close();
        }catch (Exception e){
            e.printStackTrace();
        }
        return map;
    }

    public static Map<Integer, TrafficCar> importPresetCarData(Map<Integer, Car> carMap, String ansPath, Map<Integer, Road> roadMap){
        Map<Integer, TrafficCar> map = new HashMap<>();
        try{
            FileReader read = new FileReader(ansPath);
            BufferedReader br = new BufferedReader(read);
            String line = null;
            while((line = br.readLine()) != null){
                if(line.isEmpty() || line.startsWith("#"))
                    continue;
                String[] items = line2Strings(line);
                List<Integer> solution = new LinkedList<>();
                Integer id = Integer.valueOf(items[0]);
                //确定起点 (路口)
                solution.add(carMap.get(id).from);
                for(int i = 2; i < items.length - 1; i++){
                    solution.add(TrafficCross.getCross(roadMap.get(Integer.valueOf(items[i])),
                            roadMap.get(Integer.valueOf(items[i+1]))));
                }
                //确定终点(路口)
                solution.add(carMap.get(id).to);
                //添加实际发车时间属性
                 TrafficCar trafficCar = new TrafficCar(carMap.get(id), Integer.valueOf(items[1]));
                trafficCar.solution = solution;
                map.put(id, trafficCar);
            }
            read.close();
        }catch (Exception e){
            e.printStackTrace();
        }
        return map;
    }

    private static String[] line2Strings(String line){
        line = line.replace(" ","");
        line = line.substring(1, line.length() - 1);
        return line.split(",");
    }
}
