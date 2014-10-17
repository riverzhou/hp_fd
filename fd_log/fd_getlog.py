#!/usr/bin/env python3


#from fd_config      import redis_dbid
from fd_redis       import redis_db

list_dbs    = [ 1 ,2 ,3, 4, 5 ]

list_keys   = ['warning', 'error', 'debug', 'critical', 'info', 'data', 'time']


def main():
        for dbid in list_dbs:
                redis = redis_db(dbid)
                for key in list_keys:
                        buff = redis.get_list(key)
                        f = open('./log/' + str(dbid) + '_' + key + '.log', 'wb')
                        for line in buff:
                                f.write(line)
                                f.write('\r\n'.encode())
                        f.close()


main()

