#!/usr/bin/env python3

from fd_account import read_ac, group

login_file      = '0_login.txt'

dict_ac_group   = {}
dict_login      = {}

#=============================================================

def check_login():
        global dict_ac_group, dict_login, login_file 
        f = open(login_file, 'r')
        while True:
                line = f.readline()
                if not line or line.strip() == '':
                        break
                bidno = line.split(',')[1].split()[1].strip()
                dict_login[bidno] = line.strip()
                del(dict_ac_group[bidno])
        f.close()


def main():
        global dict_ac_group, dict_bidok, dict_bid112
        dict_ac_group = read_ac()[group]
        check_login()
        print('\r\nlogin ok : \r\n')
        for bidno in dict_login:
                print(dict_login[bidno])
        print('\r\nnot login yet : \r\n')
        for bidno in dict_ac_group:
                print(dict_ac_group[bidno])

main()

