#!/usr/bin/env python3

from pp_baseredis       import pp_redis_init_a

#================================================================================

list_dbs    = [ 1 ,2 ,3, 4, 5, 6, 7, 8, 9]

list_keys   = ['log_warning', 'log_error', 'log_debug', 'log_critical', 'log_info', 'log_data', 'log_time']

#================================================================================

def main():
        for dbid in list_dbs:
                redis_a = pp_redis_init_a(dbid).redis
                for key in list_keys:
                        f_name = './log/%.2d_%s.log' % (dbid, key)
                        f = open(f_name, 'wb')
                        buff = redis_a.lrange(key,0,-1)
                        for line in buff:
                                f.write(line)
                                f.write('\r\n'.encode())
                        f.close()

if __name__ == '__main__':
        main()

