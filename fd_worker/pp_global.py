#!/usr/bin/env python3

from time           import sleep
from threading      import Event, Lock
from pickle         import dumps, loads

from pp_baseclass   import pp_thread
from pp_baseredis   import pp_redis

from fd_log         import logger

#========================================================================

def time_sub(end, begin):
        try:
                e = end.split(':')
                b = begin.split(':')
                return (int(e[0])*3600 + int(e[1])*60 + int(e[2])) - (int(b[0])*3600 + int(b[1])*60 + int(b[2]))
        except:
                return -1

class pp_global(pp_thread):
        key_static  = 'cfg_static'
        key_dynamic = 'cfg_dynamic'
        key_trigger = 'cfg_trigger'

        def __init__(self):
                super().__init__()
                self.event_config_init  = Event()

        def init_local_config(self):
                self.flag_create_login  = True
                self.flag_create_toubiao= [False, False]

                self.flag_gameover      = False
                self.event_gameover     = Event()

                self.event_image        = [Event(), Event(), Event()]
                self.event_price        = [Event(), Event(), Event()]

                self.trigger_price      = [None, None, None]
                self.lock_trigger       = Lock()

                self.lock_systime       = Lock()
                self.sys_time           = '10:30:00'
                self.sys_code           = None

                self.total_worker       = len(self.list_account)
                self.num_todo_tb0       = len(self.list_account)
                self.lock_todo_tb0      = Lock()

                return True

        def init_static_config(self, key_val):
                self.list_account       = key_val['account_list']
                return True

        def init_dynamic_config(self, key_val):
                self.trigger_image      = key_val['image_trigger']
                self.trigger_channel    = key_val['channel_trigger']
                self.timeout_channel    = key_val['channel_timeout']
                self.deadline_decode    = key_val['decode_deadline']
                self.type_decode        = key_val['decode_type']
                self.timeout_decode     = key_val['decode_timeout']
                self.timeout_image      = key_val['image_timeout']
                self.timeout_price      = key_val['price_timeout']
                self.maxretry_bid0      = key_val['bid0_maxretry']
                return True

        def check_static_config(self, key_val):
                if key_val == None:
                        return False
                try:
                        if 'account_list' not in key_val:
                                return False
                        return True
                except:
                        return False

        def check_dynamic_config(self, key_val):
                if key_val == None:
                        return False
                try:
                        if 'image_trigger'   not in key_val:
                                return False
                        if 'channel_trigger' not in key_val:
                                return False
                        if 'channel_timeout' not in key_val:
                                return False
                        if 'decode_deadline' not in key_val:
                                return False
                        if 'decode_type'     not in key_val:
                                return False
                        if 'decode_timeout'  not in key_val:
                                return False
                        if 'image_timeout'   not in key_val:
                                return False
                        if 'price_timeout'   not in key_val:
                                return False
                        if 'bid0_maxretry'   not in key_val:
                                return False
                        return True
                except:
                        return False

        def init_config(self):
                while True:
                        key_val = self.get_static_config()
                        if self.check_static_config(key_val) != True:
                                sleep(1)
                                continue
                        self.init_static_config(key_val)
                        break

                self.init_local_config()

                while True:
                        key_val = self.get_dynamic_config()
                        if self.check_dynamic_config(key_val) != True:
                                sleep(1)
                                continue
                        self.init_dynamic_config(key_val)
                        break

                self.event_config_init.set()

                pp_global_config_print()

                while True:
                        if self.wait_dynamic_config() != True:
                                sleep(1)
                                continue

                        key_val = self.get_dynamic_config()
                        if self.check_dynamic_config(key_val) != True:
                                sleep(1)
                                continue
                        self.init_dynamic_config(key_val)
                        pp_global_config_print()

                return True

        @pp_redis.safe_proc
        def get_static_config(self):
                global pp_redis
                obj = pp_redis.redis.get(self.key_static)
                if obj == None:
                        return None
                key_val = loads(obj)
                return key_val

        @pp_redis.safe_proc
        def get_dynamic_config(self):
                global pp_redis
                obj = pp_redis.redis.get(self.key_dynamic)
                if obj == None:
                        return None
                key_val = loads(obj)
                return key_val

        @pp_redis.safe_proc
        def wait_dynamic_config(self):
                global pp_redis
                ret = pp_redis.redis.blpop(self.key_trigger)
                if ret == None:
                        return None
                return True

        def main(self):
                self.init_config()

        def wait_for_init(self):
                try:
                        return self.event_config_init.wait()
                except  KeyboardInterrupt:
                        return None
                except:
                        return False

        def set_trigger_price(self, count, price):
                self.lock_trigger.acquire()
                if self.trigger_price[count] == None:
                        self.trigger_price[count] = price
                self.lock_trigger.release()

        def set_game_over(self):
                self.flag_gameover = True
                self.event_gameover.set()

        def update_systime(self, stime):
                self.lock_systime.acquire()
                if time_sub(stime, self.sys_time) > 0:
                        self.sys_time = stime
                self.lock_systime.release()

        def update_syscode(self, code):
                if self.sys_code == None and code == 'A':
                        self.sys_code = code
                        return
                if self.sys_code == None and code == 'B':
                        self.sys_code = code
                        return
                if self.sys_code == 'A'  and code == 'B':
                        self.sys_code = code
                        return

        def set_bid0_finish(self):
                self.lock_todo_tb0.acquire()
                self.num_todo_tb0 -= 1
                self.lock_todo_tb0.release()

        def check_bid0_finish(self):
                if self.sys_code == 'B':
                        return True
                if self.num_todo_tb0 <= 0:
                        return True
                else:
                        return False

#--------------------------------------------

pp_global_info = pp_global()

def pp_global_init():
        global pp_global_info
        pp_global_info.start()
        return pp_global_info.wait_for_init()

def pp_global_config_print():
        global pp_global_info
        logger.info(str(pp_global_info.list_account))
        logger.info(str(pp_global_info.trigger_image))
        logger.info(str(pp_global_info.trigger_channel))
        logger.info(str(pp_global_info.timeout_channel))
        logger.info(str(pp_global_info.deadline_decode))
        logger.info(str(pp_global_info.type_decode))
        logger.info(str(pp_global_info.timeout_decode))
        logger.info(str(pp_global_info.timeout_image))
        logger.info(str(pp_global_info.timeout_price))
        logger.info(str(pp_global_info.maxretry_bid0))
        return

#============================================

def config_test():
        if pp_redis_init()  != True:
                return

        if pp_global_init() != True:
                return

if __name__ == "__main__":
        from pp_baseredis   import pp_redis_init
        config_test()

