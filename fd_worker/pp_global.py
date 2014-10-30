#!/usr/bin/env python3

from threading      import Event, Lock
from fd_config      import mode_price

def time_sub(end, begin):
        e = end.split(':')
        b = begin.split(':')
        return (int(e[0])*3600 + int(e[1])*60 + int(e[2])) - (int(b[0])*3600 + int(b[1])*60 + int(b[2]))

class fd_global():

        trigger_image_a = [('10:35:00', 72600), ('11:29:35', 700), (None, None)]
        trigger_image_b = [('10:35:00', 72600), ('11:29:35', 600), ('11:29:35', 800)]

        trigger_channel_first  = ('10:33:20', '10:35:30')
        trigger_channel_second = ('11:27:50', '11:29:55')

        decode_deadline = '11:29:50'

        channel_timeout = 110

        def __init__(self):
                global mode_price

                if mode_price == 'A':
                        self.trigger_image = self.trigger_image_a
                else:
                        self.trigger_image = self.trigger_image_b

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

