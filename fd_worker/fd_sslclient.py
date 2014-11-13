#!/usr/bin/env python3

from threading              import Event, Lock
from time                   import sleep
from datetime               import datetime
from traceback              import print_exc, format_exc

from pp_log                 import printer
from pp_sslproto            import proto_ssl, proto_machine
from pp_server              import server_dict
from pp_baseclass           import pp_thread
from pp_global              import pp_global_info

from fd_channel             import channel_center
from fd_decode              import decode_worker
from fd_udpclient           import daemon_udp

#===========================================================

def time_sub(end, begin):
        try:
                e = datetime.timestamp(datetime.strptime(end,   '%Y-%m-%d %H:%M:%S.%f'))
                b = datetime.timestamp(datetime.strptime(begin, '%Y-%m-%d %H:%M:%S.%f'))
                return e-b
        except:
                return -1

class fd_login():
        max_retry_login     = 3

        def __init__(self, client):
                self.client             = client

        def do_login(self):
                try:
                        for i in range(self.max_retry_login):
                                if self.proc_login() == True:
                                        return True
                                else:
                                        sleep(1)
                        return False
                except:
                        printer.critical(format_exc())
                        return False

        def proc_login(self):
                global  channel_center

                proto   = self.client.proto
                req     = proto.make_login_req()

                channel_center.login_request_increase()
                group, channel = channel_center.get_channel('login')
                channel_center.login_request_decrease()
                if channel == None:
                        printer.error('client %s fd_login get channel Failed' % self.client.bidno)
                        return False

                head = proto.make_ssl_head(server_dict[group]['login']['name'])

                self.client.check_login_interval()
                info_val = channel_center.pyget(channel, req, head)
                if info_val == None:
                        printer.error('client %s fd_login info is None' % self.client.bidno)
                        return False
                if info_val['status'] != 200:
                        printer.error('client %s fd_login status %s' % (self.client.bidno, info_val['status']))
                        return False
                if info_val['body'] == '' or info_val['body'] == None:
                        printer.error('client %s fd_login body is None' % self.client.bidno)
                        return False

                ack_val   = proto.parse_login_ack(info_val['body'])
                if ack_val == None:
                        printer.error('client %s fd_login ack is None' % self.client.bidno)
                        return False
                if 'pid' not in ack_val or 'name' not in ack_val:
                        printer.error('client %s fd_login ack error %s' % (self.client.bidno, str(info_val)))
                        return False

                self.client.pid_login   = ack_val['pid']
                self.client.name_login  = ack_val['name']
                printer.warning('client %s login %s %s' % (self.client.bidno, ack_val['name'], ack_val['pid']))
                return True

class fd_image(pp_thread):
        max_retry               = 2

        def __init__(self, client, count, price, image_timeout):
                super().__init__()
                self.client             = client
                self.count              = count
                self.price              = price
                self.event_finish       = Event()
                self.flag_timeout       = False
                self.lock_timeout       = Lock()
                self.flag_error         = False
                self.image_timeout      = image_timeout

        def main(self):
                try:
                        self.do_image()
                except  KeyboardInterrupt:
                        pass
                except:
                        printer.critical(format_exc())

        def do_image(self):
                global  channel_center
                proto   = self.client.proto
                req     = proto.make_image_req(self.price)
                if self.count == 0:
                        channel = 'tb0'
                else:
                        channel = 'tb1'

                for i in range(self.max_retry):
                        group, handle = channel_center.get_channel(channel)
                        if handle == None :
                                printer.error('client %s bid %d fd_image get channel Failed' % (self.client.bidno, self.count))
                                continue

                        head = proto.make_ssl_head(server_dict[group]['toubiao']['name'])

                        self.client.check_image_interval()
                        info_val = channel_center.pyget(handle, req, head)
                        if info_val == None :
                                printer.error('client %s bid %d fd_image info is None' % (self.client.bidno, self.count))
                                continue
                        if info_val['status'] != 200:
                                printer.error('client %s bid %d fd_image status %s' % (self.client.bidno, self.count, info_val['status']))
                                continue
                        if info_val['body'] == '' or info_val['body'] == None:
                                printer.error('client %s bid %d fd_image body is None' % (self.client.bidno, self.count))
                                continue

                        ack_sid  = proto.get_sid_from_head(info_val['head'])
                        ack_val  = proto.parse_image_ack(info_val['body'])
                        if ack_val == None:
                                printer.error('client %s bid %d fd_image ack is None' % (self.client.bidno, self.count))
                                self.flag_error = True
                                self.event_finish.set()
                                return
                        if ack_sid == None or ack_sid == '':
                                printer.error('client %s bid %d fd_image sid is None' % (self.client.bidno, self.count))
                                self.flag_error = True
                                self.event_finish.set()
                                return
                        if 'image' not in ack_val:
                                printer.error('client %s bid %d fd_image ack error %s' % (self.client.bidno, self.count, str(info_val)))
                                self.flag_error = True
                                self.event_finish.set()
                                return
                        if ack_val['image'] == None or ack_val['image'] == '':
                                printer.error('client %s bid %d fd_image image is None' % (self.client.bidno, self.count))
                                self.flag_error = True
                                self.event_finish.set()
                                return

                        self.lock_timeout.acquire()
                        if self.flag_timeout == False:
                                self.client.sid_bid[self.count]     = ack_sid
                                self.client.picture_bid[self.count] = ack_val['image']
                        self.lock_timeout.release()
                        self.event_finish.set()
                        return

                printer.error('client %s bid %d fd_image got max_retry %d' % (self.client.bidno, self.count, self.max_retry))
                self.flag_error = True
                self.event_finish.set()
                return

        def wait_for_finish(self, timeout = None):
                waittime = timeout if timeout != None else self.image_timeout
                if self.event_finish.wait(waittime) == True:
                        if self.flag_error == False:
                                return True
                        else:
                                return False
                else:
                        self.lock_timeout.acquire()
                        self.flag_timeout = True
                        self.lock_timeout.release()
                        printer.error('client %s bid %d fd_image Timeout' % (self.client.bidno, self.count))
                        sleep(0)
                        return False


class fd_price(pp_thread):
        max_retry               = 1
        min_self_interval       = 1

        def __init__(self, client, count, price, group):
                super().__init__()
                self.client             = client
                self.count              = count
                self.price              = price
                self.group              = group
                self.time_self_lastreq  = None

        def main(self):
                try:
                        self.do_price()
                except  KeyboardInterrupt:
                        pass
                except:
                        printer.critical(format_exc())

        def check_self_interval(self):
                curtime = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if self.time_self_lastreq == None:
                        self.time_self_lastreq = curtime
                        return True
                sleeptime = self.min_self_interval - time_sub(curtime, self.time_self_lastreq)
                self.time_self_lastreq = curtime
                if sleeptime > 0:
                        sleep(sleeptime)
                return True

        def do_price(self):
                global channel_center
                proto   = self.client.proto
                sid     = self.client.sid_bid[self.count]
                number  = self.client.number_bid[self.count]
                req     = proto.make_price_req(self.price, number)
                if self.count == 0:
                        channel = 'tb0'
                else:
                        channel = 'tb1'

                for i in range(self.max_retry):
                        group, handle = channel_center.get_channel(channel, self.group)
                        if handle == None :
                                printer.error('client %s bid %d fd_price get channel Failed' % (self.client.bidno, self.count))
                                continue

                        head = proto.make_ssl_head(server_dict[group]['toubiao']['name'], sid)

                        #self.check_self_interval()
                        info_val = channel_center.pyget(handle, req, head)
                        if info_val == None :
                                printer.error('client %s bid %d fd_price info is None' % (self.client.bidno, self.count))
                                continue
                        if info_val['status'] != 200 :
                                printer.error('client %s bid %d fd_price status %s' % (self.client.bidno, self.count, info_val['status']))
                                continue
                        if info_val['body'] == '' or info_val['body'] == None:
                                printer.error('client %s bid %d fd_price body is None' % (self.client.bidno, self.count))
                                continue

                        ack_val = proto.parse_price_ack(info_val['body'])
                        if ack_val == None:
                                printer.error('client %s bid %d fd_price ack is None' % (self.client.bidno, self.count))
                                return
                        if 'errcode' in ack_val:
                                printer.error('client %s bid %d fd_price ack error %s' % (self.client.bidno, self.count, str(ack_val)))
                                if ack_val['errcode'] == '112':
                                        self.client.set_err_112(self.count)
                                return
                        if 'price' not in ack_val :
                                printer.error('client %s bid %d fd_price ack error %s' % (self.client.bidno, self.count, str(ack_val)))
                                return
                        self.client.set_price_bid(self.count, ack_val['price'])
                        return


class fd_decode(pp_thread):

        def __init__(self, client, count, sid, picture):
                global pp_global_info
                super().__init__()
                self.client             = client
                self.count              = count
                self.sid                = sid
                self.picture            = picture
                self.event_finish       = Event()
                self.flag_timeout       = False
                self.lock_timeout       = Lock()
                self.type_decode        = pp_global_info.type_decode[count]
                self.timeout_decode     = pp_global_info.timeout_decode[count]

        def main(self):
                try:
                        self.do_decode()
                except  KeyboardInterrupt:
                        pass
                except:
                        printer.critical(format_exc())

        def do_decode(self):
                global decode_worker
                decode_worker.put_request(self.sid, self.type_decode, self.timeout_decode, self.picture)
                number = decode_worker.get_result(self.sid)
                self.lock_timeout.acquire()
                if self.flag_timeout == False:
                        self.client.number_bid[self.count] = number
                self.lock_timeout.release()
                self.event_finish.set()
                return

        def wait_for_finish(self, timeout = None):
                waittime = timeout if timeout != None else self.timeout_decode
                if self.event_finish.wait(waittime+2) == True:                  # XXX 多等待2秒
                        return True
                else:
                        self.lock_timeout.acquire()
                        self.flag_timeout = True
                        self.lock_timeout.release()
                        printer.error('client %s bid %d fd_decode Timeout' % (self.client.bidno, self.count))
                        sleep(0)
                        return False


class fd_bid():
        max_retry_image             = 3
        max_retry_price             = 2

        count                       = 0     # 在子类中重写此参数
        max_image_timeout           = 0     # 在子类中重写此参数
        max_price_timeout           = 0     # 在子类中重写此参数

        def __init__(self, client):
                self.client             = client
                self.price              = None

        def do_bid(self):
                try:
                        return self.proc_bid()
                except:
                        printer.critical(format_exc())
                        return False

        def proc_bid(self):
                if self.proc_image() != True:
                        printer.warning('client %s bid %s image Failed' % (self.client.bidno, self.count))
                        return False
                printer.warning('client %s bid %s image %s %s ' % (self.client.bidno, self.count, self.client.sid_bid[self.count], self.client.number_bid[self.count]))

                if self.proc_price() != True:
                        printer.warning('client %s bid %s price Failed' % (self.client.bidno, self.count))
                        return False
                printer.warning('client %s bid %s price %s %s %s' % (self.client.bidno, self.count, self.client.price_bid[self.count], self.client.name_login, self.client.pid_login))

                return  True

        def proc_image(self):
                global pp_global_info

                pp_global_info.event_image[self.count].wait()
                self.price = pp_global_info.trigger_price[self.count]
                if self.price == None:
                        printer.warning('client %s bid %s price is None , should be too high' % (self.client.bidno, self.count))
                        return False
                if self.count == 2:
                        try:
                                price1 = int(self.client.check_price_bid(1))
                        except:
                                price1 = None
                        if price1 != None and price1 >= self.price:
                                printer.warning('client %s bid 2 price lower than bid 1 ' % self.client.bidno)
                                return False

                for i in range(self.max_retry_image):
                        self.client.check_image_interval(False)
                        self.client.picture_bid[self.count] = None
                        self.client.sid_bid[self.count]     = None
                        thread_image = fd_image(self.client, self.count, self.price, self.max_image_timeout)
                        thread_image.start()
                        if thread_image.wait_for_finish() != True :
                                continue
                        if self.client.sid_bid[self.count] == None or self.client.picture_bid[self.count] == None :
                                continue

                        self.client.number_bid[self.count] = None
                        thread_decode = fd_decode(self.client, self.count, self.client.bidno+self.client.sid_bid[self.count], self.client.picture_bid[self.count])
                        thread_decode.start()
                        if thread_decode.wait_for_finish() != True :
                                continue
                        if self.client.number_bid[self.count] != None and self.client.number_bid[self.count] != '000000':
                                return True
                        else:
                                printer.error('client %s bid %d proc_image decode 000000' % (self.client.bidno, self.count))

                return False

        def proc_price(self):
                global pp_global_info

                pp_global_info.event_price[self.count].wait()
                if self.price == None:
                        printer.warning('client %s bid %s price is None , should be too high' % (self.client.bidno, self.count))
                        return False
                for i in range(self.max_retry_price):
                        thread_price = [fd_price(self.client, self.count, self.price, 0), fd_price(self.client, self.count, self.price, 1)]
                        thread_price[0].start()
                        thread_price[1].start()
                        self.client.check_price_interval()
                        if pp_global_info.flag_gameover == True:
                                break
                        if self.client.check_err_112(self.count) == True:
                                printer.warning('client %s bid %s price %s meet err_112 %s %s' % (self.client.bidno, self.count, self.price, self.client.name_login, self.client.pid_login))
                                break
                        if self.client.check_price_bid(self.count) != None:
                                return True

                self.client.wait_price_bid(self.count, self.max_price_timeout)
                if self.client.check_price_bid(self.count) != None:
                        return True
                else:
                        return False


class fd_bid_0(fd_bid):
        count               = 0
        max_image_timeout   = 10
        max_price_timeout   = 30

class fd_bid_1(fd_bid):
        count               = 1
        max_image_timeout   = 4
        max_price_timeout   = 2

class fd_bid_2(fd_bid):
        count               = 2
        max_image_timeout   = 3
        max_price_timeout   = 10

class fd_client(pp_thread):
        min_login_interval  = 3
        min_image_interval  = 3
        min_price_interval  = 2

        max_retry_bid0      = 20
        timewait_bid1       = 3

        def __init__(self, bidno, passwd):
                super().__init__(bidno)
                self.bidno          = bidno
                self.passwd         = passwd
                self.machine        = proto_machine()
                self.proto          = proto_ssl(bidno, passwd, self.machine.mcode, self.machine.image)

                self.err_112        = [False, False, False]
                self.name_login     = None
                self.pid_login      = None
                self.sid_bid        = [None, None, None]
                self.picture_bid    = [None, None, None]
                self.number_bid     = [None, None, None]
                self.price_bid      = [None, None, None]
                self.lock_bid       = [Lock(),  Lock(),  Lock()]
                self.event_bid      = [Event(), Event(), Event()]

                self.time_login_lastreq = None
                self.time_image_lastreq = None
                self.time_price_lastreq = None

        def check_login_interval(self):
                curtime = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if self.time_login_lastreq == None:
                        self.time_login_lastreq  = curtime
                        return True
                sleeptime = self.min_login_interval - time_sub(curtime, self.time_login_lastreq)
                self.time_login_lastreq = curtime
                if sleeptime > 0:
                        sleep(sleeptime)
                return True

        def check_image_interval(self, update = True):
                curtime = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if self.time_image_lastreq == None:
                        if update == True:
                                self.time_image_lastreq = curtime
                        return True
                sleeptime = self.min_image_interval - time_sub(curtime, self.time_image_lastreq)
                if update == True:
                        self.time_image_lastreq = curtime
                if sleeptime > 0:
                        sleep(sleeptime)
                return True

        def check_price_interval(self):
                curtime = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if self.time_price_lastreq == None:
                        self.time_price_lastreq = curtime
                        return True
                sleeptime = self.min_price_interval - time_sub(curtime, self.time_price_lastreq)
                self.time_price_lastreq = curtime
                if sleeptime > 0:
                        sleep(sleeptime)
                return True

        def do_login(self):
                login = fd_login(self)
                if login.do_login() != True:
                        printer.warning('client %s login failed. Abort.....' % self.bidno)
                        return False
                else:
                        daemon_udp.add((self.bidno, self.pid_login))
                        return True

        def do_bid0(self):
                bid0 = fd_bid_0(self)
                if bid0.do_bid() != True:
                        printer.warning('client %s bid 0 failed. Abort.....' % self.bidno)
                        return False
                return True

        def do_bid1(self):
                bid1 = fd_bid_1(self)
                if bid1.do_bid() != True:
                        printer.warning('client %s bid 1 failed. Abort.....' % self.bidno)
                        return False
                sleep(self.timewait_bid1)
                return True

        def do_bid2(self):
                global pp_global_info
                if pp_global_info.flag_gameover == True:
                        return False
                if pp_global_info.trigger_image[2][0] == None or pp_global_info.trigger_image[2][1] == None:
                        return False
                bid2 = fd_bid_2(self)
                if bid2.do_bid() != True:
                        printer.warning('client %s bid 2 failed. Abort.....' % self.bidno)
                        return False
                return True

        def set_bid0_finish(self):
                global pp_global_info
                return pp_global_info.set_bid0_finish()

        def main(self):
                global pp_global_info, daemon_udp

                self.do_login()

                i = 0
                maxretry = self.max_retry_bid0
                while True:
                        try:
                                maxretry = int(pp_global_info.maxretry_bid0)
                        except:
                                maxretry = self.max_retry_bid0
                        if i > maxretry:
                                break
                        else:
                                i += 1
                        self.do_bid0()
                        if self.check_bid0_finish() == True:
                                break

                self.set_bid0_finish()

                self.do_bid1()

                self.do_bid2()

                sleep(10)
                printer.warning('client %s bids finished. price : %s . Quit.....' % (self.bidno, str(self.price_bid)))
                return

        def wait_price_bid(self, count, timeout):
                return self.event_bid[count].wait(timeout)

        def check_err_112(self, count):
                return self.err_112[count]

        def check_price_bid(self, count):
                return self.price_bid[count]

        def set_err_112(self, count):
                self.lock_bid[count].acquire()
                self.err_112[count] = True
                #self.event_bid[count].set()
                self.lock_bid[count].release()
                return True

        def set_price_bid(self, count, price):
                self.lock_bid[count].acquire()
                self.price_bid[count] = price
                if price != None:
                        self.event_bid[count].set()
                self.lock_bid[count].release()
                return price

        def check_bid0_finish(self):
                if self.price_bid[0] != None:
                        return True
                if self.err_112[0] == True:
                        return True
                return False

