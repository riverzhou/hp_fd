#!/usr/bin/env python3


from fd_config      import redis_dbid
from fd_redis       import redis_db


list_keys = ['warning', 'error', 'debug', 'critical', 'info']

redis = redis_db(redis_dbid)

for key in list_keys:
        buff = redis.get_list(key)
        f = open('./log/'+key+'.log', 'wb')
        for line in buff:
                f.write(line)
                f.write('\r\n'.encode())
        f.close()


