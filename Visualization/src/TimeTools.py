# -*- coding: utf-8 -*-
"""
@Created: Sun Feb 10 22:12:34 2019

@Author: And-ZJ

@Content:

    函数 runTime: 装饰器，显示函数运行时间，可废弃
    
    类 RunTime: 拥有两个装饰器的类。一个直接显示函数运行时间，另一个则记录函数运行时间。
    
@Edited:    
    
    2.0: 改用类实现
    
"""

#%% runTime
import time
from functools import wraps

def runTime(function):
    """
        可废弃
        装饰器，显示函数运行时间，简易版本，功能同 RunTimel.show()
    """
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        useTime = t1 - t0
        if (useTime < 60):
            print(" '%s.%s' Running Time : %f secs" %(function.__module__, function.__name__,useTime))
        else:
            print(" '%s.%s' Running Time : %f mins" %(function.__module__, function.__name__,useTime/60))
        return result
    return function_timer

#%% RunTime
from collections import defaultdict
class RunTime:
    
    @staticmethod
    def show(moduleName:bool=False):
        """
            装饰器，显示函数运行时间
        Parameters
        ----------
        moduleName : bool, optional
            打印内容是否含有模块名. The default is False.
            False: 自动用模块名和函数名做 key ，若模块名是 __main__ ，则只有函数名做 key.
            True: 则会显示 __main__ 模块的名字，而其他模块名是默认就显示的
        Returns
        -------
        function
            装饰器.

        """
        def wrapper(function):
            @wraps(function)
            def display(*args,**kwargs):
                st = time.time()
                result = function(*args, **kwargs)
                et = time.time()
                ut = et - st
                if moduleName or function.__module__ != '__main__':
                    name = "{0}.{1}".format(function.__module__,function.__name__)
                else:
                    name = "{0}".format(function.__name__)
                s = "RunTime.show: '{0}()' -> {1:0.3f} secs".format(name,ut)
                print(s)
                return result
            return display
        return wrapper
    
    
    RECORD = defaultdict(lambda :0)
    @staticmethod
    def init():
        """
        清除时间累计，清除通过 total 统计的运行时间。
        Returns
        -------
        None.

        """
        RunTime.RECORD = defaultdict(lambda :0)
    
    @staticmethod
    def total(key:[int,str]=None,moduleName:bool=False):
        """
        装饰器，记录函数运行时间，如果一个函数会多次调用，要看总运行时间，则用此装饰器记录较为方便。

        Parameters
        ----------
        key : 运行时间记录在哪个键里 [int,str], optional
            不填则自动生成 key . The default is None.
            自动生成 key 规则，自动用模块名和函数名做 key ，若模块名是 __main__ ，则只有函数名做 key
        moduleName : bool, optional
            显示模块名. The default is False.
            若为 True，则会显示 __main__ 模块的名字，而其他模块名是默认就显示的
        Returns
        -------
        function
            装饰器.

        """
        def wrapper(function):
            @wraps(function)
            def recorder(*args,**kwargs):
                st = time.time()
                result = function(*args, **kwargs)
                et = time.time()
                ut = et - st
                name = key
                """
                此处不能赋值给 key，否则会报 key 不存在。
                例如这种用法：
                key = key
                或者这种：
                name = key
                key = name
                都是错的.
                错误原因，python的闭包原则。
                参考链接：https://www.cnblogs.com/JohnABC/p/4076855.html
                """
                if name is None:
                    if moduleName or function.__module__ != '__main__':
                        name = "{0}.{1}".format(function.__module__,function.__name__)
                    else:
                        name = "{0}".format(function.__name__)
                RunTime.RECORD[name] += ut
                return result
            return recorder
        return wrapper

    @staticmethod
    def getTotalTime(key):
        return RunTime.RECORD[key]        
    
    @staticmethod
    def list():
        print('RunTime list: {0} records.'.format(len(RunTime.RECORD)))
        # 按字母顺序打印
        sortedKey = sorted(list(RunTime.RECORD.keys()))
        for key in sortedKey:
            value = RunTime.RECORD[key]
        # for key,value in RunTime.RECORD.items():
            print("'{0}()' -> {1:0.3f} secs".format(key,value))

RunTime.init()

#%%
if __name__ == '__main__':
    

    ### example:
    
    from TimeTools import RunTime
    RunTime.init()
    
    @RunTime.show()
    def a():
        time.sleep(0.05)
    
    @RunTime.show(moduleName=True)
    def b():
        time.sleep(0.1)

    @RunTime.total()
    def c():
        time.sleep(0.2)
    
    @RunTime.total()
    def d():
        time.sleep(0.3)
        
    a()    
    b()
    b()
    a()
    c()
    d()
    c()
    RunTime.list()
    
    ### exmaple output:
    """
    RunTime.show: 'a()' -> 0.051 secs
    RunTime.show: '__main__.b()' -> 0.101 secs
    RunTime.show: '__main__.b()' -> 0.101 secs
    RunTime.show: 'a()' -> 0.051 secs
    RunTime list: 2 records.
    'd()' -> 0.301 secs
    'c()' -> 0.401 secs
    """

    pass



