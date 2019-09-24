import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
from datetime import datetime
import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import matplotlib.ticker as mticker
import metpy.calc as mpcalc
from metpy.units import units
from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
from netCDF4 import num2date
import numpy as np
import scipy.ndimage as ndimage
import shapefile
from siphon.catalog import TDSCatalog
import xarray as xr

#----------
#--------------------
# SET VARIABLES
#--------------------
#----------

now = datetime.utcnow()
surface_temperature = 'Temperature_height_above_ground'

#----------
#--------------------
# GRABBING HRRR SURFACE TEMPERATURE DATA
#--------------------
#----------

# Grab the latest HRRR dataset.
cat = TDSCatalog('https://thredds-test.unidata.ucar.edu/thredds/catalog/'
                 'grib/NCEP/HRRR/CONUS_2p5km/latest.xml')
dataset = cat.datasets[0]
ncss = dataset.subset()

# Query the surface temperature data.
sfctemp = ncss.query()
sfctemp.variables(surface_temperature)
sfctemp.vertical_level(2.0)
sfctemp.add_lonlat().lonlat_box(north=44, south=27, east=271, west=250)
sfctemp.time(now)
sfctemp_data = ncss.get_data(sfctemp)

# Grab and correct variables.
sfctemp_vars = units.K * sfctemp_data.variables[surface_temperature][:].squeeze()
sfctemp_vars = sfctemp_vars.to('degF')
fnl_sfctemp = ndimage.gaussian_filter(sfctemp_vars, sigma=2, order=0)

# Extract lon/lat.
lon = sfctemp_data.variables['lon'][:]
lat = sfctemp_data.variables['lat'][:]

# Grab time from data.
time = sfctemp_data.variables[sfctemp_data.variables[surface_temperature].dimensions[0]]
vtime = num2date(time[:], time.units)
ntime = vtime[0]
datatime = ntime.strftime("%H:%M" + "Z")

#----------
#--------------------
# CREATE THE MAP, PLOT THE DATA, AND CREATE FIGURE
#--------------------
#----------

# Define projection.
ax = plt.axes(projection=ccrs.LambertConformal(central_latitude=35, central_longitude=-98,
                                               standard_parallels=(30, 60)))

# Define projecton and figure properties.
fig = plt.figure(1, figsize=(10,10))
ax.set_extent([-109.1, -90.5, 28.1, 43.1], ccrs.PlateCarree())

# Create the map features.
ax.add_feature(cfeature.OCEAN.with_scale('50m'),facecolor='#F2F2F2',
                                                edgecolor='black',
                                                zorder=0,
                                                linewidth=.5)
ax.add_feature(cfeature.LAND.with_scale('50m'),edgecolor='black',
                                               facecolor='#E1E1E1',
                                               zorder=1)
ax.add_feature(cfeature.BORDERS.with_scale('50m'),zorder=4,linewidth=.5,edgecolor='black')
ax.add_feature(cfeature.COASTLINE.with_scale('50m'),zorder=4,linewidth=.5,edgecolor='black')
ax.add_feature(cfeature.LAKES.with_scale('50m'),zorder=2,linewidth=.5,edgecolor='black',
                                                facecolor='#F2F2F2')
ax.add_feature(cfeature.STATES.with_scale('50m'),linewidth=.5,
                                                 edgecolor='black',
                                                 zorder=5)

# Use the cartopy shapefile reader to import custom county map.
reader = shpreader.Reader('/home/victoraalvarez/Documents/pythonScripts'
                          '/pythonPlayground/mapFiles/county_map/countyl010g.shp')
counties = list(reader.geometries())
COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())

ax.add_feature(COUNTIES,linewidth=.5,facecolor='none',edgecolor='black',zorder=4
                       ,alpha=.3)

# Use the cartopy shapefile reader to import FORECAST AREA.
reader = shpreader.Reader('/home/victoraalvarez/Documents/pythonScripts/'
                          'pythonPlayground/mapFiles/fa/fa3.shp')
fa = list(reader.geometries())
FA = cfeature.ShapelyFeature(fa, ccrs.PlateCarree())

ax.add_feature(FA,linewidth=2,facecolor='none',edgecolor='black',zorder=7,
                  capstyle='round')
ax.add_feature(FA,linewidth=.5,facecolor='none',edgecolor='white',zorder=8)

# Remove border from plot.
ax.background_patch.set_facecolor('none')
ax.outline_patch.set_edgecolor('none')

# Plot the dataset.
step_sfctemp = np.arange(-10, 120, 2)
cntr_sfctemp = np.arange(-10, 120, 10)
cntr2_sfctemp = np.arange(-10, 120, 2)

fill_sfctemp = ax.contourf(lon, lat, fnl_sfctemp, step_sfctemp,cmap='twilight_shifted',
                           vmin=-20,vmax=120,zorder=3,transform=ccrs.PlateCarree())
cntr_sfctemp = ax.contour(lon, lat, fnl_sfctemp, cntr_sfctemp,colors='black',zorder=3,
                          linewidths=.5,linestyles='solid',
                          alpha=.6,transform=ccrs.PlateCarree())
cntr2_sfctemp = ax.contour(lon, lat, fnl_sfctemp, cntr2_sfctemp,colors='black',zorder=3,
                          linewidths=.2,linestyles='solid',
                          alpha=.2,transform=ccrs.PlateCarree())

sfctemp_lbl = ax.clabel(cntr_sfctemp, fontsize=5, colors='black', inline=1, inline_spacing=1,
                                      fmt='%i')

for l in sfctemp_lbl:
    l.set_rotation(0)

# Add title & colorbar.
df = '%m/%d/%Y %H:%M'

plt.title("HRRR SURFACE TEMPS",loc='left',fontsize=8,fontweight='bold',
          y=-0.09)
timestamp = datetime.utcnow().strftime(df)+"Z"
plt.title(timestamp,loc='right',fontsize=8,fontweight='bold',
          y=-0.09)
plt.suptitle("DATA VALID: " + datatime,fontsize=6,ha='right',fontweight='bold',
          x=0.764,y=0.094)

cbar = fig.colorbar(fill_sfctemp, shrink=.896, anchor=0.1, pad=0.025)
cbar.ax.tick_params(labelsize=7)
cbar.outline.set_visible(False)
cbar.ax.tick_params(length=0)

# Plot!
plt.savefig('./images/HRRRSFCTEMP.png', dpi=300, bbox_inches='tight')
