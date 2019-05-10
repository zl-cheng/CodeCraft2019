package com.huawei.enums;

/**
 * @author 程智凌
 * @date 2019/3/9 15:40
 */
public enum DirEnum {
    LEFT(2),
    RIGHT(1),
    STRAIGHT(3);

    public int val;
    DirEnum(int val){
        this.val = val;
    }
}
