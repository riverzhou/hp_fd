#!/usr/bin/env python3

from pp_baseredis       import pp_redis_init_a, pp_redis_init_b

#================================================================================

list_dbs    = [ 1 ,2 ,3, 4, 5, 6, 7, 8, 9, 10, 11]

list_keys   = ['warning', 'error', 'debug', 'critical', 'info', 'data', 'time']

#================================================================================

def main():
        for dbid in list_dbs:
                redis_a = pp_redis_init_a(dbid).redis
                redis_b = pp_redis_init_b(dbid).redis
                for key in list_keys:
                        f_name = './log/%.2d_%s.log' % (dbid, key)
                        f = open(f_name, 'wb')
                        buff = redis_a.lrange(key,0,-1)
                        for line in buff:
                                f.write(line)
                                f.write('\r\n'.encode())
                        buff = redis_b.lrange(key,0,-1)
                        for line in buff:
                                f.write(line)
                                f.write('\r\n'.encode())
                        f.close()

if __name__ == '__main__':
        main()

