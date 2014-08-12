#!/usr/bin/env python3

import  logging
from    threading       import Thread, Event, Lock, Semaphore
from    queue           import Queue, LifoQueue
from    datetime        import datetime
from    redis           import StrictRedis
from    traceback       import print_exc
from    pickle          import dumps, loads

#------------------------------------------

redis_passwd  = 'river'
redis_port    = 6379
redis_ip      = '192.168.1.90'
redis_db      = 5

#------------------------------------------

class pp_thread(Thread):
        def __init__(self, info = ''):
                super().__init__()
                self.flag_stop     = False
                self.event_stop    = Event()
                self.event_started = Event()
                self.thread_info   = info
                self.setDaemon(True)

        def wait_for_start(self):
                self.event_started.wait()

        def stop(self):
                self.flag_stop = True
                self.event_stop.set()

        def run(self):
                self.event_started.set()
                try:
                        self.main()
                except  KeyboardInterrupt:
                        pass

        def main(self): pass

class pp_sender(pp_thread):
        def __init__(self, info = '', lifo = False):
                super().__init__(info)
                self.queue = Queue() if not lifo else LifoQueue()

        def put(self, buff):
                self.queue.put(buff)

        def stop(self):
                pp_thread.stop(self)
                self.put(None)

        def get(self):
                try:
                        return self.queue.get()
                except  KeyboardInterrupt:
                        raise KeyboardInterrupt

        def main(self):
                while True:
                        buff = self.get()
                        if self.flag_stop  == True or not buff  : break
                        if self.proc(buff) == True              : self.queue.task_done()
                        if self.flag_stop  == True              : break

        def proc(self, buff): pass

class redis_sender(pp_sender):
        def __init__(self, redis, info):
                super().__init__(info)
                self.redis = redis

        def send(self, buff):
                self.put(buff)

        def proc(self, buff):
                try:
                        self.redis.rpush(buff[0], buff[1])
                        return True
                except  KeyboardInterrupt:
                        raise KeyboardInterrupt
                except:
                        print_exc()
                        return False

class redis_logger():
        dict_log_level= {
                        'all'      : 0,
                        'debug'    : 10,
                        'info'     : 20,
                        'warning'  : 30,
                        'error'    : 40,
                        'critical' : 50,
                        'null'     : 60,
                        }

        def __init__(self, level = 'debug'):
                self.redis = self.connect_redis()
                if self.redis == None : return None

                level = level if level in self.dict_log_level else 'debug'

                self.log_level = self.dict_log_level[level]

                self.redis_sender = redis_sender(self.redis, 'redis_sender')
                self.redis_sender.start()
                self.redis_sender.wait_for_start()

        def debug(self, log, bin=False):
                if self.log_level > self.dict_log_level['debug']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.send(('debug', dumps((time, log),0)))
                else:
                        self.redis_sender.send(('debug', (time, log)))

        def info(self, log, bin=False):
                if self.log_level > self.dict_log_level['info']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.send(('info', dumps((time, log),0)))
                else:
                        self.redis_sender.send(('info', (time, log)))

        def warning(self, log, bin=False):
                if self.log_level > self.dict_log_level['warning']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.send(('warning', dumps((time, log),0)))
                else:
                        self.redis_sender.send(('warning', (time, log)))

        def error(self, log, bin=False):
                if self.log_level > self.dict_log_level['error']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.send(('error', dumps((time, log),0)))
                else:
                        self.redis_sender.send(('error', (time, log)))

        def critical(self, log, bin=False):
                if self.log_level > self.dict_log_level['critical']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.send(('critical', dumps((time, log),0)))
                else:
                        self.redis_sender.send(('critical', (time, log)))

        def wait_for_flush(self):
                self.redis_sender.queue.join()

        def connect_redis(self):
                global redis_ip, redis_port, redis_passwd, redis_db
                try:
                        return StrictRedis(host = redis_ip, port = redis_port, password = redis_passwd, db = redis_db)
                except:
                        print_exc()
                        return None

#-----------------------------------------------------------------------------------------

class console_logger():
        def debug(self, log):
                print('debug:    ',log)

        def info(self, log):
                print('info:     ',log)

        def warning(self, log):
                print('warning:  ',log)

        def error(self, log):
                print('error:    ',log)

        def critical(self, log):
                print('critical: ',log)

#-----------------------------------------------------------------------------------------

printer = redis_logger()
logger  = console_logger()

#================================ for test ===============================================

if __name__ == "__main__":
        logger.debug('test logger debug')
        logger.info('test logger info')
        logger.warning('test logger warning')
        logger.error('test logger error')
        logger.critical('test logger critical')
        #logger.wait_for_flush()

