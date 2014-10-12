#!/usr/bin/env python3

from traceback              import print_exc
from time                   import sleep

from pp_log                 import logger, printer
from pp_server              import pp_dns_init

from fd_config              import list_account, redis_dbid
from fd_global              import global_info

from fd_image               import fd_image_init
from fd_channel             import fd_channel_init
from fd_udpclient           import fd_udp_init
from fd_synctime            import fd_timer_init
from fd_sslclient           import fd_client

#==============================================================

list_client = []

def main():
        global list_account, list_client, global_info

        pp_dns_init()
        fd_image_init()
        fd_channel_init()
        fd_udp_init()
        fd_timer_init()

        for account in list_account:
                client = fd_client(account[0], account[1])
                client.start()
                list_client.append(client)

        printer.debug('worker [%d] started' % redis_dbid)
        printer.debug('client %d initted' % len(list_client))
        global_info.event_gameover.wait()
        printer.debug('worker [%d] stopping' % redis_dbid)

        sleep(30)
        printer.wait_for_flush()

if __name__ == '__main__':
        try:
                main()
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()


