#!/usr/bin/env python3

class foobar_logger():
        def debug(self, log):
                print('debug',log)

        def info(self, log):
                print('info',log)

        def warning(self, log):
                print('warning',log)

        def error(self, log):
                print('error',log)

        def critical(self, log):
                print('critical',log)

logger  = foobar_logger()
printer = foobar_logger()

