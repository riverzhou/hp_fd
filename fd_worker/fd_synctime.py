#!/usr/bin/env python3

from  traceback         import print_exc, format_exc
from  time              import sleep, time

from  pp_baseclass      import pp_thread
from  pp_global         import pp_global_info

from  fd_redis          import redis_db
from  fd_config         import redis_dbid

#=================================================================================

def getsleeptime(interval):
        return  interval - time()%interval


class fd_synctime(pp_thread):
        key_time        = 'curtime'
        key_dead        = 'deadline'
        time_interval   = 0.5

        def __init__(self):
                super().__init__()
                global redis_dbid
                self.db      = redis_dbid
                self.redis   = redis_db(self.db, 'timer')

        def main(self):
                global pp_global_info
                self.redis.set(self.key_dead, pp_global_info.decode_deadline)
                while True:
                        sleep(getsleeptime(self.time_interval))
                        self.redis.set(self.key_time, pp_global_info.sys_time)


#------------------------------------------------------

daemon_timer = fd_synctime()

def fd_timer_init():
        daemon_timer.start()
        daemon_timer.wait_for_start()

if __name__ == '__main__':
        fd_timer_init()
        daemon_timer.wait_for_stop()


