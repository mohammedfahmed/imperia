#
# ........ FAST & DIRTY ........

import numpy as np
import os
import subprocess
import time
from contextlib import contextmanager
import map_tools
import socket

import re

from emanesh.events import EventService
from emanesh.events import PathlossEvent
from emanesh.events import LocationEvent
from emanesh import ControlPortClient
from emanesh import EMANEShell

import paramiko

import radio_calculations

from namedlist import namedlist

project_dir = "/home/ubuntu/Desktop/emane-tutorial/22/"

@contextmanager
def open_tdma():
    # subprocess.call(["sudo", "-S", "/home/ubuntu/Desktop/two_points/start"], shell=False) best but annoying to type the password..
    subprocess.call(["cd /home/ubuntu/Python/models/emanedemos/tdma; echo ubuntu | sudo -S ./demo-start"], shell=True)
    print ""
    try:
        yield
    finally:
        # stop emane
        subprocess.call(["cd /home/ubuntu/Python/models/emanedemos/tdma; echo ubuntu | sudo -S ./demo-stop"], shell=True)
        print ""
        # subprocess.call(["sudo", "-S", "/home/ubuntu/Desktop/two_points/end"], shell=False)



def init_nodes(service):


if __name__ == "__main__":
    with open_tdma():
        time.sleep(5)
        esh = EMANEShell('localhost',47000)
        # Debug level
        #esh.do_loglevel('4')
        # haifa airport, Naharia, Tiberias, Haifa airport 33.013 35.05
        service = EventService(('224.1.2.8', 45703, 'emanenode0'))

        init_nodes(service)
        raw_input("Press Enter to continue...")
        print "Done"
        #pyplot.plot(distances, rates)
        #pyplot.xscale('log')
        #pyplot.show()
