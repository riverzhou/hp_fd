#!/usr/bin/env python3

from time       import time, sleep, localtime, mktime, strptime, strftime
from datetime   import datetime

image_file     = '5_image_get.txt'

decode_file    = '5_decode_req.txt'

#================================================================================================

list_decode_req = []

list_image_lost = []

list_info_lost  = []

list_bidno_lost = []

def image(image_filename):
        global list_decode_req, list_image_lost, list_info_lost, list_bidno_lost
        image_f = open(image_filename, 'r')
        print(image_filename.split('.')[0], ':')
        print()
        while True:
                line = image_f.readline()
                if not line or line.strip() == '':
                        break
                sid = line.split('JSESSIONID=')[1].split(';')[0].strip()
                bidno = line.split('BIDNUMBER=')[1].split('&')[0].strip()
                if sid not in list_decode_req:
                        list_image_lost.append(sid)
                        list_info_lost.append(line)
                        list_bidno_lost.append(bidno)
                        #print(sid)
                        print(line)
        image_f.close()

def decode(decode_filename):
        global list_decode_req
        bid_f   = open(decode_filename, 'r')
        while True:
                line = bid_f.readline()
                if not line or line.strip() == '':
                        break
                sid  = line.split('fd_redis_writer')[1].split(',')[0][9:].strip()
                list_decode_req.append(sid)
                #print(sid)
        bid_f.close()

def main():
        decode(decode_file)
        print('Total decode req : %d \n' % len(list_decode_req))
        image(image_file)
        print('Total image lost : %d \n' % len(list_image_lost))
        for bidno in list_bidno_lost:
                print(bidno)

main()


