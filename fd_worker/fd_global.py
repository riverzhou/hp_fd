#!/usr/bin/env python3

from threading          import Thread, Event, Lock, Semaphore

class fd_global():
        def __init__(self):
                self.flag_gameover  = False

                self.event_image    = [Event(), Event(), Event()]
                self.event_price    = [Event(), Event(), Event()]

                self.trigger_image  = [ ('10:32:00', 0), ('11:29:35', 600), (None, None)]
                self.trigger_price  = [ None, None, None]
                self.lock_trigger   = Lock()

        def set_trigger_price(self, count, price):
                self.lock_trigger.acquire()
                if self.trigger_price[count] == None:
                        self.trigger_price[count] = price
                self.lock_trigger.release()

global_info = fd_global()


