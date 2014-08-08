#!/usr/bin/env python3


class redis_db():
        global  pp_config
        ip      = pp_config['redis_ip']
        port    = pp_config['redis_port']
        passwd  = pp_config['redis_pass']

        def connect_redis(self):
                try:
                        return StrictRedis(host = self.ip, port = self.port, password = self.passwd, db = self.db)
                except:
                        print_exc()
                        return None

        def __init__(self, db = None):
                self.db     = db if db != None else pp_config['redis_db']
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
        def __init__(self):
                pass


        def write_picture(self, sid, picture):
                pass


        def read_number(self, sid):
                pass

redis_worker = fd_redis()


