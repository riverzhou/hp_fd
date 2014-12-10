#!/usr/bin/env python3

from pickle         import dumps, loads
from traceback      import print_exc, format_exc

from pp_baseredis   import pp_redis_init

import db01,db02,db03,db04,db05,db06,db07,db08,db09

db_config = [None,db01,db02,db03,db04,db05,db06,db07,db08,db09]

#=========================================================

key_static  = 'cfg_static'
key_dynamic = 'cfg_dynamic'
key_trigger = 'cfg_trigger'

class set_config():
        def __init__(self, dbid):
                self.dbid       = dbid
                self.pp_redis   = pp_redis_init(dbid)

        def redis_save(self):
                self.pp_redis.redis.save()

        def redis_set_one(self, key, val):
                ret = self.pp_redis.redis.set(key, val)
                if ret == True:
                        return True
                else:
                        print('redis_set_one failed')
                        return False

        def redis_push_one(self, key, val):
                ret = self.pp_redis.redis.rpush(key, val)
                if ret != None:
                        return True
                else:
                        print('redis_push_one failed')
                        return False

        def make_static_config(self):
                global db_config
                key_val = {}
                key_val['account_list']         = db_config[self.dbid].account_list
                return dumps(key_val, protocol = 0)

        def make_dynmic_config(self):
                global db_config
                key_val = {}
                key_val['channel_trigger']      = db_config[self.dbid].channel_trigger
                key_val['channel_timeout']      = db_config[self.dbid].channel_timeout
                key_val['image_trigger']        = db_config[self.dbid].image_trigger
                key_val['decode_deadline']      = db_config[self.dbid].decode_deadline
                key_val['decode_type']          = db_config[self.dbid].decode_type
                key_val['decode_timeout']       = db_config[self.dbid].decode_timeout
                key_val['image_timeout']        = db_config[self.dbid].image_timeout
                key_val['price_timeout']        = db_config[self.dbid].price_timeout
                key_val['bid0_maxretry']        = db_config[self.dbid].bid0_maxretry
                return dumps(key_val, protocol = 0)

        def write_static_config(self):
                cfg = self.make_static_config()
                if cfg == None:
                        print('make_static_config %d None' % self.dbid)
                        return False
                ret = self.redis_set_one(key_static, cfg)
                return ret

        def write_dynamic_config(self):
                cfg = self.make_dynmic_config()
                if cfg == None:
                        print('make_dynmic_config %d None' % self.dbid)
                        return False
                ret = self.redis_set_one(key_dynamic, cfg)
                if ret != True:
                        return False
                ret = self.redis_push_one(key_trigger, 1)
                if ret != True:
                        return False
                return True

def set_db(dbid):
        config = set_config(dbid) 
        if config.pp_redis                  == None:
                print('redis %d init failed'    % dbid)
                return False
        if config.write_static_config()     != True:
                print('write %d static failed'  % dbid)
                return False
        if config.write_dynamic_config()    != True:
                print('write %d dynamic failed' % dbid)
                return False
        config.redis_save()
        print('config %d write finished .....'  % dbid)
        return True

def main():
        for dbid in range(9):
                set_db(dbid+1)

if __name__ == "__main__":
        try:
                main()
        except  KeyboardInterrupt:
                print()
        except:
                print_exc()
        

