#!/usr/bin/env python3

from time                   import sleep
from traceback              import print_exc, format_exc
from redis                  import StrictRedis
from threading              import Event, Lock
from queue                  import Queue

from pp_baseclass           import pp_thread
from fd_config              import redis_passwd, redis_port, redis_ip

from pp_log                 import logger, printer

#------------------------------------------

class redis_db():
        global redis_ip, redis_port, redis_pass
        ip      = redis_ip
        port    = redis_port
        passwd  = redis_passwd
        default_db = 0

        def __init__(self, db = None, info = ''):
                self.info   = info
                self.db     = db if db != None else self.default_db
                self.redis  = self.connect_redis()
                if self.redis == None : return None
                printer.debug('redis %s connect succeed' % self.info)

        def connect_redis(self):
                try:
                        return StrictRedis(host = self.ip, port = self.port, password = self.passwd, db = self.db)
                except  KeyboardInterrupt:
                        return None
                except:
                        printer.critical(format_exc())
                        return None

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
                        printer.critical(format_exc())
                return ret

        def get_one(self, key):
                return self.redis.lpop(key)[1]

        def put_one(self, key, val):
                return self.redis.rpush(key, val)

#===================================================

if __name__ == '__main__':
        redis   = redis_db()
        sleep(3)

