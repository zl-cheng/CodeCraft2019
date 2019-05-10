package com.huawei.struct;

import java.util.HashMap;
import java.util.Map;

/**
 * @author 程智凌
 * @date 2019/3/12 20:06
 */
public class IndexMinHeap {

    private int count;
    private int capacity;
    private int[][] data;
    private Map<Integer, Integer> reverse;

    private void shiftUp(int k){
        while(k > 1){
            if(data[k][1] < data[k / 2][1]){
                swap(data, k, k/2);
                reverse.put(data[k][0], k);
                reverse.put(data[k/2][0], k/2);
                k /= 2;
            }
            else break;
        }
    }

    private void shiftDown(int k){
        while(2*k <= count){
            int index = 2*k;
            if(index + 1 <= count && data[index + 1][1] < data[index][1])
                index ++;
            if(data[k][1] < data[index][1])
                break;
            swap(data, k, index);
            reverse.put(data[k][0], k);
            reverse.put(data[index][0], index);
            k = index;
        }
    }

//    public boolean contains(int i){
//        if(i + 1 >= i && i < capacity)
//            return reverse.containsKey(i);
//        else return false;
//    }

    private void swap(int[][] array, int pos1, int pos2){
        int[] temp = new int[]{array[pos1][0], array[pos1][1]};
        array[pos1] = array[pos2];
        array[pos2] = temp;
    }

    public IndexMinHeap(int capacity){
        count = 0;
        this.capacity = capacity;
        data = new int[capacity + 1][2];
        reverse = new HashMap<>(capacity + 1);
    }

    public void insert(int[] i){
        if(count >= capacity)
            return;
        count ++;
        data[count] = i;
        reverse.put(i[0], count);
        shiftUp(count);
    }

    public int[] poll(){
        if(count == 0)
            return null;
        int[] res = data[1];
        swap(data, 1, count);
        reverse.put(data[1][0], 1);
        reverse.put(data[count][0], count);
        count --;
        shiftDown(1);
        return res;
    }

    public int size(){
        return count;
    }

    public boolean isEmpty(){
        return count == 0;
    }

    public int[] getItem(int i){
        return data[i + 1];
    }

    public boolean contains(int id){
        return reverse.containsKey(id);
    }

    public void change(int i, int newItem){
        if(!contains(i))
            return;
        data[reverse.get(i)][1] = newItem;
        int j = reverse.get(i);
        shiftUp(j);
        shiftDown(j);
    }
}
