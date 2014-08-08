#!/usr/bin/env python3


class fd_global()
        def __init__(self):
                self.flag_gameover  = False
                self.flag_gamebegin = False

                self.price_bid      = [0, 0, 0]
                self.event_image    = [Event(), Event(), Event()]
                self.event_price    = [Event(), Event(), Event()]


global_info = fd_global()


