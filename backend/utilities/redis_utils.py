import time
import uuid
import redis
from threading import Thread
import pickle
import functools
import hashlib
import base64
from utilities.print_utils import logger
from config import REDIS_ENDPOINT
#REDIS_ENDPOINT = "127.0.0.1"


class GlobalLockPool:
    """
    全局线程锁 ,并发锁
    conn:redis connect
    key:redis key （设置为随机值获取并发锁）
    lock_num: 锁的数量用于控制并发,如果为1  则是代表普通全局线程锁
    """
    def __init__(self, conn,key,lock_num = 0,max_expire_time = 5):
        self.conn = conn
        hash_key = hashlib.sha256(pickle.dumps(key)).hexdigest()
        if lock_num > 1 :
            self.key = "global_lock" +str( hash('global_lock' + str(key)) % lock_num)
        else:
            self.key = "global_lock" + hash_key
        self.max_expire_time = max_expire_time
    def acquire(self):
        try:
            self.conn.expire(self.key,self.max_expire_time)
        except:
            pass
        while True:
            try:
                if self.conn.setnx(self.key,'1'):
                    break
            except Exception as e:
                print(e)
                time.sleep(0.1)
            time.sleep(0.1)
        self.conn.expire(self.key,self.max_expire_time)
        return 
    
    def acquire_unblock(self):
        try:
            if self.conn.setnx(self.key,'1'):
                self.conn.expire(self.key,self.max_expire_time)
                return True
        except Exception as e:
            logger.error(e)
            return False

    def release(self):
        self.conn.delete(self.key)
        return


def exec_test(thread_name):
    lock = GlobalLockPool(conn1,thread_name,lock_num=20)
    lock.acquire()
    print(f'{thread_name}获取 redis 分布式锁成功！{lock.key}')
    time.sleep(1)
    lock.release()
    print(f'{thread_name} 释放')


def cache(func):
    #redis 缓存 openai client 结果 增加全局线程锁
    @functools.wraps(func)
    def wrapper(client,rid, *args, **kwargs):
        key = pickle.dumps((func.__name__,rid, args, kwargs))
        hash_key = hashlib.sha256(key).hexdigest()
        lock = GlobalLockPool(redis_conn,hash_key,lock_num = 0,max_expire_time=60*3)
        lock.acquire()
        result = redis_conn.get(hash_key)
        if result is None:
            result = func(client,rid, *args, **kwargs)
            encoded_result = base64.b64encode(pickle.dumps(result)).decode('utf-8')
            redis_conn.set(hash_key, encoded_result, ex=3600*3)
            lock.release()
            return result, False
        else:
            lock.release()
            decoded_result = base64.b64decode(result)
            return pickle.loads(decoded_result), True

    return wrapper


def exec_unblock_test(thread_name):
    if lock.acquire_unblock():
        print(f'{thread_name}获取 redis 分布式锁成功！')
        time.sleep(1)   
        #lock.release()
        #print(f'{thread_name} 释放')
    else:
        time.sleep(1) 
        print(f'{thread_name}获取失败！')


def test_client(x):
    time.sleep(1)
    return x


@cache
def test_cache(client,*args, **kwargs):
    return client(*args, **kwargs)


def test_func(i):
    res,use_cache = test_cache(test_client,i)
    print(res,use_cache)


# 用于线程锁
redis_conn = redis.Redis(host=REDIS_ENDPOINT, port=6379, decode_responses=True, db=0)
workflow_redis_conn = redis.Redis(host=REDIS_ENDPOINT, port=6379, decode_responses=True, db=1)

if __name__ == '__main__':
    conn1 = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True, db=0)
    conn1.set('test',1)
    conn1.expire('test',100)
    lock = GlobalLockPool(conn1,'test')
    # for i in range(100):
    #     t_name = f'thread_{i}'
    #     t = Thread(target=exec_test, args=(t_name,))
    #     t.start()
    for i in range(100):
        t_name = f'thread_{i%2}'
        time.sleep(0.5)
        t = Thread(target=test_func, args=(t_name,))
        t.start()
    # from concurrent.futures import ThreadPoolExecutor
    # lock = GlobalLockPool(conn1, 'test', max_expire_time=1)
    # with ThreadPoolExecutor(max_workers=3) as executor:
    #     for i in range(10):
    #         t_name = f'thread_{i}'
    #         executor.submit(exec_unblock_test, t_name)
    # lock = GlobalLockPool(conn1,'test',max_expire_time=3)
    # for i in range(10):
    #     t_name = f'thread_{i}'
    #     t = Thread(target=exec_unblock_test, args=(t_name,))
    #     t.start()
