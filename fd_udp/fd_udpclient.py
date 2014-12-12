#!/usr/bin/env python3

from threading              import Event, Lock
from time                   import sleep
from datetime               import datetime
from traceback              import print_exc, format_exc

from pp_log                 import printer
from pp_server              import server_dict
from pp_baseclass           import pp_thread
from pp_global              import pp_global_info

from fd_channel             import channel_center

#===========================================================

def time_sub(end, begin):
        try:
                e = datetime.timestamp(datetime.strptime(end,   '%Y-%m-%d %H:%M:%S.%f'))
                b = datetime.timestamp(datetime.strptime(begin, '%Y-%m-%d %H:%M:%S.%f'))
                return e-b
        except:
                return -1

class fd_udpinfo(pp_thread):
        req = 'carnetbidinfo.html'

        def __init__(self, group):
                super().__init__()
                self.group = group

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
                req     = self.req
                channel = 'query'

                while True:
                        group, handle = channel_center.get_channel(channel, self.group)
                        if handle == None :
                                printer.error('group %d get channel Failed' % self.group)
                                sleep(0.1)
                                continue

                        head = proto.make_query_head(server_dict[group]['query']['name'])

                        info_val = channel_center.pyget(handle, req, head)

                        if info_val == False:
                                printer.error('group %d  info channel error' % self.group)
                                sleep(0.1)
                                continue
                        else:
                                break

                if info_val == None :
                        printer.error('group %d info is None' % self.group)
                        return

                if info_val['status'] != 200:
                        printer.error('group %d status %s' % self.group)
                        return

                if info_val['body'] == '' or info_val['body'] == None:
                        printer.error('group body is None' % self.group)
                        return

                ack_val  = proto.parse_query_ack(info_val['body'])

                if ack_val == None:
                        printer.error('group %d ack is None' % self.group)
                        return

                daemon_im.queue_info.put(ack_val)


