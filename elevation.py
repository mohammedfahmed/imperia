import os
import numpy as np

SAMPLES = 3601 # hd data (if it were SRTM3 would be 1201)
HGTDIR = '/home/ubuntu/Python/maps/SRTM3GL1' # All 'hgt' files will be kept here uncompressed


def get_elevation(lon, lat):
    hgt_file = get_file_name(lon, lat)
    if hgt_file:
        return read_elevation_from_file(hgt_file, lon, lat)
    # Treat it as data void as in SRTM documentation
    # if file is absent
    return -32768


def read_elevation_from_file(hgt_file, lon, lat):
    with open(hgt_file, 'rb') as hgt_data:
        # HGT is 16bit signed integer(i2) - big endian(>)
        elevations = np.fromfile(hgt_data, np.dtype('>i2'), SAMPLES * SAMPLES) \
            .reshape((SAMPLES, SAMPLES))

        lat_row = int(round((lat - int(lat)) * (SAMPLES - 1), 0))
        lon_row = int(round((lon - int(lon)) * (SAMPLES - 1), 0))

        return elevations[SAMPLES - 1 - lat_row, lon_row].astype(int)


def get_file_name(lon, lat):
    """
    Returns filename such as N27E086.hgt, concatenated
    with HGTDIR where these 'hgt' files are kept
    """

    if lat >= 0:
        ns = 'N'
    elif lat < 0:
        ns = 'S'

    if lon >= 0:
        ew = 'E'
    elif lon < 0:
        ew = 'W'

    hgt_file = "%(ns)s%(lat)02d%(ew)s%(lon)03d.hgt" % {'lat': abs(lat), 'lon': abs(lon), 'ns': ns, 'ew': ew}
    hgt_file_path = os.path.join(HGTDIR, hgt_file)
    if os.path.isfile(hgt_file_path):
        return hgt_file_path
    else:
        return None



print get_elevation(34.997459,32.799310)
