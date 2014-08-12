#!/usr/bin/env python3

from threading      import Event, Lock

from fd_config      import list_trigger_image

class fd_global():
        def __init__(self):
                global list_trigger_image
                self.event_gameover = Event()
                self.flag_gameover  = False

                self.event_image    = [Event(), Event(), Event()]
                self.event_price    = [Event(), Event(), Event()]

                #self.trigger_image  = [('10:32:00', 0), ('11:29:35', 600), (None, None)]
                self.trigger_image  = list_trigger_image
                self.trigger_price  = [ None, None, None]
                self.lock_trigger   = Lock()

                self.trigger_channel_first  = ('10:31:00', '10:33:00')
                self.trigger_channel_second = ('11:28:00', '11:29:55')

                self.flag_create_login   = True
                self.flag_create_toubiao = False
                #self.lock_create_toubiao = Lock()

        def set_trigger_price(self, count, price):
                self.lock_trigger.acquire()
                if self.trigger_price[count] == None:
                        self.trigger_price[count] = price
                self.lock_trigger.release()

        def set_start_channel_toubiao(self):
                self.flag_create_toubiao = True

        def set_stop_channel_toubiao(self):
                self.flag_create_toubiao = False


global_info = fd_global()


