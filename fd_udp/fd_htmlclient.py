#!/usr/bin/env python3

from threading          import Event, Lock
from time               import time, sleep, localtime, mktime, strptime, strftime
from datetime           import datetime
from traceback          import print_exc, format_exc
from queue              import Queue, Empty

from pp_log             import printer
from pp_server          import server_dict
from pp_baseclass       import pp_thread
from pp_global          import pp_global_info
from pp_htmlproto       import proto_html

from fd_channel         import channel_center

#===========================================================

def time_sub(end, begin):
        return int(mktime(strptime('1970-01-01 '+end, '%Y-%m-%d %H:%M:%S'))) - int(mktime(strptime('1970-01-01 '+begin, '%Y-%m-%d %H:%M:%S')))

def getsleeptime(interval):
        return  interval - time()%interval


class fd_htmlinfo(pp_thread):

        def __init__(self, manager, group):
                global pp_global_info
                super().__init__()
                self.manager                = manager
                self.group                  = group
                self.proto                  = proto_html()
                self.timeout_find_channel   = pp_global_info.interval_html

        def check_game_over(self, cur_time):
                if time_sub(cur_time, '11:29:55') >= 0:
                        self.manager.event_gameover.set()

        def main(self):
                try:
                        self.do_html()
                except  KeyboardInterrupt:
                        pass
                except:
                        printer.critical(format_exc())

        def do_html(self):
                global  channel_center
                proto   = self.proto
                req     = self.proto.make_html_req()
                channel = 'query'

                while True:
                        group, handle = channel_center.get_channel(channel, self.timeout_find_channel, self.group)
                        if handle == None :
                                printer.error('group %d get channel Failed' % self.group)
                                return

                        head = proto.make_html_head(server_dict[group]['query']['name'])

                        info_val = channel_center.pyget(handle, req, head)

                        if info_val == False:
                                printer.error('group %d info channel error' % self.group)
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
                        printer.error('group %d body is None' % self.group)
                        return

                ack_val  = proto.parse_html_ack(info_val['body'])

                if ack_val == None:
                        printer.error('group %d ack is None' % self.group)
                        return

                self.manager.queue_html.put(ack_val)

                if 'systime' in ack_val:
                        self.check_game_over(ack_val['systime'])

                #print(ack_val)
                if ack_val['code'] == 'B' or ack_val['code'] == 'A':
                        printer.warning(sorted(ack_val.items()))


class fd_html_manager(pp_thread):
        def __init__(self):
                global pp_global_info
                super().__init__()
                self.interval_time  = pp_global_info.interval_html
                self.queue_html     = Queue()
                self.event_gameover = Event()

        def main(self):
                while True:
                        thread_html = [fd_htmlinfo(self, 0), fd_htmlinfo(self, 1)]
                        thread_html[1].start()
                        sleep(self.interval_time/2)
                        thread_html[0].start()
                        sleep(getsleeptime(self.interval_time))

html_manager = fd_html_manager()

def fd_html_init():
        global html_manager
        html_manager.start() 

#=================================================================================

if __name__ == '__main__':
        from pp_server      import pp_dns_init
        from pp_baseredis   import pp_redis_init
        from fd_channel     import fd_channel_init

        pp_dns_init()
        pp_redis_init()
        fd_channel_init()
        fd_html_init()
        try:
                html_manager.join()
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()
        print()

