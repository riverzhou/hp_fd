#!/usr/bin/env python3

import sys

from socketserver       import UDPServer, BaseRequestHandler
from time               import time, sleep, localtime, mktime, strptime, strftime
from struct             import pack, unpack
from traceback          import print_exc
from hashlib            import md5
from xml.etree          import ElementTree
from threading          import Thread, Event, Lock, Semaphore
from queue              import Queue, Empty

from pp_baseclass       import pp_thread, pp_sender
from pp_log             import logger, printer

from pp_server          import pp_dns_init
from pp_baseredis       import pp_redis_init
from fd_channel         import fd_channel_init
from fd_htmlclient      import fd_html_init

from fd_htmlclient      import html_manager


#-------------------------------------------

UDP_SERVER =('0.0.0.0', 999)

Thread.daemon  = True
UDPServer.allow_reuse_address = True
UDPServer.request_queue_size  = 100

#================================================================================

def time_sub(end, begin):
        return int(mktime(strptime('1970-01-01 '+end, '%Y-%m-%d %H:%M:%S'))) - int(mktime(strptime('1970-01-01 '+begin, '%Y-%m-%d %H:%M:%S')))

def time_add(time, second):
        ret = strftime('%Y-%m-%d %H:%M:%S', localtime(int(mktime(strptime('1970-01-01 '+time, "%Y-%m-%d %H:%M:%S"))) + second))
        return ret.split()[1]

def getsleeptime(itime):
        return itime - time()%itime

def format_data(list_data):
        list_out = []
        for data in list_data :
                list_out.append((str(data[1]).split()[1], str(data[2])))
        return list_out

#================================================================================

class proto_udp():
        def decode(self, data):
                buff = b''
                len0 = len(data)
                len1 = len0 // 4
                len2 = len0 % 4
                if len2 != 0:
                        len1 += 1
                for i in range(4 - len2):
                        data += b'0'
                for i in range(len1) :
                        buff += pack('i', ~unpack('i', data[i*4:i*4+4])[0])
                buff = buff[0:len0]
                return buff

        def encode(self, data):
                buff = b''
                len0 = len(data)
                len1 = len0 // 4
                len2 = len0 % 4
                if len2 != 0:
                        len1 += 1
                for i in range(4 - len2):
                        data += b'0'
                for i in range(len1) :
                        buff += pack('i', ~unpack('i', data[i*4:i*4+4])[0])
                buff = buff[0:len0]
                return buff

        def udp_make_format_ack(self, key_val):
                return ( (
                        '<xml><TYPE>FORMAT</TYPE><INFO>\r\n' +
                        '拍卖会：%1%\r\n' +
                        '投放额度数：%2%\r\n' +
                        '本场拍卖会警示价：%3%\r\n' +
                        '拍卖会起止时间：%4%至%5%\r\n' +
                        '首次出价时段：%6%至%7%\r\n' +
                        '修改出价时段：%8%至%9%\r\n' +
                        '\r\n' +
                        '          目前为首次出价时段\r\n' +
                        '系统目前时间：%10%\r\n' +
                        '目前已投标人数：%11%\r\n' +
                        '目前最低可成交价：%12%\r\n' +
                        '最低可成交价出价时间：%13%\r\n' +
                        '#\r\n' +
                        '拍卖会：%1%\r\n' +
                        '投放额度数：%2%\r\n' +
                        '目前已投标人数：%3%\r\n' +
                        '拍卖会起止时间：%4%至%5%\r\n' +
                        '首次出价时段：%6%至%7%\r\n' +
                        '修改出价时段：%8%至%9%\r\n' +
                        '\r\n' +
                        '          目前为修改出价时段\r\n' +
                        '系统目前时间：%10%\r\n' +
                        '目前最低可成交价：%11%\r\n' +
                        '最低可成交价出价时间：%12%\r\n' +
                        '目前修改价格区间：%13%至%14%</INFO><xml>'
                        ).encode('gb18030') ,
                        key_val['addr']
                        )

        def parse_ack(self, string):
                key_val = {}
                try:
                        xml_string = '<XML>' + string.strip() + '</XML>'
                        root = ElementTree.fromstring(xml_string)
                        for child in root:
                                key_val[child.tag] = child.text
                except :
                        print(string)
                print(string)
                #print(sorted(key_val.items()))
                #print('')
                return key_val

        def udp_make_o_info(self, key_val):
                '''
                <TYPE>INFO</TYPE><INFO>C2014年5月24日上海市个人非营业性客车额度投标拍卖会已经结束！
                '''
                info = ( (
                        '\n<TYPE>INFO</TYPE><INFO>C%s上海市个人非营业性客车额度投标拍卖会已经结束！\r\n\r\n</INFO>\n\n\n\n\n\n\t\t\t'
                        ) % (
                        key_val['date']
                        ) )
                print(info)
                return info.encode('gb18030')

        def udp_make_x_info(self, key_val):
                '''
                <TYPE>INFO</TYPE><INFO>C2014年5月24日上海市个人非营业性客车额度投标拍卖会尚未开始。
                起止时间为：
                2014年5月24日10时30分0秒
                到2014年5月24日11时30分0秒

                系统目前时间：10:20:06</INFO>
                '''
                info = ( (
                        '\n<TYPE>INFO</TYPE><INFO>C%s上海市个人非营业性客车额度投标拍卖会尚未开始。\r\n起止时间为：\r\n%s10时30分0秒\r\n到%s11时30分0秒\r\n\r\n系统目前时间：%s</INFO>\n\n\n\n\n\n\t\t\t'
                        ) % (
                        key_val['date'],
                        key_val['date'],
                        key_val['date'],
                        key_val['systime']
                        ) )
                print(info)
                return info.encode('gb18030')

        def udp_make_y_info(self, key_val):
                '''
                <TYPE>INFO</TYPE><INFO>C2014年5月24日上海市个人非营业性客车额度投标拍卖会已经结束，稍后发布拍卖会结果，请等待！


                拍卖会结果也可通过本公司网站WWW.ALLTOBID.COM进行查询。</INFO>
                '''
                info = ( (
                        '\n<TYPE>INFO</TYPE><INFO>C%s上海市个人非营业性客车额度投标拍卖会已经结束，稍后发布拍卖会结果，请等待！\r\n\r\n拍卖会结果也可通过本公司网站WWW.ALLTOBID.COM进行查询。</INFO>\n\n\n\n\n\n\t\t\t'
                        ) % (
                        key_val['date']
                        ) )
                print(info)
                return info.encode('gb18030')

        def udp_make_a_info(self, key_val):
                '''
                <TYPE>INFO</TYPE><INFO>A2014年5月24日上海市个人非营业性客车额度投标拍卖会^7400^72600^10:30^11:30^10:30^11:00^11:00^11:30^10:30:13^8891^72600^10:30:13</INFO>
                '''
                info = ( (
                        '\n<TYPE>INFO</TYPE><INFO>A%s上海市个人非营业性客车额度投标拍卖会^%s^%s^10:30^11:30^10:30^11:00^11:00^11:30^%s^%s^%s^%s</INFO>\n\n\n\n\n\n\t\t\t'
                        ) % (
                        key_val['date'],
                        key_val['number_limit'],
                        key_val['price_limit'],
                        key_val['systime'],
                        key_val['number'],
                        key_val['price'],
                        key_val['lowtime']
                        ) )
                print(info)
                return info.encode('gb18030')

        def udp_make_b_info(self, key_val):
                '''
                <TYPE>INFO</TYPE><INFO>B2014年5月24日上海市个人非营业性客车额度投标拍卖会^7400^114121^10:30^11:30^10:30^11:00^11:00^11:30^11:00:14^72600^10:30:12^72300^72900</INFO>
                '''
                info = ( (
                        '\n<TYPE>INFO</TYPE><INFO>B%s上海市个人非营业性客车额度投标拍卖会^%s^%s^10:30^11:30^10:30^11:00^11:00^11:30^%s^%s^%s^%s^%s</INFO>\n\n\n\n\n\n\t\t\t'
                        ) % (
                        key_val['date'],
                        key_val['number_limit'],
                        key_val['number'],
                        key_val['systime'],
                        key_val['price'],
                        key_val['lowtime'],
                        str(int(key_val['price']) - 300),
                        str(int(key_val['price']) + 300),
                        ) )
                print(info)
                return info.encode('gb18030')

#------------------------------------------------------

class info_maker(pp_thread, proto_udp):
        #strftime('%H:%M:%S',localtime(time()))
        def __init__(self, info = ''):
                global pp_config
                pp_thread.__init__(self, info)
                proto_udp.__init__(self)
                self.addr_list = []
                self.lock_addr = Lock()

        def main(self):
                global html_manager

                while True:
                        key_val = html_manager.queue_html.get()
                        print(sorted(key_val.items()))
                        if key_val == None:
                                sleep(0.1)
                        if key_val['code'] == 'B':
                                self.make_b(key_val)
                                continue
                        if key_val['code'] == 'A':
                                self.make_a(key_val)
                                continue

        def make_a(self, key_val):
                global price_limit, number_limit
                if len(self.addr_list) == 0 :
                        return False
                self.make(self.udp_make_a_info(key_val))
                return True

        def make_b(self, key_val):
                global number_people, number_limit
                if len(self.addr_list) == 0 :
                        return False
                self.make(self.udp_make_b_info(key_val))
                return True

        def make(self, info):
                addr_list = []
                self.lock_addr.acquire()
                for addr in self.addr_list :
                        addr_list.append(addr)
                self.lock_addr.release()
                for addr in addr_list :
                        daemon_bs.put((info, addr))

        def reg(self, addr):
                self.lock_addr.acquire()
                if not addr in self.addr_list :
                        self.addr_list.append(addr)
                self.lock_addr.release()

        def unreg(self, addr):
                self.lock_addr.acquire()
                for i in range(len(self.addr_list)) :
                        if self.addr_list[i] == addr :
                                del(self.addr_list[i])
                                break
                self.lock_addr.release()

#------------------------------------------------------

class buff_sender(pp_sender):
        def proc(self, buff):  # buff 为 (info, addr)
                global server_udp, daemon_im
                info, addr = buff
                data = daemon_im.encode(info)
                server_udp.socket.sendto(data, addr)

#------------------------------------------------------

class udp_handle(BaseRequestHandler):
        def handle(self):
                global daemon_im
                proto_dict = {
                        'FORMAT' : self.proc_format ,
                        'LOGOFF' : self.proc_logoff ,
                        }
                string = self.get()
                key_val = daemon_im.parse_ack(string)
                key_val['addr'] = self.client_address
                try:
                        proc = proto_dict[key_val['TYPE']]
                except  KeyError:
                        pass
                except:
                        print_exc()
                else:
                        proc(key_val)

        def get(self):
                global daemon_im
                return daemon_im.decode(self.request[0]).decode('gb18030')

        def proc_logoff(self, key_val):
                global daemon_im
                daemon_im.unreg(key_val['addr'])

        def proc_format(self, key_val):
                global daemon_im, daemon_bs
                daemon_im.reg(key_val['addr'])
                daemon_bs.put(daemon_im.udp_make_format_ack(key_val))

class udp_server(pp_thread):
        def main(self):
                global server_udp
                server_udp.serve_forever()

#================================================================================

def main_init():
        pp_dns_init()
        pp_redis_init()
        fd_channel_init()
        fd_html_init()

def main():
        global daemon_im, daemon_bs, server_udp, UDP_SERVER

        main_init()

        server_udp = UDPServer(UDP_SERVER, udp_handle)

        daemon_im = info_maker()
        daemon_im.start()
        daemon_im.wait_for_start()
        daemon_bs = buff_sender()
        daemon_bs.start()
        daemon_bs.wait_for_start()
        daemon_us = udp_server()
        daemon_us.start()
        daemon_us.wait_for_start()

        logger.debug('UDP Server start at %s : %d' % (UDP_SERVER[0], UDP_SERVER[1]))
        print('UDP Server start at %s : %d' % (UDP_SERVER[0], UDP_SERVER[1]))
        daemon_im.join()

if __name__ == "__main__":
        try:
                main()
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()
        finally:
                print()

