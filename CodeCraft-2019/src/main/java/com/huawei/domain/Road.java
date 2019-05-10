package com.huawei.domain;

/**
 * @author 程智凌
 * @date 2019/3/9 14:37
 */
public class Road {
    public Integer id;   //id
    public int length;  //道路长度
    public int speed;   //最高限速
    public int channel; //车道数目
    public Integer from; //起始点（路口）id
    public Integer to;   //终点（路口）id
    public boolean isDuplex;    //是否双向

//    public Road(int id, int length, int speed, int channel, int from, int to, boolean isDuplex) {
//        this.id = id;
//        this.length = length;
//        this.speed = speed;
//        this.channel = channel;
//        this.from = from;
//        this.to = to;
//        this.isDuplex = isDuplex;
//    }

    public Road(String[] strs) {
//        String[] strs = line.split(",");
        this.id = Integer.valueOf(strs[0]);
        this.length = Integer.valueOf(strs[1]);
        this.speed = Integer.valueOf(strs[2]);
        this.channel = Integer.valueOf(strs[3]);
        this.from = Integer.valueOf(strs[4]);
        this.to = Integer.valueOf(strs[5]);
        this.isDuplex = Integer.valueOf(strs[6]) == 1;
    }
}
