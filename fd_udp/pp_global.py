#!/usr/bin/env python3

from time           import sleep
from threading      import Event, Lock
from pickle         import dumps, loads

from pp_baseclass   import pp_thread
from pp_baseredis   import pp_redis

from fd_log         import logger

#========================================================================

def time_sub(end, begin):
        try:
                e = end.split(':')
                b = begin.split(':')
                return (int(e[0])*3600 + int(e[1])*60 + int(e[2])) - (int(b[0])*3600 + int(b[1])*60 + int(b[2]))
        except:
                return -1

class pp_global(pp_thread):

        def __init__(self):
                super().__init__()
                self.flag_gameover      = False
                self.event_gameover     = Event()
                self.timeout_channel    = [30, None]
                self.interval_channel   = 0.4
                self.interval_html      = 0.5

        def set_game_over(self):
                self.flag_gameover = True
                self.event_gameover.set()

        def update_systime(self, stime):
                self.lock_systime.acquire()
                if time_sub(stime, self.sys_time) > 0:
                        self.sys_time = stime
                self.lock_systime.release()

        def update_syscode(self, code):
                if self.sys_code == None and code == 'A':
                        self.sys_code = code
                        return
                if self.sys_code == None and code == 'B':
                        self.sys_code = code
                        return
                if self.sys_code == 'A'  and code == 'B':
                        self.sys_code = code
                        return

#--------------------------------------------

pp_global_info = pp_global()

