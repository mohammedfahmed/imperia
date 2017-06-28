# Map sources

# SRTM: American mission that released the 90m-30m (3-1 arcsec) DEM (digital elevation model)
# after an interferometric Shuttle mission (STS-99). originally
# 1 arcsec only for USA, now also for the world. Data is available
# through USGS (US geological survey). Only 56 S - 60 N is included
# Format: .hgt
# Coordinates: WGS84 ellipsoid, filled with gravity (?) EGM96
# Data has some voids
# version 3 is more regular, integrated with ASTER data
# other void-filled versions: CGIAR-CSI, USGS HydroSheds


# ASTER: American-Japanese mission that released 90m-15m "GDEM" (global DEM) data after
# optical satellite measurements. 83 S-83 N is included. Quality is much more variable
# than SRTM and there are artifacts (clouds can shadow optical photos)
# version 2 has eliminated some of the artifacts
#

# Actual sources:
# From USGS (as files) you have SRTM3 (check also EROS)
# http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/
# name of files are -> ^ (34N33E has 34-35N 33-34E)

# NASA Earth explorer (check also LP DAAC) has many maps of different sources:
# SRTMGL1 is 1 arcsec for the whole world
# https://earthexplorer.usgs.gov/ (needs login)
# login EROS: arongo1, pass: arongo12, email: ringo@mailinator.net
# login URS Earthdata: arongo1, pass: arongo12UU, email: ringo@mailinator.net

# LIDAR data is for urban purposes

# NB: SPLAT! uses positive longitude for W instead of for E!

import subprocess
import tempfile
import shutil
import os


def get_pathloss(tx_lat,tx_lon,tx_height,rx_lat,rx_lon,rx_height):
    path_splathd = '/usr/local/bin/splat-hd'
    path_mapdir = '/home/ubuntu/Python/maps/SRTM3GL1'

    path_tmp = tempfile.mkdtemp()
    tx =  open(os.path.join(path_tmp,"tx.qth"),"w")
    rx =  open(os.path.join(path_tmp,"rx.qth"),"w")
    params =  open(os.path.join(path_tmp,"tx.lrp"),"w")

    tx.write('transmitter\n%g\n%g\n%g meters\n' % (tx_lat, -tx_lon, tx_height)) # SPLAT! convention for longitude
    rx.write('receiver\n%g\n%g\n%g meters\n' % (rx_lat, -rx_lon, rx_height)) # SPLAT! convention for longitude

    params.write('''15.000 ; Earth Dielectric Constant (Relative permittivity)
% 0.005 ; Earth Conductivity (Siemens per meter)
% 301.000 ; Atmospheric Bending Constant (N-units)
% 647.000 ; Frequency in MHz (20 MHz to 20 GHz)
% 5 ;Radio Climate (5 = Continental Temperate)
% 0 ;Polarization (0 = Horizontal, 1 = Vertical)
% 0.50 ; Fraction of situations (50% of locations)
% 0.90 ; Fraction of time (90% of the time)
% 46000.0 ; ERP in Watts (optional)
''')
    params.close()
    tx.close()
    rx.close()
    subprocess.call([path_splathd, "-t", tx.name, '-r', rx.name, '-d', path_mapdir,
                     '-p', 'terrain_profile.png', '-l', 'loss.png'],
                    shell=False)

    shutil.rmtree(path_tmp)

get_pathloss(32.73, 35.09, 1000, 32.79, 34.98, 2000)

