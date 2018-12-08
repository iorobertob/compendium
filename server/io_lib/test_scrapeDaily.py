# -*- coding: utf-8 -*- 
import sys
import io_notify
import io_debug, parse_class
# This is necessary for the connection to mysql to support special characters (acentos, etc.)
reload(sys)
sys.setdefaultencoding("utf-8")

# self.year  = date.strftime('%Y')
# self.year  = int(self.year[-2:])
# self.month = int(date.strftime('%m'))
# self.day   = int(date.strftime('%d'))

from datetime import timedelta, date

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

start_dt = date(2017, 1, 1)
end_dt = date(2017, 12, 31)

foo = parse_class.Parser(True, None, True, False)
for dt in daterange(start_dt, end_dt):
    print(dt.strftime("%Y-%m-%d"))
    print "day: " + str(dt.weekday())
    # TEST parse_daily
    #foo.parse_daily(dt)