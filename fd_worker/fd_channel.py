#!/usr/bin/env python3

from threading              import Event, Lock
from queue                  import Queue, Empty
from time                   import sleep, time
from http.client            import HTTPSConnection, HTTPConnection
from traceback              import print_exc

from pp_log                 import logger, printer
from pp_baseclass           import pp_thread
from pp_server              import server_dict
from fd_global              import global_info

#=============================================================================

class fd_channel():
        timeout_find_channel = 1

        def __init__(self):
                self.queue = [{},{}]
                self.queue[0]['login']      = Queue()
                self.queue[1]['login']      = Queue()
                self.queue[0]['tb0']        = Queue()
                self.queue[1]['tb0']        = Queue()
                self.queue[0]['tb1']        = Queue()
                self.queue[1]['tb1']        = Queue()

                self.count_login_request    = 0
                self.lock_login_request     = Lock()

        def find_channel(self, channel, group, timeout = None):
                if group == -1:
                        channel_group = 0 if self.queue[0][channel].qsize() >= self.queue[1][channel].qsize() else 1
                else:
                        channel_group = group
                channel_handle = None
                try:
                        channel_handle = self.queue[channel_group][channel].get(True, timeout)
                except  KeyboardInterrupt:
                        return channel_group, None
                except  Empty:
                        return channel_group, None
                except:
                        print_exc()
                        return channel_group, None
                print   (
                        'fd_channel : login[0] %d login[1] %d , tb0[0] %d tb0[1] %d , tb1[0] %d tb1[1] %d'
                        % (self.queue[0]['login'].qsize(), self.queue[1]['login'].qsize(), self.queue[0]['tb0'].qsize(), self.queue[1]['tb0'].qsize(), self.queue[0]['tb1'].qsize(), self.queue[1]['tb1'].qsize())
                        )
                return  channel_group, channel_handle

        def get_channel(self, channel, group = -1):
                while True:
                        channel_group, channel_handle = self.find_channel(channel, group, self.timeout_find_channel)
                        if channel_handle != None:
                                break
                        sleep(0)
                return  channel_group, channel_handle
                                
        def put_channel(self, channel, group, handle):
                return self.queue[group][channel].put(handle)

        def login_request_increase(self):
                self.lock_login_request.acquire()
                self.count_login_request += 1
                self.lock_login_request.release()

        def login_request_decrease(self):
                self.lock_login_request.acquire()
                self.count_login_request -= 1
                if self.count_login_request < 0 : 
                        self.count_login_request = 0
                self.lock_login_request.release()

        def pyget(self, handler, req, headers = {}):
                printer.info(str(headers))
                printer.info(req)

                try:
                        handler.request('GET', req, headers = headers)
                except  KeyboardInterrupt:
                        return None
                except:
                        print_exc()
                        #是否记录异常到日志 XXX XXX XXX
                        return None
                try:
                        ack  = handler.getresponse()
                        body = ack.read()
                except  KeyboardInterrupt:
                        return None
                except:
                        print_exc()
                        #是否记录异常到日志 XXX XXX XXX
                        return None

                key_val = {}
                key_val['body']    = body
                key_val['head']    = str(ack.msg)
                key_val['status']  = ack.status

                printer.info(key_val['head'])
                printer.info(key_val['body'])
                return key_val

#===================================

def getsleeptime(interval):
        return  interval - time()%interval

class pp_channel_maker(pp_thread):
        def __init__(self, manager, server, group, channel):
                super().__init__(None)
                self.manager = manager
                self.server  = server
                self.group   = group
                self.channel = channel

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
                        channel_center.put_channel(self.channel, self.group, handler)
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
                if global_info.flag_create_login != True or global_info.flag_gameover == True:
                        return
                if channel_center.count_login_request <= 0: 
                        return
                if self.number_onway >= self.max_onway:
                        return
                try:
                        maker = [pp_channel_maker(self, 'login', 0, 'login'), pp_channel_maker(self, 'login', 1, 'login')]
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

        def __init__(self, id):
                super().__init__()
                self.lock_onway   = Lock()
                self.number_onway = 0
                self.id = id

        def main(self):
                while True:
                        self.manage_channel()
                        sleep(getsleeptime(self.time_interval))

        def manage_channel(self):
                global global_info
                if global_info.flag_create_toubiao[self.id] != True or global_info.flag_gameover == True:
                        return
                if self.number_onway >= self.max_onway:
                        return
                if self.id == 0:
                        channel = 'tb0'
                else:
                        channel = 'tb1'
                try:
                        maker = [pp_channel_maker(self, 'toubiao', 0, channel), pp_channel_maker(self, 'toubiao', 1, channel)]
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

channel_center = fd_channel()

login   = pp_login_channel_manager()
toubiao = [pp_toubiao_channel_manager(0), pp_toubiao_channel_manager(1)]

def fd_channel_init():
        global login, toubiao

        login.start()
        toubiao[0].start()
        toubiao[1].start()

        login.wait_for_start()
        toubiao[0].wait_for_start()
        toubiao[1].wait_for_start()

def print_channel_number():
        print('login 0', channel_center.queue[0]['login'].qsize())
        print('login 1', channel_center.queue[1]['login'].qsize())
        print('tb0 0', channel_center.queue[0]['tb0'].qsize())
        print('tb0 1', channel_center.queue[1]['tb0'].qsize())
        print('tb1 0', channel_center.queue[0]['tb1'].qsize())
        print('tb1 1', channel_center.queue[1]['tb1'].qsize())

def fd_channel_test():
        global global_info
        global_info.flag_create_login       = True
        global_info.flag_create_toubiao[0]  = True
        global_info.flag_create_toubiao[1]  = True


