#!/usr/bin/env python3

from threading              import Thread, Event, Lock, Semaphore
from queue                  import Queue, LifoQueue
from time                   import sleep, time
from http.client            import HTTPSConnection, HTTPConnection
from traceback              import print_exc

from pp_log                 import logger, printer
from pp_baseclass           import pp_thread
from pp_server              import server_dict
from fd_global              import global_info

class fd_channel():
        def __init__(self):
                self.queue = [{},{}]
                self.queue[0]['login']          = Queue()
                self.queue[1]['login']          = Queue()
                self.queue[0]['toubiao']        = Queue()
                self.queue[1]['toubiao']        = Queue()

                self.count_login_request        = 0
                self.lock_login_request         = Lock()

        def get_channel(self, server, group = -1):
                if group == -1:
                        group = 0 if self.queue[0][server].qsize() >= self.queue[1][server].qsize() else 1
                channel = None
                try:
                        channel = self.queue[group][server].get()
                except  KeyboardInterrupt:
                        pass
                except:
                        print_exc()
                print('fd_channel login[0] %d login[1] %d toubiao[0] %d toubiao[1] %d'
                        % (self.queue[0]['login'].qsize(), self.queue[1]['login'].qsize(), self.queue[0]['toubiao'].qsize(), self.queue[0]['toubiao'].qsize()))
                return  group, channel

        def put_channel(self, server, group, channel):
                return self.queue[group][server].put(channel)

        def login_request_increase(self):
                self.lock_login_request.acquire()
                self.count_login_request += 1
                #print('fd_channel login_request_increase', self.count_login_request)
                self.lock_login_request.release()

        def login_request_decrease(self):
                self.lock_login_request.acquire()
                self.count_login_request -= 1
                if self.count_login_request < 0 : 
                        self.count_login_request = 0
                #print('fd_channel login_request_decrease', self.count_login_request)
                self.lock_login_request.release()

        def pyget(self, handler, req, headers = {}):
                printer.info(req)

                try:
                        handler.request('GET', req, headers = headers)
                except  KeyboardInterrupt:
                        return None
                except:
                        print_exc()
                        return None
                try:
                        ack  = handler.getresponse()
                        body = ack.read()
                except  KeyboardInterrupt:
                        return None
                except:
                        print_exc()
                        return None

                key_val = {}
                key_val['body']    = body
                key_val['head']    = str(ack.msg)
                key_val['status']  = ack.status

                printer.info(key_val['body'])
                return key_val

#-----------------------------------

channel_center = fd_channel()

#===================================

def getsleeptime(interval):
        return  interval - time()%interval

class pp_channel_maker(pp_thread):
        def __init__(self, manager, server, group):
                super().__init__(None)
                self.manager = manager
                self.server  = server
                self.group   = group

        def main(self):
                self.create_channel()

        def create_channel(self):
                global channel_center, server_dict
                self.manager.maker_in()
                host    = server_dict[self.group][self.server]['ip']
                handler = HTTPSConnection(host)
                #handler = HTTPConnection(host)
                handler._http_vsn = 10
                handler._http_vsn_str = 'HTTP/1.0'
                try:
                        handler.connect()
                except  KeyboardInterrupt:
                        pass
                except:
                        print_exc()
                else:
                        channel_center.put_channel(self.server, self.group, handler)
                        #print('pp_channel_maker', self.group, self.server)
                self.manager.maker_out()

class pp_login_channel_manager(pp_thread):
        time_interval   = 1
        max_onway       = 30

        def __init__(self):
                super().__init__()
                self.lock_onway   = Lock()
                self.number_onway = 0

        def main(self):
                while True:
                        self.manage_channel()
                        sleep(getsleeptime(self.time_interval))

        def manage_channel(self):
                global channel_center, global_info
                if global_info.flag_create_login != True:
                        return
                if channel_center.count_login_request <= 0: 
                        return
                if self.number_onway >= self.max_onway:
                        return
                try:
                        maker = [pp_channel_maker(self, 'login', 0), pp_channel_maker(self, 'login', 1)]
                except:
                        print_exc()
                        return
                maker[0].start()
                maker[1].start()

        def maker_in(self):
                self.lock_onway.acquire()
                self.number_onway += 1
                self.lock_onway.release()
                
        def maker_out(self):
                self.lock_onway.acquire()
                self.number_onway -= 1
                self.lock_onway.release()

class pp_toubiao_channel_manager(pp_thread):
        time_interval   = 1
        max_onway       = 200

        def __init__(self):
                super().__init__()
                self.lock_onway   = Lock()
                self.number_onway = 0

        def main(self):
                while True:
                        self.manage_channel()
                        sleep(getsleeptime(self.time_interval))

        def manage_channel(self):
                global channel_center, global_info
                if global_info.flag_create_toubiao != True:
                        return
                if self.number_onway >= self.max_onway:
                        return
                try:
                        maker = [pp_channel_maker(self, 'toubiao', 0), pp_channel_maker(self, 'toubiao', 1)]
                except:
                        print_exc()
                        return
                maker[0].start()
                maker[1].start()

        def maker_in(self):
                self.lock_onway.acquire()
                self.number_onway += 1
                self.lock_onway.release()
                
        def maker_out(self):
                self.lock_onway.acquire()
                self.number_onway -= 1
                self.lock_onway.release()

#================================================

login   = pp_login_channel_manager()
toubiao = pp_toubiao_channel_manager()

def fd_channel_init():
        global login, toubiao
        login.start()
        toubiao.start()
        login.wait_for_start()
        toubiao.wait_for_start()

def print_channel_number():
        print('login 0', channel_center.queue[0]['login'].qsize())
        print('login 1', channel_center.queue[1]['login'].qsize())
        print('toubiao 0', channel_center.queue[0]['toubiao'].qsize())
        print('toubiao 1', channel_center.queue[1]['toubiao'].qsize())

def fd_channel_test():
        global global_info
        global_info.flag_create_login   = True
        global_info.flag_create_toubiao = True


