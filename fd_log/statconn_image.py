#!/usr/bin/env python3

from time       import time, sleep, localtime, mktime, strptime, strftime
from datetime   import datetime
import sys

if sys.argv[1] == '2':
        image_file      = '2_image_get.txt'
        bid_file        = '2_price_get.txt'
else:
        image_file      = '1_image_get.txt'
        bid_file        = '1_price_get.txt'

#================================================================================================

def time_sub(end, begin):
        e = datetime.timestamp(datetime.strptime('1970-01-01 '+end,   '%Y-%m-%d %H:%M:%S.%f'))
        b = datetime.timestamp(datetime.strptime('1970-01-01 '+begin, '%Y-%m-%d %H:%M:%S.%f'))
        #print(e,b)
        return "%.6f" % (e-b)


def image():
        image_f = open(image_file, 'r')
        while True:
                line = image_f.readline()
                if not line or line.strip() == '':
                        break
                data = line.split()
                '''
                for i in range(12):
                        print(i, data[i])
                '''
                machine      = data[0].strip().split('_')[0]
                req_time     = data[3].strip()
                ack_time     = data[6].strip()
                server_group = data[11].strip().strip("'").split('.')[0]
                delay_time   = time_sub(ack_time, req_time)
                print('imagecode', machine, server_group.ljust(8), req_time, ack_time, delay_time)
        image_f.close()

def main():
        image()


main()
