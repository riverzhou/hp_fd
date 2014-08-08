#!/usr/bin/env python3


from datetime       import datetime
from socket         import socket, AF_INET, SOCK_DGRAM
from threading      import Lock
from time           import time, sleep, localtime, mktime, strptime, strftime

from pp_baseclass   import pp_thread
from pp_udpproto    import udp_proto
from pp_server      import server_dict

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
                super.__init__()

                self.bidno       = acount['bidno']
                self.pid         = acount['pid']
                self.group       = group

                self.server_addr = server_dict[group]['udp']['ip'], server_dict[group]['udp']['port']

                self.sock        = socket(AF_INET, SOCK_DGRAM)
                self.sock.settimeout(self.udp_timeout)
                self.sock.bind(('',0))

                self.proto       = udp_proto()
                self.udp_format  = udp_format(self)

        def stop(self):
                if self.udp_format != None : self.udp_format.stop()
                if self.sock != None:
                        self.logoff_udp()
                        try:
                                self.sock.close()
                        except:
                                pass
                self.sock       = None
                self.event_shot = None
                self.price_shot = 0
                self.flag_stop  = True
                self.event_stop.set()

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


        def check_shot_price(self, cur_price):
                if self.price_shot != 0 and self.event_shot != None and self.price_shot <= cur_price + 300 and self.price_shot >= cur_price - 300:
                        try:
                                self.event_shot.set()
                        except:
                                print_exc()

        def check_image_price(self, cur_price, cur_time):
                if self.list_trigger_time == None or self.list_trigger_event == None : return
                list_t = list(map(lambda t: time_sub(cur_time, t), self.list_trigger_time))
                for n in range(len(list_t)):
                        if list_t[n] > 0 and list_t[n] <= 3 :
                                self.list_trigger_event[n] = True

        def recv_udp(self):
                while True:
                        try:
                                if self.sock != None : udp_result = self.sock.recvfrom(1500)
                        except  (TimeoutError, OSError):
                                return None
                        except :
                                print_exc()
                                return None

                        if self.flag_stop == True:
                                return None

                        if udp_result[1] == self.server_addr:
                                return udp_result[0]

        def update_status(self):
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
                        '''set gameover'''
                        return

                ctime = info_val['ltime']
                stime = info_val['systime']
                price = info_val['price']

                try:
                        int_price = int(price)
                except:
                        return

                global global_info
                global_info.set_current_price(int_price)

                self.check_shot_price(int_price)
                self.check_image_price(int_price, stime)

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
                        worker = udp_worker(acount, group)
                        worker.start()
                        self.list_worker.append(worker)

class fd_client(pp_thread):
        pass



