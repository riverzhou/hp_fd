#!/usr/bin/env python3

from time       import sleep
from traceback  import print_exc
from redis      import StrictRedis

redis_ip    = '192.168.1.90'
redis_port  = 6379
redis_pass  = 'river'
redis_defdb = 0

class redis_db():
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
                self.db = db if db != None else redis_defdb
                self.redis  = self.connect_redis()
                if self.redis == None : return None
                print('redis connect succeed')

        def get(self, key):
                return self.redis.lrange(key, 0, -1)

        def set(self, key, val):
                return self.redis.set(key, val)

        def clean(self, key):
                return self.redis.delete(key)

        def blk_get_one(self, key):
                return self.redis.blpop(key)[1]


class fd_redis():
        image_db    = 5
        image_key   = 'image_req'
        number_key  = 'number_ack'

        def __init__(self):
                self.redis = redis_db(self.image_db)

        def put_picture(self, sid, picture):
                info = ','.join(sid, picture)
                return self.redis.push(self.image_key, info)

        def get_number(self):
                info = self.redis.bpop(self.number_key)
                sid, number = info.split(',')
                return sid, number

        def write_picture(self, sid, picture):
                pass

        def read_number(self, sid):
                sleep(10)
                return '111111'


redis_worker = fd_redis()


