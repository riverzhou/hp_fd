#!/usr/bin/env python3

from time           import time, sleep, localtime, mktime, strptime, strftime
from datetime       import datetime
from collections    import OrderedDict
import sys

if sys.argv[1] == '2':
        req_file    = '2_decode_req.txt'
        ack_file    = '2_decode_ack.txt'
else:
        req_file    = '1_decode_req.txt'
        ack_file    = '1_decode_ack.txt'

#================================================================================================

dict_decode = {}
count_req   = 0
count_ack   = 0

#================================================================================================

def time_sub(end, begin):
        #print(end,begin)
        e = datetime.timestamp(datetime.strptime('1970-01-01 '+end,   '%Y-%m-%d %H:%M:%S.%f'))
        b = datetime.timestamp(datetime.strptime('1970-01-01 '+begin, '%Y-%m-%d %H:%M:%S.%f'))
        ##print(e,b)
        return "%.6f" % (e-b)


def req():
        global dict_decode, count_req, count_ack
        count_req   = 0
        req_f = open(req_file, 'r')
        while True:
                line = req_f.readline()
                if not line or line.strip() == '':
                        break
                count_req += 1
                data = line.split()
                '''
                for i in range(len(data)):
                        print(i, data[i])
                '''
                machine     = data[0].strip().split('_')[0].lstrip('log/')
                time        = data[1].strip(',').strip('"').strip("'")
                tmp         = data[3].split(',')
                uid         = tmp[0]
                bidno       = uid[0:8]
                sid         = uid[8:]
                d_type      = tmp[1]
                d_timeout   = tmp[2]
                #print(machine, time, bidno, sid, d_type, d_timeout)
                dict_decode[uid] = OrderedDict()
                dict_decode[uid]['machine'] = machine
                dict_decode[uid]['bidno']   = bidno
                dict_decode[uid]['sid']     = sid
                dict_decode[uid]['req_time']= time
                dict_decode[uid]['type']    = d_type
                dict_decode[uid]['timeout'] = d_timeout
        req_f.close()

def ack():
        global dict_decode, count_req, count_ack
        count_ack   = 0
        ack_f   = open(ack_file, 'r')
        while True:
                line = ack_f.readline()
                if not line or line.strip() == '':
                        break
                count_ack += 1
                data = line.split()
                '''
                for i in range(len(data)):
                        print(i, data[i])
                '''
                machine     = data[0].strip().split('_')[0].lstrip('log/')
                time        = data[1].strip(',').strip('"').strip("'")
                tmp         = data[3].split(',')
                uid         = tmp[0]
                bidno       = uid[0:8]
                sid         = uid[8:]
                d_number    = tmp[1].strip("')")
                #print(machine, time, bidno, sid, d_number)
                if uid not in dict_decode:
                        print('uid no found !!!!!!!!!!!!!!!!!')
                cost_decode = time_sub(time, dict_decode[uid]['req_time'])
                dict_decode[uid]['ack_time']= time
                dict_decode[uid]['number']  = d_number
                dict_decode[uid]['cost']    = cost_decode
        ack_f.close()


def print_result():
        global dict_decode, count_req, count_ack

        for uid in dict_decode:
                data = dict_decode[uid]
                try:
                        ack_time = data['ack_time']
                        number   = data['number']
                        cost     = data['cost']
                except:
                        ack_time = None
                        number   = None
                        cost     = None
                print('%s %s %s %s %s %.2s %s %s %s' % (data['machine'], data['bidno'], data['sid'], data['req_time'], data['type'], data['timeout'].rjust(2), ack_time, number, cost))

        print('Total req is %d ' % count_req)
        print('Total ack is %d ' % count_ack)


def main():
        global dict_decode, count_req, count_ack
        req()
        ack()
        print_result()

main()

