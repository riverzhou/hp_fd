#!/usr/bin/env python3

from time       import sleep

from fd_redis   import redis_db


image_db    = 5
key_number  = 'ack_number'
key_image   = 'req_image'


def test(redis):
        req = redis.blk_get_one(key_image)
        if req == None:
                return
        sid, image = req.decode().split(',')
        print('sid', sid)
        #sleep(5)
        number = '123456'
        ack = ','.join([sid, number])
        redis.put_one(key_number, ack.encode())
        print('sid number', sid, number)
        sleep(0)


if __name__ == '__main__':
        redis = redis_db(image_db)
        while True:
                test(redis)

