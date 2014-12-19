#!/usr/bin/env python3

from  traceback         import print_exc, format_exc
from  time              import sleep, time

from  pp_baseredis      import pp_redis
from  pp_baseclass      import pp_thread
from  pp_global         import pp_global_info

#=================================================================================

def getsleeptime(interval):
        if interval == 0:
                return interval
        return  interval - time()%interval

class fd_synctime(pp_thread):
        deadline_decode = '11:29:55'
        key_time        = 'syn_curtime'
        key_dead        = 'syn_deadline'
        time_interval   = 0.5

        def __init__(self):
                super().__init__()

        def main(self):
                global pp_global_info
                while True:
                        sleep(getsleeptime(self.time_interval))
                        self.set_systime()
                        self.set_deadline()

        @pp_redis.safe_proc
        def set_deadline(self):
                global pp_redis
                try:
                        deadline_decode = pp_global_info.deadline_decode
                except:
                        deadline_decode = self.deadline_decode
                return pp_redis.redis.set(self.key_dead, deadline_decode)

        @pp_redis.safe_proc
        def set_systime(self):
                global pp_redis
                return pp_redis.redis.set(self.key_time, pp_global_info.sys_time)

#------------------------------------------------------

daemon_timer = fd_synctime()

def fd_timer_init():
        daemon_timer.start()
        daemon_timer.wait_for_start()

if __name__ == '__main__':
        fd_timer_init()
        daemon_timer.wait_for_stop()


