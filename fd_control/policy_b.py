#!/usr/bin/evn python3

import common_policy

#----------------------------------------------------------------------------

channel_trigger = common_policy.channel_trigger
channel_timeout = common_policy.channel_timeout
bid0_maxretry   = common_policy.bid0_maxretry

#----------------------------------------------------------------------------

image_trigger   = [('10:35:00', 72600), ('11:29:40', 600), ('11:29:55', 400)]

decode_type     = ['A', 'B', 'C']
decode_timeout  = [30, 8, 2]
decode_deadline = '11:29:56'

