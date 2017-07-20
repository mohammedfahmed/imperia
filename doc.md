*Installation of emane (source code)*

# dependencies:
  sudo apt-get install gcc g++ autoconf automake libtool libxml2-dev libprotobuf-dev \
python-protobuf libpcap-dev libpcre3-dev uuid-dev debhelper pkg-config python-lxml \
python-setuptools protobuf-compiler git dh-python






*Installation of emane-tutorial*

We need pycurl to use the olsr viewer

# header files for libcurl
 sudo apt-get install libcurl4-openssl-dev
# header files for openssl
 sudo apt-get install libssl-dev
# pycurl
 sudo pip install pycurl




Also installed 
# utility library for struct-array like objects in python, in python 3 there is 
# a native types.SimpleNamespace:
 sudo pip install namedlist


coordinates of Haifa: 32.75°N, 35.0°E 









# start TDMA in emane:
emaneevent-pathloss 1:10 90 -i emanenode0
emaneevent-tdmaschedule -i emanenode0  schedule.xml 

# aggressive ping with TOS
sudo ping node-2 -Q 0xc0 -i 0.1

# compile only a part of emane
go to the subdirectory and run make && sudo make install
it works with only the tdma part

# debug emane
don't start it with "-r" (real-time) or "-d" (daemon). Edit host-ctl to do that

# debug example in emane.
# See whole packet, then Ethernet header, IP, UDP, OLSR (Hello message)
(gdb) b /home/ubuntu/Source/emane/src/models/mac/tdma/basemodelimpl.cc:886
No source file named /home/ubuntu/Source/emane/src/models/mac/tdma/basemodelimpl.cc.
Make breakpoint pending on future shared library load? (y or [n]) y
Breakpoint 2 (/home/ubuntu/Source/emane/src/models/mac/tdma/basemodelimpl.cc:886) pending.
(gdb) c
Continuing.
(gdb) list
883	void EMANE::Models::TDMA::BaseModel::Implementation::processDownstreamPacket(DownstreamPacket & pkt,
884	                                                                             const ControlMessages &)
885	{
886	  LOGGER_STANDARD_LOGGING(pPlatformService_->logService(),
887	                          DEBUG_LEVEL,
888	                          "MACI %03hu TDMA::BaseModel::%s",
889	                          id_,
890	                          __func__);
891
(gdb) info locals
fd = 41
__for_range = std::vector of length 1, capacity 1 = {{iov_base = 0x7fffdc00d210, iov_len = 62}}
__for_begin = <optimized out>
__func__ = "processDownstreamPacket"
vv = std::vector of length 1, capacity 1 = {{iov_base = 0x7fffdc00d210, iov_len = 62}}
u8Queue = 65 'A'
packetsDropped = <optimized out>
(gdb) x/62xb vv[0].iov_base
0x7fffdc00d210:	0xff	0xff	0xff	0xff	0xff	0xff	0x02	0x02
0x7fffdc00d218:	0x00	0x00	0x00	0x04	0x08	0x00	0x45	0xc0
0x7fffdc00d220:	0x00	0x30	0x7e	0xcd	0x40	0x00	0x40	0x11
0x7fffdc00d228:	0xa5	0x65	0x0a	0x64	0x00	0x04	0x0a	0x64
0x7fffdc00d230:	0x00	0xff	0x02	0xba	0x02	0xba	0x00	0x1c
0x7fffdc00d238:	0xd9	0x0a	0x00	0x14	0x27	0x0c	0xc9	0x46
0x7fffdc00d240:	0x00	0x10	0x0a	0x64	0x00	0x04	0x01	0x00
0x7fffdc00d248:	0x0b	0x8b	0x00	0x00	0x04	0x03
(gdb) x/14xb vv[0].iov_base
0x7fffdc00d210:	0xff	0xff	0xff	0xff	0xff	0xff	0x02	0x02
0x7fffdc00d218:	0x00	0x00	0x00	0x04	0x08	0x00
(gdb) x/20xb vv[0].iov_base+14
0x7fffdc00d21e:	0x45	0xc0	0x00	0x30	0x7e	0xcd	0x40	0x00
0x7fffdc00d226:	0x40	0x11	0xa5	0x65	0x0a	0x64	0x00	0x04
0x7fffdc00d22e:	0x0a	0x64	0x00	0xff
(gdb) x/8xb vv[0].iov_base+14+20
0x7fffdc00d232:	0x02	0xba	0x02	0xba	0x00	0x1c	0xd9	0x0a
(gdb) x/20xb vv[0].iov_base+14+20+8
0x7fffdc00d23a:	0x00	0x14	0x27	0x0c	0xc9	0x46	0x00	0x10
0x7fffdc00d242:	0x0a	0x64	0x00	0x04	0x01	0x00	0x0b	0x8b
0x7fffdc00d24a:	0x00	0x00	0x04	0x03

# hexdump of a packet
# NB: you want an hexdump byte after byte to avoid little/big endian confusion
hexdump -C /tmp/TCmsgs.bin

