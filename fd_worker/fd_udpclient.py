#!/usr/bin/env python3

from traceback              import print_exc, format_exc
from datetime               import datetime
from socket                 import socket, AF_INET, SOCK_DGRAM, timeout
from threading              import Lock
from queue                  import Queue, LifoQueue
from time                   import time, sleep, localtime, mktime, strptime, strftime

from pp_baseclass           import pp_thread
from pp_udpproto            import udp_proto
from pp_server              import server_dict
from pp_log                 import printer
from pp_global              import pp_global_info

#=================================================

def time_sub(end, begin):
        try:
                e = end.split(':')
                b = begin.split(':')
                return (int(e[0])*3600 + int(e[1])*60 + int(e[2])) - (int(b[0])*3600 + int(b[1])*60 + int(b[2]))
        except:
                return -1


def getsleeptime(interval):
        return  interval - time()%interval


class udp_format(pp_thread):
        interval = 20

        def __init__(self, worker):
                super().__init__(worker.bidno)
                self.worker = worker

        def main(self):
                for i in range(2):
                        if self.flag_stop == True: return
                        if self.worker.sock != None:
                                try:
                                        self.worker.format_udp()
                                except:
                                        printer.critical(format_exc())
                        if self.event_stop.wait(1) == True: return

                while True:
                        if self.flag_stop == True: return
                        if self.worker.sock != None:
                                try:
                                        self.worker.format_udp()
                                except:
                                        printer.critical(format_exc())
                        if self.event_stop.wait(self.interval) == True: return


class udp_worker(pp_thread):
        udp_timeout = 10

        def __init__(self, acount, group):
                global server_dict
                super().__init__(acount[0])

                self.current_code   = None
                self.last_code      = None

                self.bidno          = acount[0]
                self.pid            = acount[1]
                self.group          = group

                self.proto          = udp_proto()
                self.udp_format     = udp_format(self)

                self.sock           = socket(AF_INET, SOCK_DGRAM)
                self.sock.settimeout(self.udp_timeout)
                self.sock.bind(('',0))

                self.server_addr    = server_dict[group]['udp']['ip'], server_dict[group]['udp']['port']

        def stop(self):
                if self.udp_format != None : self.udp_format.stop()
                if self.sock != None:
                        self.logoff_udp()
                        try:
                                self.sock.close()
                        except:
                                pass
                supper().stop()

        def logoff_udp(self):
                try:
                        self.sock.sendto(self.proto.make_logoff_req(self.bidno, self.pid), self.server_addr)
                except:
                        printer.critical(format_exc())

        def client_udp(self):
                try:
                        self.sock.sendto(self.proto.make_client_req(self.bidno, self.pid), self.server_addr)
                except:
                        printer.critical(format_exc())

        def format_udp(self):
                try:
                        self.sock.sendto(self.proto.make_format_req(self.bidno, self.pid), self.server_addr)
                except:
                        printer.critical(format_exc())

        def recv_udp(self):
                while True:
                        try:
                                if self.sock != None:
                                        udp_result = self.sock.recvfrom(1500)
                        except  (timeout, OSError):
                                return None
                        except:
                                printer.critical(format_exc())
                                return None
                        if self.flag_stop == True:
                                return None
                        if udp_result[1] == self.server_addr:
                                return udp_result[0]

        def check_shot_price(self, cur_price):
                global pp_global_info

                price = pp_global_info.trigger_price[1]
                if price != None and price <= cur_price + 300 and price >= cur_price - 300:
                        pp_global_info.event_price[1].set()

                price = pp_global_info.trigger_price[2]
                if price != None and price <= cur_price + 300 and price >= cur_price - 300:
                        pp_global_info.event_price[2].set()

        def check_image_time(self, cur_price):
                global pp_global_info

                cur_time = pp_global_info.sys_time

                time, price = pp_global_info.trigger_image[0]
                if time != None and price != None and time_sub(cur_time, time) > 0:
                        pp_global_info.set_trigger_price(0, price)
                        pp_global_info.event_price[0].set()
                        pp_global_info.event_image[0].set()

                time, delta_price = pp_global_info.trigger_image[1]
                if time != None and delta_price != None and time_sub(cur_time, time) >= 0:
                        pp_global_info.set_trigger_price(1, cur_price + delta_price)
                        pp_global_info.event_image[1].set()
                        #printer.debug('bid1', cur_price, delta_price, pp_global_info.trigger_price[1])

                time, delta_price = pp_global_info.trigger_image[2]
                if time != None and delta_price != None and time_sub(cur_time, time) >= 0:
                        pp_global_info.set_trigger_price(2, cur_price + delta_price)
                        pp_global_info.event_image[2].set()
                        #printer.debug('bid2', cur_price, delta_price, pp_global_info.trigger_price[2])

        def check_game_over(self, cur_time):
                global pp_global_info

                if cur_time == None and pp_global_info.sys_code != None and time_sub(pp_global_info.sys_time, '11:29:58') >= 0:
                        pp_global_info.set_game_over()
                        pp_global_info.event_price[0].set()
                        pp_global_info.event_price[1].set()
                        pp_global_info.event_price[2].set()
                        pp_global_info.event_image[0].set()
                        pp_global_info.event_image[1].set()
                        pp_global_info.event_image[2].set()

        def check_create_channel(self):
                global pp_global_info

                cur_time = pp_global_info.sys_time

                trigger_channel = pp_global_info.trigger_channel[1]
                time_delta = (time_sub(cur_time, trigger_channel[0]), time_sub(cur_time, trigger_channel[1]))
                if time_delta[0] >= 0 and time_delta[1] < -10:
                        pp_global_info.flag_create_toubiao[1] = True
                if time_delta[1] > 0:
                        pp_global_info.flag_create_toubiao[1] = False

                trigger_channel = pp_global_info.trigger_channel[0]
                time_delta = (time_sub(cur_time, trigger_channel[0]), time_sub(cur_time, trigger_channel[1]))
                if time_delta[0] >= 0 and time_delta[1] < -10:
                        pp_global_info.flag_create_toubiao[0] = True
                if time_delta[1] > 0:
                        pp_global_info.flag_create_toubiao[0] = False

        def check_time(self, stime):
                try:
                        if len(stime) != 8 or stime[2] != ':' or stime[5] != ':' :
                                printer.critical('udp systime error !!! ------ ' + str(stime))
                                return False
                        x = int(stime[0:2])
                        y = int(stime[3:5])
                        z = int(stime[6:8])
                except:
                        printer.critical('udp systime error !!! ------ ' + str(stime))
                        return False
                return stime

        def check_price(self, price):
                try:
                        int_price = int(price)
                except:
                        printer.critical('udp price error !!! ------ ' + str(price))
                        return False
                return int_price

        def update_status(self):
                global pp_global_info
                udp_recv = self.recv_udp()
                if udp_recv == None:
                        return

                udp_recv = self.proto.parse_decode(udp_recv)
                info_val = self.proto.parse_ack(udp_recv)
                if info_val == None:
                        return

                code  = info_val['code']

                if code == 'F':
                        return

                if code == 'C':
                        self.check_game_over(info_val['systime'])
                        return

                stime = self.check_time(info_val['systime'])
                if stime == False:
                        return

                self.update_syscode(code)
                self.update_systime(stime)
                self.check_create_channel()

                int_price = self.check_price(info_val['price'])
                if int_price == False:
                        printer.error(str(self.server_addr) + ' :: ' + udp_recv)
                        return

                self.check_shot_price(int_price)

                self.check_image_time(int_price)

                #printer.record(str(self.server_addr) + ' :: ' + udp_recv)

        def update_syscode(self, code):
                global pp_global_info
                pp_global_info.update_syscode(code)

        def update_systime(self, stime):
                global pp_global_info
                pp_global_info.update_systime(stime)

        def main(self):
                #print('udp_worker : ', str(self.server_addr))
                self.udp_format.start()
                self.udp_format.wait_for_start()
                while True:
                        if self.flag_stop == True: break
                        try:
                                self.update_status()
                        except  KeyboardInterrupt:
                                break
                        except:
                                printer.critical(format_exc())
                                sleep(1)

class udp_htmlworker(udp_worker):
         def __init__(self, acount):
                global pp_global_info
                super().__init__(acount, 1)
                self.server_addr = pp_global_info.addr_htmludp

class udp_manager(pp_thread):
        max_count_worker = 6

        def __init__(self):
                super().__init__()
                self.count_worker       = 0
                self.lock_worker        = Lock()
                self.queue_worker       = Queue()
                self.list_worker        = []
                self.flag_htmlworker    = False
                self.htmlworker         = None

        def main(self):
                group = 0
                while True:
                        account = self.queue_worker.get()
                        group = 1 if group == 0 else 0
                        worker = udp_worker(account, group)
                        self.list_worker.append(worker)
                        worker.start()
                        if self.flag_htmlworker != True:
                                self.htmlworker         = udp_htmlworker(account)
                                self.htmlworker.start()
                                self.flag_htmlworker    = True

        def add(self, account):
                self.lock_worker.acquire()
                count_worker = self.count_worker
                self.count_worker += 1
                self.lock_worker.release()
                if count_worker >= self.max_count_worker:
                        return
                self.queue_worker.put(account)

#------------------------------------------------------

daemon_udp = udp_manager()

def fd_udp_init():
        daemon_udp.start()
        daemon_udp.wait_for_start()

