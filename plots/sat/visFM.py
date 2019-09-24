import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
from datetime import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import metpy
import numpy as np
from netCDF4 import num2date
from siphon.catalog import TDSCatalog
import xarray as xr
from xarray.backends import NetCDF4DataStore

# Grab the latest data from the data server.
cat = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/satellite'
                 '/goes/east/products/CloudAndMoistureImagery/CONUS/Channel02'
                 '/current/catalog.xml')
latest_data = cat.datasets[0]

# Parse the data.
data = latest_data.remote_access(use_xarray=True)
sat_data = data.metpy.parse_cf('Sectorized_CMI')
geos = sat_data.metpy.cartopy_crs

# Extract cordinate information.
x = sat_data.metpy.x
y = sat_data.metpy.y

# Correct reflectance.
sat_data = np.sqrt(sat_data)

# Set projection and colorbar information.
fig = plt.figure(figsize=(10, 15))

lc = ccrs.LambertConformal(central_longitude=-97.5, standard_parallels=(38.5,
                                                                        38.5))
ax = fig.add_subplot(1, 1, 1, projection=lc)
ax.set_extent([-104.1, -95.5, 32.1, 39.1], crs=ccrs.PlateCarree())
ax.imshow(sat_data, extent=(x[0], x[-1], y[-1], y[0]), transform=geos,
                 interpolation='none', cmap='Greys_r', origin='upper')

# Create the map.
ax.add_feature(cfeature.OCEAN.with_scale('50m'),facecolor='slategrey',edgecolor='none',zorder=5)
ax.add_feature(cfeature.LAND.with_scale('50m'),edgecolor='dimgray',
                                               facecolor='#626262',
                                               zorder=0)
ax.add_feature(cfeature.BORDERS.with_scale('50m'),zorder=2)
ax.add_feature(cfeature.LAKES.with_scale('50m'),linewidth=.5,
                                                facecolor='lightsteelblue',
                                                edgecolor='dimgray',
                                                zorder=3)
ax.add_feature(cfeature.STATES.with_scale('50m'),linewidth=.5,
                                                 edgecolor='black',
                                                 zorder=6)

# Import the county map.
reader = shpreader.Reader('/home/victoraalvarez/Documents/pythonScripts'
                          '/pythonPlayground/mapFiles/county_map/countyl010g.shp')
counties = list(reader.geometries())
COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())

ax.add_feature(COUNTIES,linewidth=.5,facecolor='none',edgecolor='black',
                        alpha=0.5, zorder=4)

# Import the forecast area.
reader = shpreader.Reader('/home/victoraalvarez/Documents/pythonScripts/'
                          'pythonPlayground/mapFiles/fa/fa3.shp')
fa = list(reader.geometries())
FA = cfeature.ShapelyFeature(fa, ccrs.PlateCarree())

ax.add_feature(FA,linewidth=2.5,facecolor='none',edgecolor='black',zorder=7)
ax.add_feature(FA,linewidth=.5,facecolor='none',edgecolor='white',zorder=8)

# Add titles and timestamp.
timestamp = datetime.strptime(data.start_date_time, '%Y%j%H%M%S')

plt.title('Valid Time: {}'.format(timestamp), loc='right')
plt.title('GOES-EAST CONUS Ch. 2', loc='left')

# Plot!
plt.savefig('./images/VISIBLE.png', dpi=300, bbox_inches='tight')
