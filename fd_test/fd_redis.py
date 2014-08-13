#!/usr/bin/env python3

from time           import sleep
from traceback      import print_exc
from redis          import StrictRedis
from threading      import Event, Lock
from queue          import Queue

from pp_baseclass   import pp_thread

redis_ip            = '192.168.1.90'
redis_port          = 6379
redis_pass          = 'river'
redis_default_db    = 0

class redis_db():
        global redis_ip, redis_port, redis_pass
        ip      = redis_ip
        port    = redis_port
        passwd  = redis_pass

        def connect_redis(self):
                try:
                        return StrictRedis(host = self.ip, port = self.port, password = self.passwd, db = self.db)
                except  KeyboardInterrupt:
                        return None
                except:
                        print_exc()
                        return None

        def __init__(self, db = None):
                global redis_default_db
                self.db = db if db != None else redis_default_db
                self.redis  = self.connect_redis()
                if self.redis == None : return None
                print('redis connect succeed')

        def get_list(self, key):
                return self.redis.lrange(key, 0, -1)

        def get(self, key):
                return self.redis.get(key)

        def set(self, key, val):
                return self.redis.set(key, val)

        def clean(self, key):
                return self.redis.delete(key)

        def blk_get_one(self, key, timeout = 0):
                ret = None
                try:
                        ret = self.redis.blpop(key, timeout)[1]
                except  KeyboardInterrupt:
                        pass
                except:
                        print_exc()
                return ret

        def get_one(self, key):
                return self.redis.lpop(key)[1]

        def put_one(self, key, val):
                print('redis_db put_one', key, val)
                return self.redis.rpush(key, val)

