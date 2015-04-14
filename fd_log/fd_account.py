#!/usr/bin/env python3

import sys
sys.path.append('../fd_control/')

from fd_group import group

ac_file = '../fd_control/ac_file.txt'

ac_group = [1, 2, 3, 4, 5, 6, 7]

def read_ac():
        global ac_file
        f = open(ac_file, 'r')
        dict_ac = {}
        for i in ac_group:
                dict_ac[i] = {}
        while True:
                line = f.readline()
                if not line or line.strip() == '':
                        break
                bidno, passwd, name, mac = line.split()
                group = int(mac[0])
                #print(bidno, passwd, name, mac, group)
                dict_ac[group][bidno] = (mac, bidno, passwd, name)
        f.close()
        #print(dict_ac)
        return dict_ac

if __name__ == '__main__':
        print(read_ac())

