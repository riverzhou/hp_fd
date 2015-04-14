#!/usr/bin/env python3

from fd_account import read_ac, group
from pp_price   import min_price

#=============================================================

result_file     = '0_result.txt'

dict_ac_group   = {}
dict_result     = {}

#=============================================================

def check_result():
        global dict_ac_group, dict_result, result_file 
        f = open(result_file, 'r')
        while True:
                line = f.readline()
                if not line or line.strip() == '':
                        break
                bidno  = line.split(',')[1].split()[1].strip()
                first, second, third = line.split(' : ')[1].split('.')[0].split(',')
                first  = first.strip().lstrip('[').rstrip(']').strip("'")
                second = second.strip().lstrip('[').rstrip(']').strip("'")
                third  = third.strip().lstrip('[').rstrip(']').strip("'")
                price  = second
                if third != 'None':
                        price = third
                if price != 'None':
                        try:
                                price = int(price)
                        except:
                                price = 'None'
                if price != 'None':
                        if price not in dict_result:
                                dict_result[price] = {}
                        dict_result[price][bidno] = (bidno, price, first, second, third, dict_ac_group[bidno][3])
                        try:
                                del(dict_ac_group[bidno])
                        except:
                                pass
        f.close()

def main():
        global dict_ac_group, dict_result, min_price
        dict_ac_group = read_ac()[group]
        check_result()

        list_price = []
        for price in dict_result:
                list_price.append(price)
        list_price.sort(reverse = True)

        print('\r\nhit ok :')
        ok_count = 0
        for price in list_price:
                if price <= min_price:
                        break
                for bidno in sorted(dict_result[price]):
                        print(dict_result[price][bidno])
                ok_count += len(dict_result[price])
        print('hit ok count: %d \r\n' % ok_count)

        print('\r\nhit pending :')
        pending_count = 0
        if min_price in dict_result:
                for bidno in sorted(dict_result[min_price]):
                        print(dict_result[min_price][bidno])
                pending_count += len(dict_result[min_price])
        print('hit pending count: %d \r\n' % pending_count )

        print('\r\nhit low :')
        low_count = 0
        for price in list_price:
                if price >= min_price:
                        continue
                for bidno in sorted(dict_result[price]):
                        print(dict_result[price][bidno])
                low_count += len(dict_result[price])
        print('hit low count: %d \r\n' % low_count)

        print('\r\nhit none:')
        for bidno in sorted(dict_ac_group):
                print(dict_ac_group[bidno])
        print('hit none count: %d \r\n' % len(dict_ac_group))

main()

