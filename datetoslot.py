import datetime
import time

# see also date -d "Jul 20 2017 0:43:55" +%s from shell
# ex 1500551099 only seconds
# 1500551089133549744 with nano
epoch = datetime.datetime(1970, 1, 1,0)
d = datetime.datetime(2017,7,20, 00, 43, 55, 300*1000) - datetime.timedelta(hours=3) # 3 because Israel tz in summer
us = (d - epoch).total_seconds()*1e6

print "Slot (from 0): ", round((us / 600000.0 - us // 600000)*6 + 0)
