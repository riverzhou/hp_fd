#!/usr/bin/env python3

import random, string

from collections            import OrderedDict

from pp_log                 import printer

#==================================================================================================================

class proto_html():
        html_ack_len = 4096

        def make_html_head(self, host_name):
                headers = OrderedDict()
                headers['Content-Type'] = 'text/html'
                headers['Host']         = '%s:80' % host_name
                headers['Accept']       = 'text/html, */*'
                headers['User-Agent']   = 'Mozilla/3.0 (compatible; Indy Library)'
                return headers

        def parse_html_ack(self, string):
                html_string = string.strip()
                key_val = {}
                if len(html_string) == 0 :
                        return None

                if '<TYPE>INFO</TYPE><INFO>B拍卖会' in html_string:
                        key_val['code']         = 'B'
                        data = html_string.split()
                        key_val['date']         = data[0].split('：')[1].split('上海市')[0].strip()     # <TYPE>INFO</TYPE><INFO>B拍卖会：2014年4月19日上海市个人非营业性客车额度投标拍卖会
                        key_val['number_limit'] = data[1].split('：')[1].strip()                        # 投放额度数：8200
                        key_val['number']       = data[2].split('：')[1].strip()                        # 目前已投标人数：94241
                        key_val['systime']      = data[7].split('：')[1].strip()                        # 系统目前时间：11:09:37
                        key_val['price']        = data[8].split('：')[1].strip()                        # 目前最低可成交价：72600
                        key_val['lowtime']      = data[9].split('：')[1].strip()                        # 最低可成交价出价时间：10:30:08
                elif '<TYPE>INFO</TYPE><INFO>A拍卖会' in html_string:
                        key_val['code']         = 'A'
                        data = html_string.split()
                        key_val['date']         = data[0].split('：')[1].split('上海市')[0].strip()     # <TYPE>INFO</TYPE><INFO>A拍卖会：2014年4月19日上海市个人非营业性客车额度投标拍卖会
                        key_val['number_limit'] = data[1].split('：')[1].strip()                        # 投放额度数：8200
                        key_val['price_limit']  = data[2].split('：')[1].strip()                        # 本场拍卖会警示价：72600
                        key_val['systime']      = data[7].split('：')[1].strip()                        # 系统目前时间：10:39:50
                        key_val['number']       = data[8].split('：')[1].strip()                        # 目前已投标人数：77163
                        key_val['price']        = data[9].split('：')[1].strip()                        # 目前最低可成交价：100
                        key_val['lowtime']      = data[10].split('：')[1].split('<')[0].strip()         # 最低可成交价出价时间：10:30:15</INFO>
                else:
                        key_val['code'] = 'C'

                #print(key_val)
                #print(sorted(key_val.items()))

                #if key_val['code'] == 'B' or key_val['code'] == 'A':
                #        printer.error(sorted(key_val.items()))

                return key_val

        def make_html_req(self):
                return  '/carnetbidinfo.html'

#----------------------------------------------


