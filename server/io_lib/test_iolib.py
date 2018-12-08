# -*- coding: utf-8 -*- 
import sys
import io_notify
import io_debug, parse_class
# This is necessary for the connection to mysql to support special characters (acentos, etc.)
reload(sys)
sys.setdefaultencoding("utf-8")
# a = io_notify.io_notify(1,None,1)
# a.send_email('delriogjl@gmail.com','test')
# a = io_debug.io_debug(True,None,True)
# a.io_print('test')
# print a.io_getbuffer()

# TEST parse_daily
foo = parse_class.Parser(True, None, True, True)
foo.parse_daily()
