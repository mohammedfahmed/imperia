import os

fd = open('/home/ubuntu/Python/models/emanedemos/tdma/routing1.conf')
text = fd.read()
fd.close()
for i in range(2,7):
    text2 = text.replace("persist/1/var/run/olsrd.lock", ("persist/%d/var/run/olsrd.lock" % (i)))
    fd = open(('/home/ubuntu/Python/models/emanedemos/tdma/routing%d.conf' % (i)),'w')
    fd.write(text2)
    fd.close()