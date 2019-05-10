package com.huawei.domain;

/**
 * @author 程智凌
 * @date 2019/3/9 14:40
 */
public class Car {
    public Integer id;   //id
    public Integer from; //起始点（路口）id
    public Integer to;   //终点（路口）id
    public int speed;   //最高速度
    public int time;    //出发时间
    public boolean isPreset;
    public boolean isPrioriry;

//    public Car(int id, int from, int to, int speed, int time) {
//        this.id = id;
//        this.from = from;
//        this.to = to;
//        this.speed = speed;
//        this.time = time;
//    }

    public Car(String line){
        String[] strs = line.split(",");
        this.id = Integer.valueOf(strs[0]);
        this.from = Integer.valueOf(strs[1]);
        this.to = Integer.valueOf(strs[2]);
        this.speed = Integer.valueOf(strs[3]);
        this.time = Integer.valueOf(strs[4]);
        this.isPrioriry = Integer.valueOf(strs[5]) == 1;
        this.isPreset = Integer.valueOf(strs[6]) == 1;
    }
}
