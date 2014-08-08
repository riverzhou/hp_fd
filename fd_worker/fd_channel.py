#!/usr/bin/env python3


class fd_channel():
        def __init__(self):
                #self.max_queue = = [{},{}]
                #self.max_queue[0]['login']     = 20
                #self.max_queue[1]['login']     = 20
                #self.max_queue[0]['toubiao']   = 150
                #self.max_queue[1]['toubiao']   = 150

                self.queue = [{},{}]
                self.queue[0]['login']          = Queue()
                self.queue[1]['login']          = Queue()
                self.queue[0]['toubiao']        = Queue()
                self.queue[1]['toubiao']        = Queue()

                self.flag_create_login          = False
                self.flag_create_toubiao        = False

                self.lock_create_login          = Lock()
                self.lock_create_toubiao        = Lock()

                self.count_login_request        = 0
                self.lock_login_request         = Lock()

        def get_channel(self, server, group = -1):
                if group == -1:
                        group = 0 if self.queue[0]['server'] >= self.queue[1]['server'] else 1
                channel = None
                try:
                        channel = self.queue[group][server].get()
                except  KeyboardInterrupt:
                        raise KeyboardInterrupt
                return  channel

        def put_channel(self, server, group, channel):
                return self.queue[group][server].put(channel)

#-----------------------------------

channel_center = fd_channel()

#===================================

def getsleeptime(interval):
        return  interval - time()%interval

class pp_channel_maker(pp_thread):
        def __init__(self, manager, server, group):
                self.manager = manager
                self.server  = server
                self.group   = group
                super().__init__()

        def main(self):
                self.create_channel()

        def create_channel(self):
                global channel_center, server_dict
                self.manager.maker_in()
                host    = server_dict[self.group]['self.server']
                handler = HTTPSConnection(host)
                handler._http_vsn = 10
                handler._http_vsn_str = 'HTTP/1.0'
                try:
                        self.handler.connect()
                except:
                        self.manager.maker_out()
                else:
                        channel_center.put_channel(self.server, self.group, handler)
                        self.manager.maker_out()


class pp_login_channel_manager(pp_thread):
        time_interval   = 1
        max_onway       = 30

        def __init__(self, manager, server, group):
                self.lock_onway   = Lock()
                self.number_onway = 0
                super().__init__()

        def main(self):
                while True:
                        self.manager()
                        sleep(getsleeptime(self.time_interval)

        def manage_chanel(self):
                global channel_center
                if channel_center.flag_create_login != True:
                        return
                if channel_center.count_login_request <= 0 : 
                        return
                if self.number_onway >= self.max_onway :
                        return
                try:
                        maker = [pp_channel_maker(self, 'login', 0), pp_channel_maker(self, 'login', 1)]
                except:
                        return
                maker[0].start()
                maker[1].start()

        def maker_in(self):
                self.lock_onway.acquire()
                self.number_onway += 1
                self.lock_onway.release()
                
        def maker_in(self):
                self.lock_onway.acquire()
                self.number_onway -= 1
                self.lock_onway.release()


class pp_toubiao_channel_manager(pp_thread):
        time_interval   = 1
        max_onway       = 200

        def __init__(self, manager, server, group):
                self.lock_onway   = Lock()
                self.number_onway = 0
                super().__init__()

        def main(self):
                while True:
                        self.manager()
                        sleep(getsleeptime(self.time_interval)

        def manage_chanel(self):
                global channel_center
                if channel_center.flag_create_toubiao != True:
                        return
                if self.number_onway >= self.max_onway :
                        return
                try:
                        maker = [pp_channel_maker(self, 'toubiao', 0), pp_channel_maker(self, 'toubiao', 1)]
                except:
                        return
                maker[0].start()
                maker[1].start()

        def maker_in(self):
                self.lock_onway.acquire()
                self.number_onway += 1
                self.lock_onway.release()
                
        def maker_in(self):
                self.lock_onway.acquire()
                self.number_onway -= 1
                self.lock_onway.release()



