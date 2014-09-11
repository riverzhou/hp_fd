#!/usr/bin/env python3

from threading      import Event, Lock

def time_sub(end, begin):
        e = end.split(':')
        b = begin.split(':')
        return (int(e[0])*3600 + int(e[1])*60 + int(e[2])) - (int(b[0])*3600 + int(b[1])*60 + int(b[2]))

class fd_global():
        trigger_image  = [('10:32:00', 72600), ('11:29:35', 600), (None, None)]

        trigger_channel_first  = ('10:31:00', '10:33:00')
        trigger_channel_second = ('11:28:00', '11:29:55')

        decode_deadline = '11:29:50'

        def __init__(self):
                self.flag_create_login   = True
                self.flag_create_toubiao = [False, False]

                self.flag_gameover  = False
                self.event_gameover = Event()

                self.event_image    = [Event(), Event(), Event()]
                self.event_price    = [Event(), Event(), Event()]

                self.trigger_price  = [None, None, None]
                self.lock_trigger   = Lock()

                self.lock_systime   = Lock()
                self.sys_time       = '10:30:00'

        def set_trigger_price(self, count, price):
                self.lock_trigger.acquire()
                if self.trigger_price[count] == None:
                        self.trigger_price[count] = price
                self.lock_trigger.release()

        def set_game_over(self):
                self.flag_gameover  = True
                self.event_gameover.set()

        def update_systime(self, stime):
                self.lock_systime.acquire()
                if time_sub(stime, self.sys_time) > 0:
                        self.sys_time = stime
                self.lock_systime.release()

#-----------------------------

global_info = fd_global()

