import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as PathEffects
import metpy.calc as mpcalc
from metpy.units import units
from netCDF4 import num2date
import numpy as np
import scipy.ndimage as ndimage
import shapefile
from siphon.catalog import TDSCatalog
import xarray as xr

# Set current time.
now = datetime.utcnow()

# Import latest RAP dataset.
imprt = TDSCatalog('https://thredds-test.unidata.ucar.edu/thredds/catalog/'
                   'grib/NCEP/RAP/CONUS_13km/latest.xml')
dataset = imprt.datasets[0]
ncss = dataset.subset()

# Query the imported datasets wind data.
wind = ncss.query()
wind.variables('u-component_of_wind_isobaric',
               'v-component_of_wind_isobaric')
wind.add_lonlat().vertical_level(500 * 100)
wind.time(now)
wind.lonlat_box(north=50, south=20, east=281, west=233)
wind_data = ncss.get_data(wind)

# Query the imported datasets height data.
hght = ncss.query()
hght.variables('Geopotential_height_isobaric')
hght.add_lonlat().vertical_level(500 * 100)
hght.time(now)
hght.lonlat_box(north=50, south=20, east=281, west=233)
hght_data = ncss.get_data(hght)

# Grab the variables and correct units.
hght_vars = hght_data.variables['Geopotential_height_isobaric'][:].squeeze() * units.meter
uwnd_vars = wind_data.variables['u-component_of_wind_isobaric'][:].squeeze()
vwnd_vars = wind_data.variables['v-component_of_wind_isobaric'][:].squeeze()

fnl_hght = ndimage.gaussian_filter(hght_vars, sigma=2, order=0)
fnl_uwnd = units('m/s') * ndimage.gaussian_filter(uwnd_vars, sigma=2, order=0)
fnl_vwnd = units('m/s') * ndimage.gaussian_filter(vwnd_vars, sigma=2, order=0)

lon = hght_data.variables['lon'][:]
lat = hght_data.variables['lat'][:]

time = hght_data.variables[hght_data.variables['Geopotential_height_isobaric'].dimensions[0]]
vtime = num2date(time[:], time.units)

# Define the projection.
ax = plt.axes(projection=ccrs.LambertConformal(central_latitude=35, central_longitude=-101,
                                               standard_parallels=(30, 60)))

# Create the map figure.
fig = plt.figure(1, figsize=(10,10))
ax.set_extent([-127, -89, 25, 50], ccrs.PlateCarree())

# Create the map features.
ax.add_feature(cfeature.OCEAN.with_scale('50m'),facecolor='#5C697A',
                                                edgecolor='black',
                                                zorder=0,
                                                linewidth=.5)
ax.add_feature(cfeature.LAND.with_scale('50m'),edgecolor='black',
                                               facecolor='#626262',
                                               zorder=1)
ax.add_feature(cfeature.BORDERS.with_scale('50m'),zorder=2,linewidth=.5)
ax.add_feature(cfeature.STATES.with_scale('50m'),linewidth=.5,
                                                 edgecolor='black',
                                                 zorder=3)

# Plot the dataset data.
cs1 = ax.contour(lon, lat, fnl_hght, colors='black',linewidths=1.5,
                zorder=100, transform=ccrs.PlateCarree())
cs2 = ax.contour(lon, lat, fnl_hght, colors='white',linewidths=.5,
                zorder=101, transform=ccrs.PlateCarree())

label1 = ax.clabel(cs1, fontsize=6, colors='white', inline=1, inline_spacing=2,
          fmt='%i', rightside_up=True, use_clabeltext=False)
plt.setp(label1,path_effects=[PathEffects.withStroke(linewidth=1.5,foreground="black")])
label2 = ax.clabel(cs2, fontsize=6, colors='white', inline=1, inline_spacing=2,
          fmt='%i', rightside_up=True, use_clabeltext=False)

for l in label1+label2:
    l.set_rotation(0)

b1 = ax.barbs(lon, lat, fnl_uwnd.to('knots').m, fnl_vwnd.to('knots').m, color='black',
         length=4.5, regrid_shape=15, pivot='middle',linewidth=1.5,
         zorder=103, transform=ccrs.PlateCarree())
b2 = ax.barbs(lon, lat, fnl_uwnd.to('knots').m, fnl_vwnd.to('knots').m, color='white',
         length=4.5, regrid_shape=15, pivot='middle',linewidth=0.5,
         zorder=104, transform=ccrs.PlateCarree())

# Use the cartopy shapefile reader to import FORECAST AREA.
reader = shpreader.Reader('./fa/fa3.shp')
fa = list(reader.geometries())
FA = cfeature.ShapelyFeature(fa, ccrs.PlateCarree())

ax.add_feature(FA,linewidth=1.5,facecolor='none',edgecolor='black',zorder=4)
ax.add_feature(FA,linewidth=.5,facecolor='none',edgecolor='white',zorder=5)

# Add title & discussion information.
plt.title("CURRENT 500MB ANALYSIS",loc='left',fontsize=8,fontweight='bold',
          y=-0.09)
timestamp = datetime.utcnow().strftime('%m/%d/%Y %H:%M')+"Z"
plt.title(timestamp,loc='right',fontsize=8,fontweight='bold',
          y=-0.09)

# Plot!
plt.savefig('500MB.png', dpi=300, bbox_inches='tight')
