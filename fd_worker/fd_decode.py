#!/usr/bin/env python3

from time                   import sleep
from traceback              import print_exc, format_exc
from threading              import Event, Lock
from queue                  import Queue

from pp_baseclass           import pp_thread
from pp_log                 import printer

from pp_baseredis           import pp_redis

#------------------------------------------

class fd_redis_reader(pp_thread):
        key_number = 'ack_number'

        def __init__(self, manager):
                super().__init__()
                self.manager = manager

        def main(self):
                while True:
                        val = self.read()
                        if val == None:
                                sleep(0)
                                continue
                        self.manager.put_number(val)
                        printer.data('fd_redis_reader %s' % val)

        @pp_redis.safe_proc
        def read(self):
                global pp_redis
                return pp_redis.redis.blpop(self.key_number)[1].decode()


class fd_redis_writer(pp_thread):
        key_image = 'req_image'

        def __init__(self, manager):
                super().__init__()
                self.manager = manager

        def main(self):
                while True:
                        val = self.manager.get_image()
                        if val == None:
                                sleep(0)
                                continue
                        self.write(val)
                        printer.data('fd_redis_writer %s' % val)

        @pp_redis.safe_proc
        def write(self, val):
                global pp_redis
                return pp_redis.redis.rpush(self.key_image, val.encode())


class fd_dama_result():
        def __init__(self):
                self.event  = Event()
                self.number = None

        def put_number(self, number):
                self.number = number
                self.event.set()
                return True

        def get_number(self):
                try:
                        self.event.wait()
                except  KeyboardInterrupt:
                        return None
                except:
                        printer.critical(format_exc())
                        return None
                return self.number


class fd_decode_manager(pp_thread):

        def __init__(self):
                super().__init__()
                self.queue_image    = Queue()
                self.queue_number   = Queue()

                reader = fd_redis_reader(self)
                writer = fd_redis_writer(self)

                writer.start()
                writer.wait_for_start()

                reader.start()
                reader.wait_for_start()

                self.dict_result = {}
                self.lock_result = Lock()

        def get_number(self):
                ret = None
                try:
                        ret = self.queue_number.get()
                except  KeyboardInterrupt:
                        pass
                except:
                        printer.critical(format_exc())
                if ret == None:
                        return None, None
                sid, number = ret.split(',')
                return  sid, number

        def main(self):
                while True:
                        sid, number = self.get_number()
                        if sid == None or number == None:
                                sleep(0)
                                continue
                        if sid not in self.dict_result:
                                continue
                        self.dict_result[sid].put_number(number)

        #子线程回调接口
        def get_image(self):
                ret = None
                try:
                        ret = self.queue_image.get()
                except  KeyboardInterrupt:
                        pass
                except:
                        printer.critical(format_exc())
                return  ret

        #子线程回调接口
        def put_number(self, val):
                return  self.queue_number.put(val)

        #外部调用接口
        def get_result(self, sid):
                if sid not in self.dict_result:
                        return None
                return  self.dict_result[sid].get_number()

        #外部调用接口
        def put_request(self, sid, decode_type , decode_timeout, image):
                self.lock_result.acquire()
                if sid not in self.dict_result:
                        self.dict_result[sid] = fd_dama_result()
                self.lock_result.release()
                val = ','.join([sid, decode_type, str(decode_timeout), image])
                return  self.queue_image.put(val)

#---------------------------------------------------

decode_worker = fd_decode_manager()

def fd_decode_init():
        decode_worker.start()
        decode_worker.wait_for_start()

