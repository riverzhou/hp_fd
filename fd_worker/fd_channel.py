#!/usr/bin/env python3

from threading              import Event, Lock
from queue                  import Queue, Empty
from time                   import sleep, time
from datetime               import datetime
from http.client            import HTTPSConnection, HTTPConnection
from traceback              import print_exc, format_exc

from pp_log                 import printer
from pp_server              import server_dict

from pp_global              import pp_global_info
from pp_baseclass           import pp_thread

#=============================================================================

def time_sub(end, begin):
        try:
                e = datetime.timestamp(datetime.strptime(end,   '%Y-%m-%d %H:%M:%S.%f'))
                b = datetime.timestamp(datetime.strptime(begin, '%Y-%m-%d %H:%M:%S.%f'))
                return e-b
        except:
                return -1

class fd_channel():
        timeout_find_channel = 0.5

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
                self.lock_get_channel       = Lock()

        def check_channel(self, channel_handle_tuple):
                global pp_global_info
                cur_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                time     = channel_handle_tuple[0]
                handle   = channel_handle_tuple[1]
                if time_sub(cur_time, time) < pp_global_info.timeout_channel[0]:
                        return True
                else:
                        self.close_handle(handle)
                        return False

        def find_channel(self, channel, group, timeout = None):
                if group == -1:
                        channel_group = 0 if self.queue[0][channel].qsize() >= self.queue[1][channel].qsize() else 1
                else:
                        channel_group = group
                channel_handle_tuple = None
                try:
                        channel_handle_tuple = self.queue[channel_group][channel].get(True, timeout)
                except  KeyboardInterrupt:
                        return channel_group, None
                except  Empty:
                        return channel_group, None
                except:
                        printer.critical(format_exc())
                        return channel_group, None
                return  channel_group, channel_handle_tuple

        def get_channel(self, channel, group = -1):
                channel_handle = None
                while True:
                        self.lock_get_channel.acquire()
                        channel_group, channel_handle_tuple = self.find_channel(channel, group, self.timeout_find_channel)
                        self.lock_get_channel.release()
                        if channel_handle_tuple == None :
                                sleep(0)
                                continue
                        if self.check_channel(channel_handle_tuple) != True :
                                sleep(0)
                                continue
                        channel_handle = channel_handle_tuple[1]
                        if channel_handle == None:
                                sleep(0)
                                continue
                        break

                printer.debug(
                        'fd_channel : login[0] %d login[1] %d , tb0[0] %d tb0[1] %d , tb1[0] %d tb1[1] %d'
                        % (self.queue[0]['login'].qsize(), self.queue[1]['login'].qsize(), self.queue[0]['tb0'].qsize(), self.queue[1]['tb0'].qsize(), self.queue[0]['tb1'].qsize(), self.queue[1]['tb1'].qsize())
                        )

                return  channel_group, channel_handle

        def put_channel(self, channel, group, handle):
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                channel_handle_tuple = (time, handle)
                return  self.queue[group][channel].put(channel_handle_tuple)

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

        def close_handle(self, handle):
                try:
                        handle.close()
                except:
                        pass

        def pyget(self, handle, req, headers = {}):
                time_req = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')

                printer.info(time_req + ' :: ' + str(headers) + ' :: ' + req)

                try:
                        handle.request('GET', req, headers = headers)
                except  KeyboardInterrupt:
                        self.close_handle(handle)
                        return None
                except:
                        printer.critical(format_exc())
                        self.close_handle(handle)
                        return None
                try:
                        ack  = handle.getresponse()
                        body = ack.read()
                except  KeyboardInterrupt:
                        self.close_handle(handle)
                        return None
                except:
                        printer.critical(format_exc())
                        self.close_handle(handle)
                        return None

                self.close_handle(handle)

                key_val = {}
                key_val['head']    = str(ack.msg)
                key_val['status']  = ack.status
                try:
                        key_val['body'] = body.decode('gb18030')
                except:
                        printer.error(body)
                        key_val['body'] = ''

                time_ack = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')

                printer.info(time_ack + ' :: ' + str(key_val['head']) + ' :: ' + str(key_val['body']))

                printer.time(time_req + ' --- ' + time_ack + ' :: ' + str(headers) + ' :: ' + req + ' :: ' + str(key_val['head']) + ' :: ' + str(key_val['body']))

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
                handle = HTTPSConnection(host)
                handle._http_vsn = 10
                handle._http_vsn_str = 'HTTP/1.0'
                try:
                        handle.connect()
                except  KeyboardInterrupt:
                        pass
                except:
                        printer.critical(format_exc())
                else:
                        channel_center.put_channel(self.channel, self.group, handle)
                self.manager.maker_out()

class pp_login_channel_manager(pp_thread):
        max_onway       = 20

        def __init__(self):
                super().__init__()
                self.lock_onway   = Lock()
                self.number_onway = 0

        def main(self):
                global pp_global_info
                time_interval = 2
                while True:
                        try:
                                time_interval = int(pp_global_info.timeout_channel[1])
                        except:
                                time_interval = 2
                        sleep(getsleeptime(time_interval)
                        self.manage_channel()

        def manage_channel(self):
                global channel_center, pp_global_info
                if pp_global_info.flag_create_login != True or pp_global_info.flag_gameover == True:
                        return
                if channel_center.count_login_request <= 0: 
                        return
                if self.number_onway >= self.max_onway:
                        return
                try:
                        maker = [pp_channel_maker(self, 'login', 0, 'login'), pp_channel_maker(self, 'login', 1, 'login')]
                except:
                        printer.critical(format_exc())
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
        max_onway       = 100

        def __init__(self, id):
                super().__init__()
                self.lock_onway   = Lock()
                self.number_onway = 0
                self.id = id

        def main(self):
                global pp_global_info
                time_interval = 2
                while True:
                        try:
                                time_interval = int(pp_global_info.timeout_channel[1])
                        except:
                                time_interval = 2
                        sleep(getsleeptime(time_interval)
                        self.manage_channel()

        def manage_channel(self):
                global pp_global_info
                if pp_global_info.flag_create_toubiao[self.id] != True or pp_global_info.flag_gameover == True:
                        return
                if self.number_onway >= self.max_onway:
                        return
                if self.id == 0 and pp_global_info.check_bid0_finish() == True:
                        return
                if self.id == 0:
                        channel = 'tb0'
                else:
                        channel = 'tb1'
                try:
                        maker = [pp_channel_maker(self, 'toubiao', 0, channel), pp_channel_maker(self, 'toubiao', 1, channel)]
                except:
                        printer.critical(format_exc())
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

