# coordinates Mitzpe Ramon 30.605N 34.805E


# run emane
# the result is NOT consistent with expectation, but a single run
# where I manually disabled OLSR and ARP gave the expected results.
# See results/SINRcheck.odt

import pylab
import numpy as np
from matplotlib import pyplot
import subprocess
import time
from contextlib import contextmanager

import re

from emanesh.events import EventService
from emanesh.events import LocationEvent
from emanesh import ControlPortClient
from emanesh import EMANEShell

import paramiko

import radio_calculations

@contextmanager
def openemane():
    # subprocess.call(["sudo", "-S", "/home/ubuntu/Desktop/two_points/start"], shell=False) best but annoying to type the password..
    subprocess.call(["echo ubuntu | sudo -S /home/ubuntu/Desktop/two_points/start"], shell=True)
    yield
    # stop emane
    subprocess.call(["echo ubuntu | sudo -S /home/ubuntu/Desktop/two_points/end"], shell=True)
    # subprocess.call(["sudo", "-S", "/home/ubuntu/Desktop/two_points/end"], shell=False)


def degreesToRadians(degrees):
    return degrees * pylab.pi / 180.0


def distance(lat1, lon1, lat2, lon2):
    earthRadiusm = 6371.0e3
    dlat = degreesToRadians(lat2 - lat1)
    dlon = degreesToRadians(lon2 - lon1)

    lat1 = degreesToRadians(lat1)
    lat2 = degreesToRadians(lat2)
    a = np.sin(dlat / 2.0) * np.sin(dlat / 2.0) + np.sin(dlon / 2.0) * np.sin(dlon / 2.0) * np.cos(lat1) * np.cos(lat2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return earthRadiusm * c




with openemane():
    esh = EMANEShell('node-1',47000)
    # Debug level
    esh.do_loglevel('4')
    subprocess.call(['gnome-terminal', '-e', 'bash -c "tail -f /home/ubuntu/Desktop/two_points/persist/1/var/log/emane.log | grep SINR"'])
    #

    service = EventService(('224.1.2.8',45703,'emanenode0'))

    lator = 40.031290
    lat2 = 40.031300
    lonor = -74.523095
    lon2 = -74.523095

    parameters = dict()
    parameters['frequencyHz'] = 2347000000
    parameters['bandwidthHz'] = 20e6
    parameters['systemnoisefloordB'] = 4
    parameters['txpowerdB'] = 0
    parameters['txgaindB'] = 0
    parameters['rxgaindB'] = 0

    # create an event setting 10's position
    n = 3
    distances = np.zeros(n)
    rates = np.zeros(n)
    dlat_array = 10**-5*np.linspace(300,800,n)

    for i in range(n):
        dlat = dlat_array[i]
        event = LocationEvent()
        event.append(1, latitude=lator, longitude=lonor, altitude=3.000000)
        event.append(2, latitude=lator+dlat, longitude=lonor, altitude=3.000000)
        distances[i] = distance(lator,lonor,lator+dlat,lonor)
        parameters['distanceM'] = distances[i]
        time.sleep(2)
        print "-------------------------------------"
        print "Distance: ", distances[i]
        service.publish(0,event)
        cpc = ControlPortClient('node-1', 47000)
        cpc.clearStatistic(3,'')
        cpc.clearStatistic(2,'')

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('node-1', username='ubuntu',
                    password='ubuntu')
        stdin, stdout, stderr = ssh.exec_command("ping -c 400 -i 0.2 radio-2")
        ping_output = stdout.readlines()
        ssh.close()
        #time.sleep(5)

        stat = cpc.getStatistic(3,'')
        numUpstreamPacketsBroadcastDrop0 = stat['numUpstreamPacketsBroadcastDrop0'][0]
        numUpstreamPacketsBroadcastRx0 = stat['numUpstreamPacketsBroadcastRx0'][0]
        numUpstreamPacketsBroadcastTx0 = stat['numUpstreamPacketsBroadcastTx0'][0]
        # print 'stat 3 up broad: drop rx tx'
        # print numUpstreamPacketsBroadcastRx0,numUpstreamPacketsBroadcastTx0, numUpstreamPacketsBroadcastDrop0

        stat = cpc.getStatistic(2,'')
        numUpstreamPacketsBroadcastDrop0 = stat['numUpstreamPacketsBroadcastDrop0'][0]
        numUpstreamPacketsBroadcastRx0 = stat['numUpstreamPacketsBroadcastRx0'][0]
        numUpstreamPacketsBroadcastTx0 = stat['numUpstreamPacketsBroadcastTx0'][0]
        # print 'stat 2 up broad: drop rx tx'
        # print numUpstreamPacketsBroadcastRx0,numUpstreamPacketsBroadcastTx0, numUpstreamPacketsBroadcastDrop0

        numUpstreamPacketsUnicastDrop0 = stat['numUpstreamPacketsUnicastDrop0'][0]
        numUpstreamPacketsUnicastRx0 = stat['numUpstreamPacketsUnicastRx0'][0]
        numUpstreamPacketsUnicastTx0 = stat['numUpstreamPacketsUnicastTx0'][0]
        # print 'stat 2 up uni: drop rx tx'
        # print numUpstreamPacketsUnicastDrop0,numUpstreamPacketsUnicastRx0, numUpstreamPacketsUnicastTx0
        rates[i] = 1.0 - np.float64(numUpstreamPacketsUnicastDrop0)/(numUpstreamPacketsUnicastRx0+numUpstreamPacketsUnicastTx0)

        # numDownstreamPacketsBroadcastDrop0 = stat['numDownstreamPacketsBroadcastDrop0'][0] # what the hell is that...
        # numDownstreamPacketsBroadcastRx0 = stat['numDownstreamPacketsBroadcastRx0'][0] # what the hell is that...
        # numDownstreamPacketsBroadcastTx0 = stat['numDownstreamPacketsBroadcastTx0'][0] # what the hell is that...
        # print 'stat 2 down broad'
        # print numDownstreamPacketsBroadcastDrop0,numDownstreamPacketsBroadcastRx0, numDownstreamPacketsBroadcastTx0
        #
        # numDownstreamPacketsUnicastDrop0 = stat['numDownstreamPacketsUnicastDrop0'][0] # what the hell is that...
        # numDownstreamPacketsUnicastRx0 = stat['numDownstreamPacketsUnicastRx0'][0] # what the hell is that...
        # numDownstreamPacketsUnicastTx0 = stat['numDownstreamPacketsUnicastTx0'][0] # what the hell is that...
        # rates[i] = 1 #-float(numUpstreamPacketsBroadcastDrop0)/(float(numUpstreamPacketsBroadcastRx0)+float(numUpstreamPacketsBroadcastTx0))
        # print 'stat 2 down uni'
        # print numDownstreamPacketsUnicastDrop0,numDownstreamPacketsUnicastRx0, numDownstreamPacketsUnicastTx0
        m = re.search(r' ([0-9]+)\% packet loss', '\n'.join(ping_output))
        ping_rate = 1 - float(m.group(1))/100
        print "Unicast rate (upstream): ", rates[i]
        print "Broadcast rate (upstream): ", 1.0 - np.float64(numUpstreamPacketsBroadcastDrop0)/(numUpstreamPacketsBroadcastRx0+numUpstreamPacketsBroadcastTx0)
        print "Ping output: ", np.sqrt(ping_rate)
        print "Calculated SINR: ", radio_calculations.SINRdB(parameters)

    #pyplot.plot(distances, rates)
    #pyplot.xscale('log')
    #pyplot.show()


