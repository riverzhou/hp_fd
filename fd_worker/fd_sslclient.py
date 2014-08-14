#!/usr/bin/env python3

from threading              import Event
from time                   import sleep
from traceback              import print_exc

from fd_global              import global_info
from fd_channel             import channel_center
from fd_redis               import redis_worker
from fd_udpclient           import daemon_udp

from pp_baseclass           import pp_thread
from pp_sslproto            import proto_ssl, proto_machine
from pp_server              import server_dict

from pp_log                 import logger, printer

class fd_login():
        def __init__(self, client):
                self.client = client

        def do_login(self):
                global  channel_center
                proto   = self.client.proto
                req     = proto.make_login_req()
                while True:
                        channel_center.login_request_increase()
                        group, channel = channel_center.get_channel('login')
                        channel_center.login_request_decrease()
                        if channel == None:
                                continue
                        head = proto.make_ssl_head(server_dict[group]['login']['name'])
                        info_val = channel_center.pyget(channel, req, head)
                        if info_val == None:
                                continue
                        if info_val['status'] != 200 :
                                printer.error('client %s fd_login status %s' % (self.client.bidno, info_val['status']))
                                continue
                        ack_val   = proto.parse_login_ack(info_val['body'])
                        if 'pid' not in ack_val or 'name' not in ack_val:
                                printer.error('client %s fd_login ack error %s' % (self.client.bidno, str(info_val)))
                                continue
                        self.client.pid_login   = ack_val['pid']
                        self.client.name_login  = ack_val['name']
                        printer.warning('client %s login %s %s' % (self.client.bidno, ack_val['name'], ack_val['pid']))
                        break

class fd_image(pp_thread):
        image_timeout = 5 

        def __init__(self, client, count, price):
                super().__init__()
                self.client         = client
                self.count          = count
                self.price          = price
                self.event_finish   = Event()

        def main(self):
                while True :
                        try:
                                self.do_image()
                        except  KeyboardInterrupt:
                                break
                        except:
                                print_exc()
                                continue
                        else:
                                break

        def do_image(self):
                global  channel_center
                proto   = self.client.proto
                req     = proto.make_image_req(self.price)
                if self.count == 0:
                        channel = 'tb0'
                else:
                        channel = 'tb1'
                while True:
                        group, handle = channel_center.get_channel(channel)
                        if handle == None :
                                continue
                        head = proto.make_ssl_head(server_dict[group]['toubiao']['name'])
                        info_val = channel_center.pyget(handle, req, head)
                        if info_val == None :
                                continue
                        if info_val['status'] != 200 :
                                printer.error('client %s fd_image status %s' % (self.client.bidno, info_val['status']))
                                continue
                        ack_sid  = proto.get_sid_from_head(info_val['head'])
                        ack_val  = proto.parse_image_ack(info_val['body'])
                        if ack_sid == None or ack_sid == '':
                                continue
                        if 'image' not in ack_val:
                                printer.error('client %s fd_image ack error %s' % (self.client.bidno, str(info_val)))
                                continue
                        if ack_val['image'] == None or ack_val['image'] == '':
                                continue
                        self.client.sid_bid[self.count]     = ack_sid
                        self.client.picture_bid[self.count] = ack_val['image']
                        break
                self.event_finish.set()

        def wait_for_finish(self, timeout = None):
                waittime = timeout if timeout != None else self.image_timeout
                return self.event_finish.wait(waittime)

class fd_price(pp_thread):
        def __init__(self, client, count, price, group):
                super().__init__()
                self.client     = client
                self.count      = count
                self.price      = price
                self.group      = group

        def main(self):
                while True :
                        try:
                                self.do_price()
                        except  KeyboardInterrupt:
                                break
                        except:
                                print_exc()
                                continue
                        else:
                                break

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
                while True:
                        group, handle = channel_center.get_channel(channel, self.group)
                        if handle == None :
                                continue
                        head = proto.make_ssl_head(server_dict[group]['toubiao']['name'], sid)
                        info_val = channel_center.pyget(handle, req, head)
                        if info_val == None :
                                continue
                        if info_val['status'] != 200 :
                                printer.error('client %s fd_price status %s' % (self.client.bidno, info_val['status']))
                                continue
                        ack_val = proto.parse_price_ack(info_val['body'])
                        if 'price' in ack_val :
                                self.client.price_bid[self.count] = ack_val['price']
                        else:
                                printer.error('client %s fd_price ack error %s' % (self.client.bidno, str(info_val)))
                        break

class fd_decode(pp_thread):
        decode_timeout = 30

        def __init__(self, client, count, sid, picture):
                super().__init__()
                self.client         = client
                self.count          = count
                self.sid            = sid
                self.picture        = picture
                self.event_finish   = Event()

        def main(self):
                while True :
                        try:
                                self.do_decode()
                        except  KeyboardInterrupt:
                                break
                        except:
                                print_exc()
                                continue
                        else:
                                break

        def do_decode(self):
                global redis_worker
                redis_worker.put_request(self.sid, self.picture)
                self.client.number_bid[self.count] = redis_worker.get_result(self.sid)
                self.event_finish.set()

        def wait_for_finish(self, timeout = None):
                waittime = timeout if timeout != None else self.decode_timeout
                return self.event_finish.wait(waittime)

class fd_bid(pp_thread):
        bid_timeout = 2

        def __init__(self, client, count):
                super().__init__()
                self.client = client
                self.count  = count

        def main(self):
                while True:
                        try:
                                self.do_bid()
                        except  KeyboardInterrupt:
                                break
                        except:
                                print_exc()
                        else:
                                break

        def do_bid(self):
                global global_info

                global_info.event_image[self.count].wait()
                price = global_info.trigger_price[self.count]
                while True:
                        self.client.picture_bid[self.count] = None
                        image = fd_image(self.client, self.count, price)
                        image.start()
                        if image.wait_for_finish() != True :
                                continue
                        if self.client.sid_bid[self.count] == None or self.client.picture_bid[self.count] == None :
                                continue
                        self.client.number_bid[self.count] = None
                        decode = fd_decode(self.client, self.count, self.client.bidno+self.client.sid_bid[self.count], self.client.picture_bid[self.count])
                        decode.start()
                        if decode.wait_for_finish() != True :
                                continue
                        if self.client.number_bid[self.count] == None or self.client.number_bid[self.count] == '000000':
                                continue
                        break
                printer.warning('client %s bid %s image %s %s ' % (self.client.bidno, self.count, self.client.sid_bid[self.count], self.client.number_bid[self.count]))

                global_info.event_price[self.count].wait()
                self.client.price_bid[self.count] = None
                while True:
                        price = [fd_price(self.client, self.count, price, 0), fd_price(self.client, self.count, price, 1)]
                        price[0].start()
                        price[1].start()
                        sleep(self.bid_timeout)
                        if global_info.flag_gameover == True:
                                break
                        if self.client.price_bid[self.count] == None:
                                continue
                        break
                printer.warning('client %s bid %s price %s %s %s' % (self.client.bidno, self.count, self.client.price_bid[self.count], self.client.name_login, self.client.pid_login))

class fd_client(pp_thread):
        def __init__(self, bidno, passwd):
                super().__init__(bidno)
                self.bidno          = bidno
                self.passwd         = passwd
                self.machine        = proto_machine()
                self.proto          = proto_ssl(bidno, passwd, self.machine.mcode, self.machine.image)

                self.login          = fd_login(self)
                self.bid            = [fd_bid(self,0), fd_bid(self,1), fd_bid(self,2)]

                self.name_login     = None
                self.pid_login      = None
                self.sid_bid        = [None, None, None]
                self.picture_bid    = [None, None, None]
                self.number_bid     = [None, None, None]
                self.price_bid      = [None, None, None]

        def main(self):
                global daemon_udp
                self.login.do_login()
                daemon_udp.add((self.bidno, self.pid_login))

                self.bid[0].start()
                self.bid[0].wait_for_start()

                self.bid[1].start()
                self.bid[1].wait_for_start()

                self.bid[2].start()
                self.bid[2].wait_for_start()

                self.bid[0].wait_for_stop()
                self.bid[1].wait_for_stop()
                self.bid[2].wait_for_stop()

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
        #print_channel_number()

        print('client \tstarted')

        sleep(3)
        global_info.trigger_price[0] = 72600
        global_info.event_image[0].set()
        global_info.event_price[0].set()
        #print_channel_number()

        sleep(3)
        global_info.trigger_price[1] = 73000
        global_info.event_image[1].set()
        global_info.event_price[1].set()
        #print_channel_number()

        sleep(3)
        global_info.trigger_price[2] = 74000
        global_info.event_image[2].set()
        global_info.event_price[2].set()
        #print_channel_number()

        client.wait_for_stop()


