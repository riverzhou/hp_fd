#!/usr/bin/env python3


from datetime       import datetime
from socket         import socket, AF_INET, SOCK_DGRAM
from threading      import Lock
from time           import time, sleep, localtime, mktime, strptime, strftime

from pp_baseclass   import pp_thread
from pp_udpproto    import udp_proto
from pp_server      import server_dict
from fd_global      import global_info

#=================================================

def time_sub(end, begin):
        return int(mktime(strptime('1970-01-01 '+end, '%Y-%m-%d %H:%M:%S'))) - int(mktime(strptime('1970-01-01 '+begin, '%Y-%m-%d %H:%M:%S')))


def getsleeptime(interval):
        return  interval - time()%interval


class udp_format(pp_thread):
        interval = 20

        def __init__(self, worker):
                pp_thread.__init__(self, 'udp_format')
                self.worker = worker

        def main(self):
                for i in range(2):
                        if self.flag_stop == True: return
                        if self.worker.sock != None:
                                try:
                                        self.worker.format_udp()
                                except:
                                        print_exc()
                        if self.event_stop.wait(1) == True: return

                while True:
                        if self.flag_stop == True: return
                        if self.worker.sock != None:
                                try:
                                        self.worker.format_udp()
                                except:
                                        print_exc()
                        if self.event_stop.wait(self.interval) == True: return


class udp_worker(pp_thread):
        udp_timeout = 10

        def __init__(self, acount, group):
                global server_dict
                super().__init__()

                self.bidno          = acount['bidno']
                self.pid            = acount['pid']
                self.group          = group

                self.server_addr    = server_dict[group]['udp']['ip'], server_dict[group]['udp']['port']

                self.sock           = socket(AF_INET, SOCK_DGRAM)
                self.sock.settimeout(self.udp_timeout)
                self.sock.bind(('',0))

                self.proto          = udp_proto()
                self.udp_format     = udp_format(self)

                self.current_code   = None
                self.last_code      = None

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
                        print_exc()

        def client_udp(self):
                try:
                        self.sock.sendto(self.proto.make_client_req(self.bidno, self.pid), self.server_addr)
                except:
                        print_exc()

        def format_udp(self):
                try:
                        self.sock.sendto(self.proto.make_format_req(self.bidno, self.pid), self.server_addr)
                except:
                        print_exc()

        def recv_udp(self):
                while True:
                        try:
                                if self.sock != None:
                                        udp_result = self.sock.recvfrom(1500)
                        except  (TimeoutError, OSError):
                                return None
                        except :
                                print_exc()
                                return None
                        if self.flag_stop == True:
                                return None
                        if udp_result[1] == self.server_addr:
                                return udp_result[0]

        def check_shot_price(self, cur_price):
                global global_info

                price = global_info.trigger_price[1]
                if price != None and price <= cur_price + 300 and price >= cur_price - 300:
                        global_info.event_price[1].set()

                price = global_info.trigger_price[2]
                if price != None and price <= cur_price + 300 and price >= cur_price - 300:
                        global_info.event_price[2].set()

        def check_image_time(self, cur_time, cur_price):
                global global_info

                time, price = global_info.trigger_image[0]
                if time != None and price != None and time_sub(cur_time, time) > 0:
                        global_info.set_trigger_price(0, price)
                        global_info.event_price[0].set()
                        global_info.event_image[0].set()

                time, delta_price = global_info.trigger_image[1]
                if time != None and delta_price != None and time_sub(cur_time, time) > 0:
                        global_info.set_trigger_price(1, cur_price + delta_price)
                        global_info.event_image[1].set()

                time, delta_price = global_info.trigger_image[2]
                if time != None and delta_price != None and time_sub(cur_time, time) > 0:
                        global_info.set_trigger_price(2, cur_price + delta_price)
                        global_info.event_image[2].set()

        def update_status(self):
                global global_info
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

                self.current_code = code
                if code == 'C':
                        if self.last_code == 'A' or self.last_code == 'B':
                                self.last_code = code
                                global_info.flag_gameover = True
                        return
                self.last_code = code

                ctime = info_val['ltime']
                stime = info_val['systime']
                price = info_val['price']

                try:
                        int_price = int(price)
                except:
                        return

                self.check_shot_price(int_price)
                self.check_image_time(stime, int_price)

        def main(self):
                self.udp_format.start()
                self.udp_format.wait_for_start()
                while True:
                        if self.flag_stop == True: break
                        self.update_status()

class udp_manager():
        def __init__(self, list_acount):
                self.list_acount = list_acount
                self.list_worker = []

                group = 0
                for account in self.list_acount :
                        group = 1 if group == 0 else 0
                        worker = udp_worker(account, group)
                        worker.start()
                        self.list_worker.append(worker)


udp_accounts = [
        {'bidno':'12345678', 'pid':'123456789012345678'},
        {'bidno':'12345677', 'pid':'123456789012345677'},
        {'bidno':'12345676', 'pid':'123456789012345676'},
        {'bidno':'12345675', 'pid':'123456789012345675'},
        ]

fd_udp = udp_manager(udp_accounts)

sleep(100)
