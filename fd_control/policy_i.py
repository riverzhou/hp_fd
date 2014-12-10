#!/usr/bin/evn python3

import common_policy

#----------------------------------------------------------------------------

channel_trigger = common_policy.channel_trigger
channel_timeout = common_policy.channel_timeout
bid0_maxretry   = common_policy.bid0_maxretry
deadline        = common_policy.decode_deadline

#----------------------------------------------------------------------------

image_trigger   = [('10:34:00', 72600), ('11:29:40', 800), ('11:29:55', 300)]

decode_type     = ['A', 'A', 'C']
decode_timeout  = [30, 20, 2]
image_timeout   = [10, 4, 3]
price_timeout   = [30, 2, 10]

