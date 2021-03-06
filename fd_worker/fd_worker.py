#!/usr/bin/env python3

from traceback              import print_exc
from time                   import sleep

from pp_server              import pp_dns_init
from pp_baseredis           import pp_redis, pp_redis_init, pp_redis_connect_print
from pp_global              import pp_global_info, pp_global_init, pp_global_config_print
from pp_log                 import printer

from fd_config              import redis_dbid
from fd_decode              import fd_decode_init
from fd_channel             import fd_channel_init
from fd_udpclient           import fd_udp_init
from fd_synctime            import fd_timer_init
from fd_sslclient           import fd_client
from fd_log                 import logger

#==============================================================

def main():
        global pp_global_info, printer

        pp_dns_init()

        if pp_redis_init()  != True:
                return

        if pp_global_init() != True:
                return

        fd_decode_init()
        fd_channel_init()
        fd_udp_init()
        fd_timer_init()

        list_client = []
        for account in pp_global_info.list_account:
                client = fd_client(account[0], account[1])
                client.start()
                list_client.append(client)

        printer.debug('worker [%d] started' % redis_dbid)
        printer.debug('client %d initted' % len(list_client))
        pp_global_info.event_gameover.wait()
        printer.debug('worker [%d] stopping' % redis_dbid)

        sleep(60)
        printer.wait_for_flush()
        logger.wait_for_flush()

if __name__ == '__main__':
        try:
                main()
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()
        print()

