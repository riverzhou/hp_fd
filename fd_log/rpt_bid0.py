#!/usr/bin/env python3

from fd_account import read_ac, group

bidok_file  = '0_bidok.txt'
bid112_file = '0_bid112.txt'

dict_ac_group   = {}
dict_bidok      = {}
dict_bid112     = {}

#====================================================================================

def check_bid112():
        global dict_ac_group, dict_bidok, dict_bid112, bid112_file
        f = open(bid112_file, 'r')
        while True:
                line = f.readline()
                if not line or line.strip() == '':
                        break
                bidno = line.split('::')[2].split('BIDNUMBER=')[1].split('&')[0].strip()
                dict_bid112[bidno] = line.strip()
                del(dict_ac_group[bidno])
        f.close()


def check_bidok():
        global dict_ac_group, dict_bidok, dict_bid112, bidok_file
        f = open(bidok_file, 'r')
        while True:
                line = f.readline()
                if not line or line.strip() == '':
                        break
                bidno = line.split(',')[1].split()[1].strip()
                dict_bidok[bidno] = line.strip()
                del(dict_ac_group[bidno])
        f.close()


def main():
        global dict_ac_group, dict_bidok, dict_bid112
        dict_ac_group = read_ac()[group]
        check_bidok()
        check_bid112()
        print('\r\nbid ok : \r\n')
        for bidno in dict_bidok:
                print(dict_bidok[bidno])
        print('\r\nbid 112 : \r\n')
        for bidno in dict_bid112:
                print(dict_bid112[bidno])
        print('\r\nnot bid yet : \r\n')
        for bidno in dict_ac_group:
                print(dict_ac_group[bidno])

main()

