#!/usr/bin/env python3

import  logging
from    threading           import Thread, Event, Lock
from    queue               import Queue
from    datetime            import datetime
from    traceback           import print_exc
from    pickle              import dumps, loads

from    pp_baseredis        import pp_redis

#=================================================================================

class redis_sender(Thread):
        def __init__(self, info):
                super().__init__()
                self.setDaemon(True)
                self.event_started  = Event()
                self.thread_info    = info
                self.queue          = Queue()

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

        def put(self, buff):
                self.queue.put(buff)

        def get(self):
                try:
                        return self.queue.get()
                except  KeyboardInterrupt:
                        return None
                except:
                        print_exc()
                        return None

        @pp_redis.safe_proc
        def send(self, buff):
                global pp_redis
                #print('send', buff[1])
                return pp_redis.redis.rpush(buff[0], buff[1])

#--------------------------------------------------------------------------------

class redis_logger():
        dict_log_level= {
                        'all'      : 0,
                        'debug'    : 10,
                        'info'     : 20,
                        'warning'  : 30,
                        'error'    : 40,
                        'critical' : 50,
                        'data'     : 60,
                        'time'     : 70,
                        'null'     : 80,
                        }

        def __init__(self, level = 'debug'):
                level = level if level in self.dict_log_level else 'debug'
                self.log_level = self.dict_log_level[level]

                self.redis_sender = redis_sender('redis_sender')
                self.redis_sender.start()
                self.redis_sender.wait_for_start()

        def debug(self, log, bin=False):
                if self.log_level > self.dict_log_level['debug']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.put(('log_debug', dumps((time, log),0)))
                else:
                        self.redis_sender.put(('log_debug', (time, log)))

        def info(self, log, bin=False):
                if self.log_level > self.dict_log_level['info']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.put(('log_info', dumps((time, log),0)))
                else:
                        self.redis_sender.put(('log_info', (time, log)))

        def warning(self, log, bin=False):
                if self.log_level > self.dict_log_level['warning']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.put(('log_warning', dumps((time, log),0)))
                else:
                        self.redis_sender.put(('log_warning', (time, log)))

        def error(self, log, bin=False):
                if self.log_level > self.dict_log_level['error']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.put(('log_error', dumps((time, log),0)))
                else:
                        self.redis_sender.put(('log_error', (time, log)))

        def critical(self, log, bin=False):
                if self.log_level > self.dict_log_level['critical']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.put(('log_critical', dumps((time, log),0)))
                else:
                        self.redis_sender.put(('log_critical', (time, log)))

        def data(self, log, bin=False):
                if self.log_level > self.dict_log_level['data']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.put(('log_data', dumps((time, log),0)))
                else:
                        self.redis_sender.put(('log_data', (time, log)))

        def time(self, log, bin=False):
                if self.log_level > self.dict_log_level['time']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.put(('log_time', dumps((time, log),0)))
                else:
                        self.redis_sender.put(('log_time', (time, log)))

        def wait_for_flush(self):
                self.redis_sender.queue.join()

#-----------------------------------------------------------------------------------------

class console_logger():
        def debug(self, log):
                print('log_debug:    ',log)

        def info(self, log):
                print('log_info:     ',log)

        def warning(self, log):
                print('log_warning:  ',log)

        def error(self, log):
                print('log_error:    ',log)

        def critical(self, log):
                print('log_critical: ',log)

        def data(self, log):
                print('log_data:     ',log)

        def time(self, log):
                print('log_time:     ',log)

        def wait_for_flush(self):
                pass

#-----------------------------------------------------------------------------------------

printer = redis_logger()
#logger  = console_logger()
logger  = redis_logger()

#================================ for test ===============================================

if __name__ == "__main__":
        from pp_baseredis  import pp_redis_init
        pp_redis_init()
        logger.debug('test logger debug')
        logger.info('test logger info')
        logger.warning('test logger warning')
        logger.error('test logger error')
        logger.critical('test logger critical')
        logger.data('test logger data')
        logger.time('test logger time')
        logger.wait_for_flush()

