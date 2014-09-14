#!/usr/bin/env python3

from threading              import Event, Lock
from time                   import sleep
from traceback              import print_exc, format_exc

from fd_global              import global_info
from fd_channel             import channel_center
from fd_image               import redis_worker
from fd_udpclient           import daemon_udp

from pp_baseclass           import pp_thread
from pp_sslproto            import proto_ssl, proto_machine
from pp_server              import server_dict

from pp_log                 import logger, printer

class fd_login():
        max_retry_login = 5

        def __init__(self, client):
                self.client = client

        def do_login(self):
                try:
                        for i in range(self.max_retry_login):
                                if self.proc_login() == True:
                                        return True
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
        max_retry       = 2
        image_timeout   = 5

        def __init__(self, client, count, price):
                super().__init__()
                self.client         = client
                self.count          = count
                self.price          = price
                self.event_finish   = Event()
                self.flag_timeout   = False
                self.lock_timeout   = Lock()
                self.flag_error     = False

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


class fd_decode(pp_thread):
        decode_timeout  = 15

        def __init__(self, client, count, sid, picture):
                super().__init__()
                self.client         = client
                self.count          = count
                self.sid            = sid
                self.picture        = picture
                self.event_finish   = Event()
                self.flag_timeout   = False
                self.lock_timeout   = Lock()

        def main(self):
                try:
                        self.do_decode()
                except  KeyboardInterrupt:
                        pass
                except:
                        printer.critical(format_exc())

        def do_decode(self):
                global redis_worker
                redis_worker.put_request(self.sid, self.picture)
                number = redis_worker.get_result(self.sid)
                self.lock_timeout.acquire()
                if self.flag_timeout == False:
                        self.client.number_bid[self.count] = number
                self.lock_timeout.release()
                self.event_finish.set()
                return

        def wait_for_finish(self, timeout = None):
                waittime = timeout if timeout != None else self.decode_timeout
                if self.event_finish.wait(waittime) == True:
                        return True
                else:
                        self.lock_timeout.acquire()
                        self.flag_timeout = True
                        self.lock_timeout.release()
                        printer.error('client %s bid %d fd_decode Timeout' % (self.client.bidno, self.count))
                        sleep(0)
                        return False


class fd_price(pp_thread):
        max_retry       = 2

        def __init__(self, client, count, price, group):
                super().__init__()
                self.client     = client
                self.count      = count
                self.price      = price
                self.group      = group

        def main(self):
                try:
                        self.do_price()
                except  KeyboardInterrupt:
                        pass
                except:
                        printer.critical(format_exc())

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
                                        self.client.err_112[self.count] = True
                                return
                        if 'price' not in ack_val :
                                printer.error('client %s bid %d fd_price ack error %s' % (self.client.bidno, self.count, str(ack_val)))
                                return
                        self.client.price_bid[self.count] = ack_val['price']
                        return


class fd_bid():
        bid_timeout     = 3
        max_retry_image = 3
        max_retry_price = 2

        def __init__(self, client, count):
                self.client = client
                self.count  = count
                self.price  = None

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
                global global_info

                global_info.event_image[self.count].wait()
                self.price = global_info.trigger_price[self.count]
                if self.price == None:
                        return False
                for i in range(self.max_retry_image):
                        self.client.picture_bid[self.count] = None
                        self.client.sid_bid[self.count]     = None
                        thread_image = fd_image(self.client, self.count, self.price)
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

                return False

        def proc_price(self):
                global global_info

                global_info.event_price[self.count].wait()
                self.client.price_bid[self.count] = None
                if self.price == None:
                        return False
                for i in range(self.max_retry_price):
                        thread_price = [fd_price(self.client, self.count, self.price, 0), fd_price(self.client, self.count, self.price, 1)]
                        thread_price[0].start()
                        thread_price[1].start()
                        sleep(self.bid_timeout)
                        if global_info.flag_gameover == True:
                                break
                        if self.client.err_112[self.count] == True:
                                printer.warning('client %s bid %s price %s meet err_112 %s %s' % (self.client.bidno, self.count, self.price, self.client.name_login, self.client.pid_login))
                                sleep(self.bid_timeout)
                                break
                        if self.client.price_bid[self.count] != None:
                                return True

                if self.client.price_bid[self.count] != None:
                        return True
                else:
                        return False

class fd_client(pp_thread):
        def __init__(self, bidno, passwd):
                super().__init__(bidno)
                self.bidno          = bidno
                self.passwd         = passwd
                self.machine        = proto_machine()
                self.proto          = proto_ssl(bidno, passwd, self.machine.mcode, self.machine.image)

                self.err_112        = [False, False]
                self.name_login     = None
                self.pid_login      = None
                self.sid_bid        = [None, None]
                self.picture_bid    = [None, None]
                self.number_bid     = [None, None]
                self.price_bid      = [None, None]

        def main(self):
                global daemon_udp

                login = fd_login(self)
                if login.do_login() != True:
                        printer.warning('client %s login failed. Abort.....' % self.bidno)
                        return

                daemon_udp.add((self.bidno, self.pid_login))

                bid0 = fd_bid(self,0)
                if bid0.do_bid() != True:
                        printer.warning('client %s bid 0 failed. Abort.....' % self.bidno)
                        return

                bid1 = fd_bid(self,1)
                if bid1.do_bid() != True:
                        printer.warning('client %s bid 1 failed. Abort.....' % self.bidno)
                        return

                sleep(10)
                printer.warning('client %s bids finished. Quit.....' % self.bidno)
                return


#================================================

if __name__ == '__main__':
        from fd_channel import fd_channel_init, fd_channel_test, print_channel_number
        from fd_redis   import fd_redis_init
        from pp_server  import pp_dns_init
        global global_info

        pp_dns_init()
        fd_redis_init()
        fd_channel_init()

        fd_channel_test()

        client = fd_client('12345678','1234')
        client.start()
        client.wait_for_start()

        print('client \tstarted')

        sleep(3)
        global_info.trigger_price[0] = 72600
        global_info.event_image[0].set()
        global_info.event_price[0].set()

        sleep(3)
        global_info.trigger_price[1] = 74000
        global_info.event_image[1].set()
        global_info.event_price[1].set()

        client.wait_for_stop()


