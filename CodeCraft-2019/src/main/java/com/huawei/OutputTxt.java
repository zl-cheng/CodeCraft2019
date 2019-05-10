package com.huawei;

import com.huawei.CONSTANT.TrafficData;
import com.huawei.domain.Car;
import com.huawei.traffic.TrafficCar;
import com.huawei.traffic.TrafficCross;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

/**
 * @author 程智凌
 * @date 2019/3/14 23:04
 */
public class OutputTxt {
    public static void output(Map<Integer, TrafficCar> carMap, String ansPath) throws IOException {
        File file = new File(ansPath);
        BufferedWriter wr = new BufferedWriter(new FileWriter(file));
        for(TrafficCar car : carMap.values()){
            //(1006, 1, 513, 517, 521, 510, 511, 512)
            StringBuffer buffer = new StringBuffer();
            buffer.append("(" + car.info.id + "," + car.starTime);
            Iterator<Integer> iterator = car.solutionBackUp.iterator();
            TrafficCross pre = TrafficData.trafficCrossMap.get(iterator.next());
            while(iterator.hasNext()){
                TrafficCross index = TrafficData.trafficCrossMap.get(iterator.next());
                buffer.append("," + TrafficData.trafficRoadMap.get(pre.info.id + "_" + index.info.id).info.id);
                pre = index;
            }
            buffer.append(")\n");
            wr.write(buffer.toString());
        }
        wr.close();
    }
}
