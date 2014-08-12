#!/usr/bin/env python3

from traceback      import print_exc

from fd_config      import list_account
from fd_global      import global_info

from fd_redis       import fd_redis_init
from fd_channel     import fd_channel_init
from fd_udpclient   import fd_udp_init
from fd_sslclient   import fd_client

list_client = []

def main():
        global list_account, list_client, global_info

        fd_redis_init()
        fd_channel_init()
        fd_udp_init()

        for account in list_account:
                client = fd_client(account[0], account[1])
                client.start()
                list_client.append(client)

        global_info.event_gameover.wait()

        sleep(60)

if __name__ == '__main__':
        try:
                main()
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()


