#!/usr/bin/env python3

import  logging
from    threading           import Thread, Event, Lock
from    queue               import Queue
from    datetime            import datetime
from    redis               import StrictRedis
from    traceback           import print_exc
from    pickle              import dumps, loads

from    fd_config           import redis_passwd, redis_port, redis_ip, redis_dbid

#------------------------------------------

class redis_sender(Thread):
        def __init__(self, redis, info):
                super().__init__()
                self.setDaemon(True)
                self.event_started  = Event()
                self.thread_info    = info
                self.queue = Queue()
                self.redis = redis

        def wait_for_start(self, timeout = None):
                if timeout == None:
                        self.event_started.wait()
                else:
                        try:
                                int(timeout)
                        except  KeyboardInterrupt:
                                pass
                        except:
                                print_exc()
                                self.event_started.wait(self.default_start_timeout)
                        else:
                                self.event_started.wait(timeout)

        def run(self):
                print("pp_log \tredis_sender started")
                self.event_started.set()
                try:
                        self.main()
                except  KeyboardInterrupt:
                        pass

        def main(self):
                while True:
                        buff = self.get()
                        if buff == None:
                                sleep(0)
                                continue
                        if self.send(buff) == True : 
                                self.queue.task_done()

        def send(self, buff):
                try:
                        self.redis.rpush(buff[0], buff[1])
                        return True
                except  KeyboardInterrupt:
                        return False
                except:
                        print_exc()
                        return False

        def get(self):
                try:
                        return self.queue.get()
                except  KeyboardInterrupt:
                        return None
                except:
                        print_exc()
                        return None

        def put(self, buff):
                self.queue.put(buff)


class redis_logger():
        dict_log_level= {
                        'all'      : 0,
                        'debug'    : 10,
                        'info'     : 20,
                        'warning'  : 30,
                        'error'    : 40,
                        'critical' : 50,
                        'data'     : 60,
                        'null'     : 70,
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
                        self.redis_sender.put(('debug', dumps((time, log),0)))
                else:
                        self.redis_sender.put(('debug', (time, log)))

        def info(self, log, bin=False):
                if self.log_level > self.dict_log_level['info']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.put(('info', dumps((time, log),0)))
                else:
                        self.redis_sender.put(('info', (time, log)))

        def warning(self, log, bin=False):
                if self.log_level > self.dict_log_level['warning']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.put(('warning', dumps((time, log),0)))
                else:
                        self.redis_sender.put(('warning', (time, log)))

        def error(self, log, bin=False):
                if self.log_level > self.dict_log_level['error']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.put(('error', dumps((time, log),0)))
                else:
                        self.redis_sender.put(('error', (time, log)))

        def critical(self, log, bin=False):
                if self.log_level > self.dict_log_level['critical']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.put(('critical', dumps((time, log),0)))
                else:
                        self.redis_sender.put(('critical', (time, log)))

        def data(self, log, bin=False):
                if self.log_level > self.dict_log_level['data']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.put(('data', dumps((time, log),0)))
                else:
                        self.redis_sender.put(('data', (time, log)))

        def wait_for_flush(self):
                self.redis_sender.queue.join()

        def connect_redis(self):
                global redis_ip, redis_port, redis_passwd, redis_dbid
                try:
                        return StrictRedis(host = redis_ip, port = redis_port, password = redis_passwd, db = redis_dbid)
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

        def data(self, log):
                print('data: ',log)

        def wait_for_flush(self):
                pass

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
        logger.data('test logger data')
        logger.wait_for_flush()

