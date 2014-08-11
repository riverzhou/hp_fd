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
                return self.redis.rpush(key, val)


class fd_redis_reader(pp_thread):
        key_number = 'ack_number'

        def __init__(self, manager, db):
                super().__init__()
                self.manager = manager
                self.db = db
                self.redis = redis_db(self.db)

        def main(self):
                while True:
                        val = self.read()
                        if val == None:
                                sleep(0)
                                continue
                        self.manager.put_number(val)

        def read(self):
                return self.redis.blk_get_one(self.key_number)


class fd_redis_writer(pp_thread):
        key_image = 'req_image'

        def __init__(self, manager, db):
                super().__init__()
                self.manager = manager
                self.db = db
                self.redis = redis_db(self.db)

        def main(self):
                while True:
                        val = self.manager.get_image()
                        if val == None:
                                sleep(0)
                                continue
                        self.write(val)

        def write(self, val):
                return self.redis.put_one(self.key_image, val)


class fd_dama_result():
        def __init__(self):
                self.event  = Event()
                self.number = None

        def put_number(self, number):
                self.number = number
                self.event.set()

        def get_number(self):
                self.event.wait()
                #self.event.wait(10)
                #self.number = '111111'
                print('fd_dama_result get_number', self.number)
                return self.number


class fd_redis_manager(pp_thread):
        image_db    = 5
        image_key   = 'image_req'
        number_key  = 'number_ack'

        def __init__(self):
                super().__init__()
                self.queue_image    = Queue()
                self.queue_number   = Queue()

                reader = fd_redis_reader(self, self.image_db)
                writer = fd_redis_writer(self, self.image_db)

                writer.start()
                writer.wait_for_start()

                reader.start()
                reader.wait_for_start()

                self.dict_result = {}
                self.lock_result = Lock()

        def main(self):
                while True:
                        sid, number = self.get_number()
                        if sid == None or number == None:
                                sleep(0)
                                continue
                        if sid not in self.dict_result:
                                continue
                        self.dict_result[sid].put_number(number)

        def get_image(self):
                ret = None
                try:
                        ret = self.queue_image.get()
                except  KeyboardInterrupt:
                        pass
                except:
                        print_exc()
                return  ret

        def put_number(self, val):
                return  self.queue_number.put(val)

        def get_result(self, sid):
                print('get_result sid', sid)
                if sid not in self.dict_result:
                        return None
                return  self.dict_result[sid].get_number()

        def put_request(self, sid, image):
                print('put_request sid', sid)
                self.lock_result.acquire()
                if sid not in self.dict_result:
                        self.dict_result[sid] = fd_dama_result()
                self.lock_result.release()
                val = ','.join([sid, image])
                return  self.queue_image.put(val)

        def get_number(self):
                ret = None
                try:
                        ret = self.queue_number.get()
                except  KeyboardInterrupt:
                        pass
                except:
                        print_exc()
                if ret == None:
                        return None, None
                sid, number = info.split(',')
                return  sid, number

#---------------------------------------------------

redis_worker = fd_redis_manager()

#sleep(5)

