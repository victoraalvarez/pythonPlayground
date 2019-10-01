# -------------------
# ---------------------------------------
# SET IMPORTS
# ---------------------------------------
# -------------------

import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
from datetime import datetime, timedelta
import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import matplotlib.ticker as mticker
import metpy
import metpy.calc as mpcalc
from metpy.units import units
from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
from netCDF4 import num2date
import numpy as np
import scipy.ndimage as ndimage
import shapefile
from siphon.catalog import TDSCatalog
import xarray as xr
from xarray.backends import NetCDF4DataStore

# -------------------
# ---------------------------------------
# SET VARIABLES
# ---------------------------------------
# -------------------

# Define current time using datetime module.
now = datetime.utcnow()

# Define datasets to wanted.
mslp = 'MSLP_MAPS_System_Reduction_msl'
vsfc_wind = 'v-component_of_wind_height_above_ground'
usfc_wind = 'u-component_of_wind_height_above_ground'

# -------------------
# ---------------------------------------
# GRAB THE VISIBLE SATELLITE DATA
# ---------------------------------------
# -------------------

# Use TDSCatalog to begin data access & grab latest file.
cat_vis = TDSCatalog('https://thredds-test.unidata.ucar.edu/thredds/catalog/'
                     'satellite/goes/east/products/CloudAndMoistureImagery/'
                     'CONUS/Channel02/current/catalog.xml')
latestvis = cat_vis.datasets[-1]

# Parse the data.
xrdata = latestvis.remote_access(use_xarray=True)
parsedvis = xrdata.metpy.parse_cf('Sectorized_CMI')
geos_proj = parsedvis.metpy.cartopy_crs

# Grab the coordinates.
x = parsedvis.metpy.x
y = parsedvis.metpy.y

# Adjust reflectance.
parsedvis = np.sqrt(parsedvis)

# -------------------
# ---------------------------------------
# GRAB THE RAP SURFACE MSLP & WINDS
# ---------------------------------------
# -------------------

# Use TDSCatalog to begin data access, NCSS to subset, & grab latest file.
rap_cat = TDSCatalog('https://thredds-test.unidata.ucar.edu/thredds/catalog/'
                     'grib/NCEP/RAP/CONUS_13km/latest.xml')
latestrap = rap_cat.datasets[0]
ncss = latestrap.subset()

# Query MSLP data.
mslp_data = ncss.query()
mslp_data.variables(mslp)
mslp_data.add_lonlat().lonlat_box(north=44, south=27, east=271, west=250)
mslp_data.time(now)
mslp_dataq = ncss.get_data(mslp_data)

# Correct variables.
mslpc = mslp_dataq.variables[mslp][:].squeeze()
fnl_mslp = ndimage.gaussian_filter(mslpc, sigma=2, order=0)

# Extract the lon/lat,
lon = mslp_dataq.variables['lon'][:]
lat = mslp_dataq.variables['lat'][:]

#----------
#--------------------
# CREATE THE MAP, PLOT THE DATA, AND CREATE FIGURE
#--------------------
#----------

# Create figure.
fig = plt.figure(figsize=(10, 15))

# Define projection.
lc = ccrs.LambertConformal(central_longitude=-97.5, central_latitude=35, 
                           standard_parallels=(30,60))
ax = fig.add_subplot(1, 1, 1, projection=lc)
ax.set_extent([-109.1, -90.5, 28.1, 43.1], crs=ccrs.PlateCarree())
ax.imshow(parsedvis, extent=(x[0], x[-1], y[-1], y[0]), transform=geos_proj,
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

# Plot MSLP data.
cntr_mslp = np.arange(900, 1060, 4)
cntr_mslp = ax.contour(lon, lat, fnl_mslp, colors='white',zorder=7, linewidths=.5,
                       linestyles='solid', alpha=.6, transform=ccrs.PlateCarree())

# Plot!
plt.savefig('./images/VISIBLE.png', dpi=300, bbox_inches='tight')
