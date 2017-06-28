# Radio models
# Irregular Terrain Model (ITM)	'Longley Rice' Model. US Gov. general purpose model used by FCC	20-20,000MHz	itm.cc
#
# Line of Sight (LOS)	Simple model for viewing obstructions	Any	los.cc
#
# Okumura-Hata	Hata model for cellular communications in urban areas	150-1500MHz	hata.cc
#
#  ECC33 (ITU-R P.529)	ECC33 model for cellular and microwave communications	700-3500MHz	ecc33.cc
#
# Stanford University Interim (SUI)	SUI model for WIMAX communications	1900-11000MHz	sui.cc
#
# COST231-Hata	European COST231 frequency extension to Hata model for urban areas	150-2000MHz	cost.cc
#
# ITU-R P.525	Free Space Path Loss model	20-100,000MHz	fspl.cc
#
#  ITM with obstructions 3.0	Enhanced ITM general purpose model. The Author says it's better. See for yourself.	20-100,000MHz	itwom3.0.cc
#
# Ericsson 9999	Ericsson 9999 model for cellular communications up to 1900MHz	150-1900MHz	ericsson.cc
#
# Egli VHF/UHF	General purpose VHF/UHF model. More conservative than FSPL	30-1000MHz	egli.cc
#
# Free space
#


# SPLAT!
# Free-space

# SignalServer
#

# Q-REP
#

path_ssHD = "/home/ubuntu/Software/Signal-Server/signalserverHD"

# '/home/ubuntu/Software/Signal-Server/signalserverHD'  -m -sdf '/home/ubuntu/Python/maps/SRTM3GL1/'  -lat 32.5 -lon 35.0 -txh 15 -rxh 2 -m -dbm -rt -100 -R 5 -erp 25 -f 450 -o try2.hd -pm 1 -res 3600 -t
# Relevant arguments
# Usage: signalserver [data options] [input options] [output options] -o outputfile
#
# Data:
#      -sdf Directory containing SRTM derived .sdf DEM tiles
#      -lid ASCII grid tile (LIDAR) with dimensions and resolution defined in header
#      -udt User defined point clutter as decimal co-ordinates: 'latitude,longitude,height'
#      -clt MODIS 17-class wide area clutter in ASCII grid format
# Input:
#      -lat Tx Latitude (decimal degrees) -70/+70
#      -lon Tx Longitude (decimal degrees) -180/+180
#      -txh Tx Height (above ground)
#      -rla (Optional) Rx Latitude for PPA (decimal degrees) -70/+70
#      -rlo (Optional) Rx Longitude for PPA (decimal degrees) -180/+180
#      -f Tx Frequency (MHz) 20MHz to 100GHz (LOS after 20GHz)
#      -erp Tx Effective Radiated Power (Watts) including Tx+Rx gain
#      -rxh Rx Height(s) (optional. Default=0.1)
#      -rxg Rx gain dBi (optional for text report)
#      -hp Horizontal Polarisation (default=vertical)
#      -gc Random ground clutter (feet/meters)
#      -m Metric units of measurement
#      -te Terrain code 1-6 (optional)
#      -terdic Terrain dielectric value 2-80 (optional)
#      -tercon Terrain conductivity 0.01-0.0001 (optional)
#      -cl Climate code 1-6 (optional)
#      -rel Reliability for ITM model 50 to 99 (optional)
#      -resample Resample Lidar input to specified resolution in meters (optional)
# Output:
#      -dbm Plot Rxd signal power instead of field strength
#      -rt Rx Threshold (dB / dBm / dBuV/m)
#      -o Filename. Required.
#      -R Radius (miles/kilometers)
#      -res Pixels per tile. 300/600/1200/3600 (Optional. LIDAR res is within the tile)
#      -pm Propagation model. 1: ITM, 2: LOS, 3: Hata, 4: ECC33,
#      	  5: SUI, 6: COST-Hata, 7: FSPL, 8: ITWOM, 9: Ericsson, 10: Plane earth, 11: Egli VHF/UHF
#      -pe Propagation model mode: 1=Urban,2=Suburban,3=Rural
#      -ked Knife edge diffraction (Already on for ITM)
# Debugging:
#      -t Terrain greyscale background
#      -dbg Verbose debug messages
#      -ng Normalise Path Profile graph
#      -haf Halve 1 or 2 (optional)
#      -nothreads Turn off threaded processing

# first test
lat = [34.809, 34.8506]
lon = [32.2141, 32.2279]

