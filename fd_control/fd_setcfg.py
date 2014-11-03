#!/usr/bin/env python3

from pickle         import dumps, loads

from db5_config     import *
from pp_baseredis   import pp_redis, pp_redis_init

#=========================================================

key_static  = 'cfg_static'
key_dynamic = 'cfg_dynamic'
key_trigger = 'cfg_trigger'

#@pp_redis.safe_proc
def redis_set_one(key, val):
        global pp_redis
        #print(key, val)
        ret = pp_redis.redis.set(key, val)
        if ret == True:
                return True
        else:
                print('redis_set_one failed')
                return False

#@pp_redis.safe_proc
def redis_push_one(key, val):
        global pp_redis
        #print(key, val)
        ret = pp_redis.redis.rpush(key, val)
        if ret != None:
                return True
        else:
                print('redis_push_one failed')
                return False

def make_static_config():
        key_val = {}
        key_val['account_list'] = account_list
        return dumps(key_val, protocol = 0)

def make_dynmic_config():
        key_val = {}
        key_val['channel_trigger']      = channel_trigger
        key_val['channel_timeout']      = channel_timeout
        key_val['image_trigger']        = image_trigger
        key_val['decode_type']          = decode_type
        key_val['decode_timeout']       = decode_timeout
        key_val['decode_deadline']      = decode_deadline
        return dumps(key_val, protocol = 0)

def write_static_config():
        cfg = make_static_config()
        if cfg == None:
                print('make_static_config None')
                return False
        ret = redis_set_one(key_static, cfg)
        return ret

def write_dynamic_config():
        cfg = make_dynmic_config()
        if cfg == None:
                print('make_dynmic_config None')
                return False
        ret = redis_set_one(key_dynamic, cfg)
        if ret != True:
                return False
        ret = redis_push_one(key_trigger, 1)
        if ret != True:
                return False
        return True

def main():
        if pp_redis_init()          != True:
                print('redis init failed')
                return False
        if write_static_config()    != True:
                print('write static failed')
                return False
        if write_dynamic_config()   != True:
                print('write dynamic failed')
                return False
        print('config write finished .....')
        return True

if __name__ == "__main__":
        main()
        

