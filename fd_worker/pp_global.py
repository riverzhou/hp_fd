#!/usr/bin/env python3

from threading      import Event, Lock

def time_sub(end, begin):
        e = end.split(':')
        b = begin.split(':')
        return (int(e[0])*3600 + int(e[1])*60 + int(e[2])) - (int(b[0])*3600 + int(b[1])*60 + int(b[2]))

class pp_global():

        trigger_image_a = [('10:35:00', 72600), ('11:29:40', 600), ('11:29:50', 400)]
        trigger_image_b = [('10:35:00', 72600), ('11:29:40', 600), ('11:29:55', 300)]
        trigger_image_c = [('10:35:00', 72600), ('11:29:50', 400), (None, None)]
        trigger_image_d = [('10:35:00', 72600), ('11:29:55', 300), (None, None)]

        trigger_channel_first  = ('10:33:10', '10:55:00')
        trigger_channel_second = ('11:28:10', '11:29:58')

        decode_deadline = '11:29:56'

        channel_timeout = 110

        mode_price = 'A'

        list_account = [
                ('11111111', '1111'),   # 测试
                ('22222222', '2222'),   # 测试
                ('33333333', '3333'),   # 测试
                ('44444444', '4444'),   # 测试
                ('55555555', '5555'),   # 测试
                ('66666666', '6666'),   # 测试
                ('77777777', '7777'),   # 测试
                ('88888888', '8888'),   # 测试
                ('99999999', '9999'),   # 测试
                ]

        def __init__(self):
                global mode_price

                if mode_price == 'A':
                        self.trigger_image = self.trigger_image_a
                if mode_price == 'B':
                        self.trigger_image = self.trigger_image_b
                if mode_price == 'C':
                        self.trigger_image = self.trigger_image_c
                if mode_price == 'D':
                        self.trigger_image = self.trigger_image_d
                else:
                        self.trigger_image = self.trigger_image_a

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

pp_global_info = pp_global()

