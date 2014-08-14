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
from pp_log                 import logger, printer

from fd_global              import global_info

#=================================================

def time_sub(end, begin):
        e = end.split(':')
        b = begin.split(':')
        return (int(e[0])*3600 + int(e[1])*60 + int(e[2])) - (int(b[0])*3600 + int(b[1])*60 + int(b[2]))


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

                self.server_addr    = server_dict[group]['udp']['ip'], server_dict[group]['udp']['port']

                self.sock           = socket(AF_INET, SOCK_DGRAM)
                self.sock.settimeout(self.udp_timeout)
                self.sock.bind(('',0))

                self.proto          = udp_proto()
                self.udp_format     = udp_format(self)


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

        def check_game_over(self, cur_time):
                global global_info
                if cur_time == None:
                        global_info.set_game_over()

        def check_create_channel(self, cur_time):
                global global_info
                time_delta = (time_sub(cur_time, global_info.trigger_channel_second[0]), time_sub(cur_time, global_info.trigger_channel_second[1]))
                if time_delta[0] >= 0 and time_delta[0] <= 60:
                        global_info.flag_create_toubiao[1] = True
                        return
                if time_delta[1] >= 0 and time_delta[1] <= 60:
                        global_info.flag_create_toubiao[1] = False
                        return

                time_delta = (time_sub(cur_time, global_info.trigger_channel_first[0]), time_sub(cur_time, global_info.trigger_channel_first[1]))
                if time_delta[0] >= 0 and time_delta[0] <= 60:
                        global_info.flag_create_toubiao[0] = True
                        return
                if time_delta[1] >= 0 and time_delta[1] <= 60:
                        global_info.flag_create_toubiao[0] = False
                        return

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

                stime = info_val['systime']

                if code == 'C':
                        self.check_game_over(stime)
                        return

                price = info_val['price']

                self.check_create_channel(stime)

                int_price = int(price)

                self.check_shot_price(int_price)
                self.check_image_time(stime, int_price)

        def main(self):
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
                                sleep(0)

class udp_manager(pp_thread):
        max_count_worker = 4

        def __init__(self):
                super().__init__()
                self.count_worker   = 0
                self.lock_worker    = Lock()
                self.queue_worker   = Queue()
                self.list_worker    = []

        def main(self):
                group = 0
                while True:
                        account = self.queue_worker.get()
                        group = 1 if group == 0 else 0
                        worker = udp_worker(account, group)
                        self.list_worker.append(worker)
                        worker.start()

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


if __name__ == '__main__':
        fd_udp_init()
        daemon_udp.wait_for_stop()
