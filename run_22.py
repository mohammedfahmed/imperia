#
# ........ FAST & DIRTY ........
#

#base station Haifa
#elvation 457
#lat 32.7625
#lon 35.0195

#haifa  airport
#elevation 8
#lat 32.8119
#lon 35.0433


#Naharia
#elevation 1000
#lat 33.005811
#lon 35.099478

#Naharia GDUD
#elevation 8
#lat 33.010763
#lon 35.088425

#Tiberias
#elevation 1000
#lat 32.794592
#lon 35.532089


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


import radio_calculations

from namedlist import namedlist

project_dir = "/home/ubuntu/Desktop/emane-tutorial/22/"

@contextmanager
def open_22():
    # subprocess.call(["sudo", "-S", "/home/ubuntu/Desktop/two_points/start"], shell=False) best but annoying to type the password..
    subprocess.call(["cd /home/ubuntu/Desktop/emane-tutorial/22/; echo ubuntu | sudo -S ./demo-start"], shell=True)
    try:
        yield
    finally:
        # stop emane
        subprocess.call(["cd /home/ubuntu/Desktop/emane-tutorial/22/; echo ubuntu | sudo -S ./demo-stop"], shell=True)
        # subprocess.call(["sudo", "-S", "/home/ubuntu/Desktop/two_points/end"], shell=False)


@contextmanager
def open_sdt():
    # subprocess.call(["sudo", "-S", "/home/ubuntu/Desktop/two_points/start"], shell=False) best but annoying to type the password..
    subprocess.call(["cd /home/ubuntu/Desktop/emane-tutorial/22/; echo ubuntu | sudo -S ./demo-start"], shell=True)
    try:
        yield
    finally:
        # stop emane
        subprocess.call(["cd /home/ubuntu/Desktop/emane-tutorial/22/; echo ubuntu | sudo -S ./demo-stop"], shell=True)



loc_haifabase = ((32.7625, 35.0195), 457)
loc_haifaair = ((32.8119, 35.0433), 8)
loc_naharia = ((33.005811, 35.099478),1000)
loc_naharia_gdud = ((33.010763, 35.088425), 8)
loc_tiberias = ((32.794592, 35.532089),1000)

NEM = namedlist('NEM', 'id latitude longitude')
radioNEMs = []
a2gNEM7 = NEM(7, 32.8119, 35.0433)
a2gNEM8 = NEM(8, 33.010963, 35.088425)
a2gNEM9 = NEM(9, 33.015844, 35.0433)
pl89 = 0

default_p_radio = dict(f_Hz= 600e6, ERP_W=35)
default_p_a2g = dict(f_Hz= 2e9, ERP_W=35)

sdtcmd_path = "/home/ubuntu/Software/sdt-linux-amd64-2.1/sdtcmd"


def freespace_pathloss(tx, rx):
    f = 600e6 # Hertz
    c = 299792458.0
    dist = map_tools.distance_elevated(tx.latitude, tx.longitude, rx.latitude, rx.longitude)
    return 20*np.log10(np.pi*4*dist*f/c)

def freespace_pathloss_a2g(air,ground,p):
    height_m = 500 # plane height
    f = p['f_Hz'] # Hertz
    c = 299792458.0
    dist = map_tools.distance_elevated(air.latitude, air.longitude, ground.latitude, ground.longitude)
    return 20*np.log10(np.pi*4*dist*f/c)

def egli_pathloss(tx,rx,p=default_p_radio):
    f_MHz = p['f_Hz']/1e6 # MHz
    dist_m = map_tools.distance_elevated(tx.latitude, tx.longitude, rx.latitude, rx.longitude)
    dist_km = dist_m/1000 # km
    ant_height_m = 2 # m
    return 88 + 20*np.log10(f_MHz)+40*np.log10(dist_km)-20*np.log10(ant_height_m*ant_height_m)

def egli_los_pathloss(tx,rx,p=default_p_radio):
    f_MHz = p['f_Hz']/1e6 # MHz
    c = 299792458.0
    dist_m = map_tools.distance_elevated(tx.latitude, tx.longitude, rx.latitude, rx.longitude)
    dist_km = dist_m/1000 # km
    ant_height_m = 2 # m
    if dist_km <= 0.5:
        wvlength = c/(f_MHz*1e6)
        acs_dB = 12.66-3.5*np.log10(ant_height_m/wvlength)+0.07*dist_km
        fsl_pl_dB = 32.45 + 20*np.log10(f_MHz)+20*np.log10(dist_km)
        return acs_dB + fsl_pl_dB
    else:
        return 88 + 20*np.log10(f_MHz)+40*np.log10(dist_km)-20*np.log10(ant_height_m*ant_height_m)

def signalserver_pathloss(tx,rx,p=default_p_radio):
    # power of transmitter: 35 W
    # frequency 600 MHz
    # model (-pm) irregular terrain simple
    # antenna heights (-txh -rxh): 2 m
    f_MHz = p['f_Hz']/1e6
    ERP_W = p['ERP_W']
    ssdir = os.path.join(project_dir, "persist/signalserver")
    if not os.path.exists(ssdir):
        os.makedirs(ssdir)
    out_file = os.path.join(ssdir, ("out%d_%d.hd" % (tx.id, rx.id)))
    out = subprocess.check_output(["/home/ubuntu/Software/Signal-Server/signalserverHD", "-m","-dbm",
                             "-sdf", "/home/ubuntu/Python/maps/SRTM3GL1/",
                             "-erp", str(ERP_W),
                             "-f", str(f_MHz),
                             "-o", out_file,
                             "-pm", "11",
                             "-txh", "2",
                             "-rxh", "2",
                             "-lat", str(tx.latitude),
                             "-lon", str(tx.longitude),
                             "-rla", str(rx.latitude),
                             "-rlo", str(rx.longitude)])
    f = open(out_file + ".txt", "r")
    s = f.read()
    m = re.search(r'Computed path loss: (.+) dB', s)
    pl = float(m.group(1))
    return pl

def splat_pathloss(tx,rx,p=default_p_radio):
    # power of transmitter: 25 W
    # frequency 600 MHz
    # model (-pm) irregular terrain simple
    # antenna heights (-txh -rxh): 2 m
    f_MHz = p['f_Hz']/1e6
    ERP_W = p['ERP_W']
    ssdir = os.path.join(project_dir, "persist/splat")
    if not os.path.exists(ssdir):
        os.makedirs(ssdir)
    tx_path = os.path.join(ssdir, ("tx%d_%d.qth" % (tx.id, rx.id)))
    rx_path = os.path.join(ssdir, ("rx%d_%d.qth" % (tx.id, rx.id)))
    lrp_path = os.path.join(ssdir, ("tx%d_%d.lrp" % (tx.id, rx.id)))

    path_splathd = '/usr/local/bin/splat-hd'
    path_mapdir = '/home/ubuntu/Python/maps/SRTM3GL1'

    tx_file = open(tx_path, "w")
    rx_file = open(rx_path, "w")
    params_file = open(lrp_path, "w")

    tx_file.write('transmitter\n%g\n%g\n%g meters\n' % (tx.latitude, -tx.longitude, 2))  # SPLAT! convention for longitude
    rx_file.write('receiver\n%g\n%g\n%g meters\n' % (rx.latitude, -rx.longitude, 2))  # SPLAT! convention for longitude

    params_file.write('''15.000 ; Earth Dielectric Constant (Relative permittivity)
    % 0.005 ; Earth Conductivity (Siemens per meter)
    % 301.000 ; Atmospheric Bending Constant (N-units)
''')
    params_file.write(("%% %f ; Frequency in MHz (20 MHz to 20 GHz)" % (f_MHz)))
    params_file.write('''% 5 ;Radio Climate (5 = Continental Temperate)
    % 0 ;Polarization (0 = Horizontal, 1 = Vertical)
    % 0.50 ; Fraction of situations (50% of locations)
    % 0.90 ; Fraction of time (90% of the time)
    % 35.0 ; ERP in Watts (optional)
''')
    params_file.close()
    tx_file.close()
    rx_file.close()
    out = subprocess.check_output([path_splathd,
                                   "-f", str(f_MHz),
                                    "-t", tx_path,
                                    '-r', rx_path,
                                    '-o', ('test_%d_%d.ppm' % (tx.id, rx.id)),
                                    '-d', path_mapdir,
                                    '-p', ('terrain_profile_%d_%d.png' % (tx.id, rx.id)),
                                    '-l', ('loss_%d_%d.png' % (tx.id, rx.id)),
                                   '-dbm',
                                   '-metric',
                                   '-L 2'],
                                    shell=False, cwd=ssdir)
    os.rename(os.path.join(ssdir,"transmitter-site_report.txt"), os.path.join(ssdir,("transmitter-site_report_%d_%d.txt" % (tx.id, rx.id))))
    os.rename(os.path.join(ssdir,"transmitter-to-receiver.txt"), os.path.join(ssdir,("transmitter--to-receiver_%d_%d.txt" % (tx.id, rx.id))))

    f = open(os.path.join(ssdir,("transmitter--to-receiver_%d_%d.txt" % (tx.id, rx.id))) , "r")
    s = f.read()
    m = re.search(r'ITWOM Version 3.0 path loss: (.+) dB', s)
    pl = float(m.group(1))
    return pl

def message_sdt(s):
    os.system(sdtcmd_path + " " + s)

def init_nodes(service):
    #message_sdt(b"reset")
    message_sdt(b"bgbounds 35.54,32.75,35.01,33.02")
    message_sdt(("sprite base_station image %s size 52,25" % (os.path.join(project_dir,'base_station.png'))))
    message_sdt(b"node node-01 type base_station label blue")
    message_sdt(b"node node-01 position 35.0195,32.7625")
    message_sdt(("sprite plane image %s size 52,25" % (os.path.join(project_dir,'plane.png'))))
    message_sdt(b"node node-02 type plane label blue")
    message_sdt(b"node node-02 position 35.0433,32.8119")
    message_sdt(b"link node-01,node-02,wifi")
    message_sdt(("sprite soldier image %s size 52,25" % (os.path.join(project_dir,'soldier.gif'))))
    message_sdt(b"node node-03 type soldier label blue")
    message_sdt(b"node node-03 position 35.088425,33.010963")
    message_sdt(b"node node-06 type soldier label blue")
    message_sdt(b"node node-06 position 35.147439,33.015844")

    # create an event setting base station position

    event = LocationEvent()
    event.append(11, latitude=32.7625, longitude=35.0195, altitude=457.000000)
    service.publish(0, event)
    # create an event setting plane position
    event = LocationEvent()
    event.append(12, latitude=32.8119, longitude=35.0433, altitude=500.000000)
    service.publish(0, event)

    # event = LocationEvent()
    # event.append(7, latitude=a2gNEM7.latitude, longitude=a2gNEM7.longitude, altitude=500.000000)
    # service.publish(0, event)
    #
    # event = LocationEvent()
    # event.append(8, latitude=a2gNEM8.latitude, longitude=a2gNEM8.longitude, altitude=8.00000)
    # service.publish(0, event)
    #
    # event = LocationEvent()
    # event.append(9, latitude=a2gNEM9.latitude, longitude=a2gNEM9.longitude, altitude=8.00000)
    # service.publish(0, event)

    #
    # # set 1 men position
    # event = LocationEvent()
    radioNEMs.append(NEM(1, 33.010763, 35.088425))
    radioNEMs.append(NEM(2, 33.011863, 35.088425))
    radioNEMs.append(NEM(3, 33.012963, 35.088425))

    # # set 2 men position
    # event = LocationEvent()
    radioNEMs.append(NEM(4, 33.015644, 35.147439))
    radioNEMs.append(NEM(5, 33.018744, 35.147439))
    radioNEMs.append(NEM(6, 33.015844, 35.140439))

    update_radio_pathlosses(service)
    update_89_pathloss(service)
    update_a2g_pathlosses(service)
    #time.sleep(20)


def update_radio_pathlosses(service):
    max_id = max([i.id for i in radioNEMs])
    matrix = np.zeros((max_id+1, max_id+1))
    for nemtx in radioNEMs:
        event = PathlossEvent()
        for nemrx in radioNEMs:
            if (nemrx.id != nemtx.id):
                pl = splat_pathloss(nemtx,nemrx)
                matrix[nemtx.id][nemrx.id] = pl
                event.append(nemrx.id, forward=pl)
        service.publish(nemtx.id, event)

    fmatrix = np.zeros((max_id + 1, max_id + 1))
    ematrix = np.zeros((max_id + 1, max_id + 1))
    ssmatrix = np.zeros((max_id + 1, max_id + 1))
    for nemtx in radioNEMs:
        for nemrx in radioNEMs:
            if (nemrx.id != nemtx.id):
                pl = freespace_pathloss(nemtx,nemrx)
                fmatrix[nemtx.id][nemrx.id] = pl
    for nemtx in radioNEMs:
        for nemrx in radioNEMs:
            if (nemrx.id != nemtx.id):
                pl = egli_pathloss(nemtx,nemrx)
                ematrix[nemtx.id][nemrx.id] = pl
    for nemtx in radioNEMs:
        for nemrx in radioNEMs:
            if (nemrx.id != nemtx.id):
                pl = signalserver_pathloss(nemtx,nemrx)
                ssmatrix[nemtx.id][nemrx.id] = pl
    print "freespace:"
    print np.array_str(fmatrix,max_line_width=200,precision=5)
    print "egli:"
    print np.array_str(ematrix,max_line_width=200, precision=5)
    print "signalserver:"
    print np.array_str(ssmatrix,max_line_width=200, precision=5)

    print "actual:"
    print np.array_str(matrix,max_line_width=200, precision=5)

    for nem in radioNEMs:
        print nem.id, nem.latitude, nem.longitude
    map_tools.draw_elevation([32.7, 33.1], [34.9, 35.2], ([x.longitude for x in radioNEMs],[x.latitude for x in radioNEMs], [str(x.id) for x in radioNEMs]))

def update_89_pathloss(service):
    event = PathlossEvent()
    p = default_p_a2g
    pl89 = signalserver_pathloss(a2gNEM8, a2gNEM9,p)
    event.append(9, forward=pl89)
    service.publish(8, event)

    pl98 = signalserver_pathloss(a2gNEM9, a2gNEM8,p)
    event.append(8, forward=pl98)
    service.publish(9, event)
    print "Pathloss 8->9", pl89
    print "Pathloss 9->8", pl98


def update_a2g_pathlosses(service):
    p = default_p_a2g
    pl78 = freespace_pathloss_a2g(a2gNEM7,a2gNEM8,p)
    pl79 = freespace_pathloss_a2g(a2gNEM7,a2gNEM9,p)
    print pl78, pl79

    event = PathlossEvent()
    event.append(8, forward=pl78)
    event.append(9, forward=pl79)
    service.publish(7, event)

    event = PathlossEvent()
    event.append(7, forward=pl78)
    service.publish(8, event)

    event = PathlossEvent()
    event.append(7, forward=pl78)
    service.publish(9, event)


def move_node(service, coordinates):
    n = 1000
    for i in range(0, len(coordinates)):
        if i == 0:
            continue
        for counter in range(0, n):
            counter = float(counter)/n
            lon = coordinates[i-1][0] + counter * (coordinates[i][0] - coordinates[i-1][0])
            lat = coordinates[i-1][1] + counter * (coordinates[i][1] - coordinates[i-1][1])
            message_sdt("node node-02 position" + " " + str(lon)[0:7] + "," + str(lat)[0:7] + "")
            message_sdt(b"wait 50.0")
            a2gNEM7.latitude = lat
            a2gNEM7.longitude = lon
            # create an event setting plane position only for NEM 12 (comm is precomputed)
            event = LocationEvent()
            event.append(12, latitude=lat, longitude=lon, altitude=500.000000)
            service.publish(0, event)
            # event = LocationEvent()
            # event.append(7, latitude=lat, longitude=lon, altitude=500.000000)
            # service.publish(0, event)
            update_a2g_pathlosses(service)
            time.sleep(0.01)
        time.sleep(2)

if __name__ == "__main__":
    with open_22():
        time.sleep(5)
        esh = EMANEShell('localhost',47000)
        # Debug level
        #esh.do_loglevel('4')
        # haifa airport, Naharia, Tiberias, Haifa airport 33.013 35.05
        coordinates = [( 35.0433, 32.8119), (35.05, 33.017947), (35.532089, 32.794592), (35.0433, 32.8119)]
        service = EventService(('224.1.2.8', 45703, 'emanenode0'))

        if False:
             sdtproc = subprocess.Popen(["/home/ubuntu/Software/sdt-linux-amd64-2.1/sdt3d/sdt3d.sh"])
             time.sleep(15)

        init_nodes(service)
        raw_input("Press Enter to continue...")
        move_node(service, coordinates)
        print "Done"
        #pyplot.plot(distances, rates)
        #pyplot.xscale('log')
        #pyplot.show()
