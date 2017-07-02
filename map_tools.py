# convention: lAtitude before lOngitude always!!

# see https://librenepal.com/article/reading-srtm-data-with-python/
import os
import numpy as np
import matplotlib.pyplot as plt

SAMPLES = 3601 # hd data (if it were SRTM3 would be 1201)
HGTDIR = '/home/ubuntu/Python/maps/SRTM3GL1' # All 'hgt' files will be kept here uncompressed


def get_elevation(lat, lon):
    hgt_file = get_file_name(lat, lon)
    if hgt_file:
        return read_elevation_from_file(hgt_file, lat, lon)
    # Treat it as data void as in SRTM documentation
    # if file is absent
    return -32768


def read_elevation_from_file(hgt_file, lat, lon):
    with open(hgt_file, 'rb') as hgt_data:
        # HGT is 16bit signed integer(i2) - big endian(>)
        elevations = np.fromfile(hgt_data, np.dtype('>i2'), SAMPLES * SAMPLES) \
            .reshape((SAMPLES, SAMPLES))

        lat_row = int(round((lat - int(lat)) * (SAMPLES - 1), 0))
        lon_row = int(round((lon - int(lon)) * (SAMPLES - 1), 0))

        return elevations[SAMPLES - 1 - lat_row, lon_row].astype(int)


def get_hgt_data(hgt_file):
    if(hgt_file):
        with open(hgt_file, 'rb') as hgt_data:
            # HGT is 16bit signed integer(i2) - big endian(>)
            elevations = np.fromfile(hgt_data, np.dtype('>i2'), SAMPLES * SAMPLES) \
                .reshape((SAMPLES, SAMPLES))
            elevations = np.rot90(elevations,3)
    else:
        elevations = np.zeros([SAMPLES, SAMPLES],dtype=np.int16)

    return elevations


def get_file_name(lat, lon):
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


def elevations_in_bounds(lat,lon):
    lat_start = int(lat[0])
    lat_end = int(lat[1]) + 1
    lon_start = int(lon[0])
    lon_end = int(lon[1]) + 1

    lat_axis = np.linspace(lat_start,lat_end, (lat_end-lat_start)*(SAMPLES-1)+1)
    lon_axis = np.linspace(lon_start,lon_end, (lon_end-lon_start)*(SAMPLES-1)+1)
    z_data = np.zeros([(lon_end-lon_start)*(SAMPLES-1)+1, (lat_end-lat_start)*(SAMPLES-1)+1]) # lon is x, lat is y
    for lti in range(lat_end-lat_start):
        for lni in range(lon_end-lon_start):
            hgt_file = get_file_name(lat_start+lti, lon_start+lni)
            hgt_data = get_hgt_data(hgt_file)
            z_data[(SAMPLES-1)*lni:(SAMPLES-1)*(lni+1)+1,(SAMPLES-1)*lti:(SAMPLES-1)*(lti+1)+1]=hgt_data
    data = {}
    lon_condition = (lon_axis >= lon[0]) & (lon_axis <= lon[1])
    lat_condition = (lat_axis >= lat[0]) & (lat_axis <= lat[1])
    data['lat'] = lat_axis[lat_condition]
    data['lon'] = lon_axis[lon_condition]
    z_data = z_data[:,lat_condition]
    z_data = z_data[lon_condition,:]
    data['z'] = z_data
    return data

def degreesToRadians(degrees):
    return degrees * np.pi / 180.0


def distance(lat1, lon1, lat2, lon2):
    earthRadiusm = 6371.0e3
    dlat = degreesToRadians(lat2 - lat1)
    dlon = degreesToRadians(lon2 - lon1)

    lat1 = degreesToRadians(lat1)
    lat2 = degreesToRadians(lat2)
    a = np.sin(dlat / 2.0) * np.sin(dlat / 2.0) + np.sin(dlon / 2.0) * np.sin(dlon / 2.0) * np.cos(lat1) * np.cos(lat2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return earthRadiusm * c

def distance_elevated(lat1, lon1, lat2, lon2):
    d = distance(lat1, lon1, lat2, lon2)
    h = abs(get_elevation(lat1, lon1)-get_elevation(lat2, lon2))
    return np.sqrt(d**2 + h**2)

def distance_elevated_h(lat1, lon1, height1, lat2, lon2, height2):
    d = distance(lat1, lon1, lat2, lon2)
    h = abs(get_elevation(lat1, lon1)+height1-get_elevation(lat2, lon2)-height2)
    return np.sqrt(d**2 + h**2)

def distance_h(lat1, lon1, height1, lat2, lon2, height2):
    d = distance(lat1, lon1, lat2, lon2)
    h = abs(height2-height1)
    return np.sqrt(d**2 + h**2)

def draw_elevation(lat,lon, points=([],[],[])):
    d = elevations_in_bounds(lat, lon)
    #d = elevations_in_bounds([30.4, 30.5], [34.5, 34.6])

    X, Y = np.meshgrid(d['lon'], d['lat'],indexing='ij')
    Z = d['z']
    plt.figure()
    #CS = plt.imshow(Z, extent=(lon[0], lon[1], lat[0], lat[1]))
    CS = plt.contour(X,Y,d['z'],levels=range(0, 1000, 20))
    #plt.clabel(CS, inline=1, fontsize=10)
    plt.title('Elevation [m]')
    y = points[1]
    x = points[0]
    plt.scatter(x, y,marker='D',s=10,color='r')
    for i in range(len(points[2])):
        plt.annotate(points[2][i], xy=(points[0][i], points[1][i]), xytext=(points[0][i]-1e-2, points[1][i]-1e-2),
                arrowprops=dict(facecolor='black', shrink=0.05),
                )
#    plt.draw()
    plt.show(block=True)

if __name__ == "__main__":
    draw_elevation([29.9, 33.1], [34.5, 35.9])