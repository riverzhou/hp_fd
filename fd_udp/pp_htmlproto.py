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
                if key_val == {} :
                        print(html_string)
                #        printer.error(html_string)
                return key_val

        def make_html_req(self):
                return  '/carnetbidinfo.html'

#----------------------------------------------


