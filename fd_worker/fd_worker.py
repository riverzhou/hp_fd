#!/usr/bin/env python3

from traceback              import print_exc
from time                   import sleep

from fd_config              import list_account, redis_dbid
from fd_global              import global_info

from pp_server              import pp_dns_init
from fd_redis               import fd_redis_init
from fd_channel             import fd_channel_init
from fd_udpclient           import fd_udp_init
from fd_sslclient           import fd_client

list_client = []

def main():
        global list_account, list_client, global_info

        pp_dns_init()
        fd_redis_init()
        fd_channel_init()
        fd_udp_init()

        for account in list_account:
                client = fd_client(account[0], account[1])
                client.start()
                list_client.append(client)

        print('worker \t[%d] started' % redis_dbid)
        print('client \t%d initted' % len(list_client))
        global_info.event_gameover.wait()

        sleep(90)

if __name__ == '__main__':
        try:
                main()
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()


