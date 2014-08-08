#!/usr/bin/env python3

from fd_global          import global_info
from fd_channel         import channel_center
from fd_redis           import redis_worker

from pp_sslproto        import *

class fd_login():
        def __init__(self, client):
                self.client = client

        def do_login(self):
                global  channel_center
                proto   = self.client.proto
                req     = proto.make_login_req()
                while True:
                        channel = channel_center.get_channel()
                        if channel == None :
                                continue
                        head = proto.make_ssl_head(server_dict[channel.group]['login'])
                        if channel.https_write(req, head) == False :
                                continue
                        info_val  = channel.https_read()
                        if info_val == None :
                                continue
                        if info_val['status'] != '200' :
                                continue
                        #ack_sid   = proto.get_sid_from_head(info_val['head'])
                        ack_val   = proto.parse_login_ack(info_val['body'])
                        if 'pid' not in ack_val :
                                continue
                        self.client.pid_login   = ack_val['pid']
                        self.client.name_login  = ack_val['name']
                        break

class fd_image(pp_subthread):
        image_timeout = 5 
        def __init__(self, client, count, price):
                self.client = client
                self.count  = count
                self.price  = price
                self.event_finish = Event()

        def main(self):
                while True :
                        try:
                                self.do_image()
                        except  KeyboardInterrupt:
                                break
                        except:
                                continue
                        else:
                                break

        def do_image(self):
                global  channel_center
                proto   = self.client.proto
                req     = proto.make_image_req(self.price)
                while True:
                        channel = channel_center.get_channel()
                        if channel == None :
                                continue
                        head = proto.make_ssl_head(server_dict[channel.group]['toubiao'])
                        if channel.https_write(req, head) == False :
                                continue
                        info_val  = channel.https_read()
                        if info_val == None :
                                continue
                        if info_val['status'] != '200' :
                                continue
                        ack_sid   = proto.get_sid_from_head(info_val['head'])
                        ack_val   = proto.parse_image_ack(info_val['body'])
                        if ack_sid == None or ack_sid == '' :
                                continue
                        if 'image' not in ack_val :
                                continue
                        if ack_val['image'] == None or ack_val['image'] == '' :
                                continue
                        self.client.sid_bid[self.count]     = ack_sid
                        self.client.picture_bid[self.count] = ack_val['image']
                        break
                self.event_finish.set()

        def wait_for_finish(self, timeout = None):
                waittime = timeout if timeout != None else self.image_timeout
                return self.event_finish.wait(waittime)

        def close(self):
                pass

class fd_price(pp_subthread):
        def __init__(self, client, count, price, group):
                self.client = client
                self.count  = count
                self.price  = price
                self.group  = group

        def main(self):
                while True :
                        try:
                                self.do_price()
                        except  KeyboardInterrupt:
                                break
                        except:
                                continue
                        else:
                                break

        def do_price(self):
                global channel_center
                proto   = self.client.proto
                sid     = self.client.sid_bid[self.count]
                number  = self.client.number_bid[self.count]
                req     = proto.make_price_req(self.price, number)
                while True:
                        channel = channel_center.get_channel()
                        if channel == None :
                                continue
                        head = proto.make_ssl_head(server_dict[channel.group]['toubiao'], sid)
                        if channel.https_write(req, head) == False :
                                continue
                        info_val  = channel.https_read()
                        if info_val == None :
                                continue
                        if info_val['status'] != '200' :
                                continue
                        ack_val   = proto.parse_price_ack(info_val['body'])
                        if 'price' in ack_val :
                                self.client.price_bid[self.count] = ack_val['price']
                        break

        def close(self):
                pass

class fd_decode(pp_subthread):
        image_timeout = 20 

        def __init__(self, client, count, sid, picture):
                self.client     = client
                self.count      = count
                self.sid        = sid
                self.picture    = picture

        def main(self):
                while True :
                        try:
                                self.do_decode()
                        except  KeyboardInterrupt:
                                break
                        except:
                                continue
                        else:
                                break

        def do_decode(self):
                global redis_worker
                redis_worker.write_picture(sid, picture)
                number = redis_worker.read_number(sid)
                self.client.number_bid[self.count] = number
                self.event_finish.set()

        def wait_for_finish(self, timeout = None):
                waittime = timeout if timeout != None else self.image_timeout
                return self.event_finish.wait(waittime)

class fd_bid(pp_subthread):
        bid_timeout = 2

        def __init__(self, client, count):
                self.client = client
                self.count  = count

        def main(self):
                while True :
                        try :
                                self.do_bid()
                        except  KeyboardInterrupt:
                                break
                        except :
                                pass
                        else :
                                break

        def do_bid(self):
                global global_info

                global_info.event_image[self.count].wait()
                price = global_info.price_bid[self.count]
                while True:
                        self.client.picture_bid[self.count] = None
                        image = fd_image(self.client, self.count, price)
                        image.start()
                        if image.wait_for_finish() != True or self.client.sid_bid[self.count] == None or self.client.picture_bid[self.count] == None :
                                #image.close()
                                continue
                        self.client.number_bid[self.count] = None
                        decode = fd_decode(self.client, self.count, self.client.sid_bid[self.count], self.client.picture_bid[self.count])
                        decode.start()
                        if decode.wait_for_finish() != True or self.client.number_bid[self.count] == None:
                                #decode.close()
                                continue
                        break

                global_info.event_price[self.count].wait()
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

class fd_client(pp_subthread):
        def __init__(self, bidno, passwd):
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
                while True :
                        if self.login.do_login() == True :
                                break
                        sleep(1)

                self.bid[0].start()
                self.bid[0].wait_for_start()

                self.bid[1].start()
                self.bid[1].wait_for_start()

                self.bid[2].start()
                self.bid[2].wait_for_start()

                self.event_stop.wait()


