package com.huawei.domain;

import com.huawei.enums.DirEnum;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @author 程智凌
 * @date 2019/3/9 14:42
 */
public class Cross {
    public Integer id;
    public List<Road> rIds = new ArrayList<>();    //顺时针方向 道路id

//    public Cross(int id, int rId0, int rId1, int rId2, int rId3) {
//        this.id = id;
//        this.rId0 = rId0;
//        this.rId1 = rId1;
//        this.rId2 = rId2;
//        this.rId3 = rId3;
//    }

    public Cross(String[] strs, Map<Integer, Road> roadMap) {
//        String[] strs = line.split(",");
        this.id = Integer.valueOf(strs[0]);
        for(int i = 0; i < 4; i++){
            if(Integer.valueOf(strs[i+1]) == -1)
                rIds.add(null);
            else
                rIds.add(roadMap.get(Integer.valueOf(strs[1+i])));
//            map.put(rIds[i], i);
//            map.put(Integer.valueOf(strs[1+i]), i);
        }
    }
}
