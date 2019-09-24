import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import metpy.calc as mpcalc
from metpy.units import units
from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
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
wind.lonlat_box(north=55, south=20, east=281, west=230)
wind_data = ncss.get_data(wind)

# Query the imported datasets height data.
hght = ncss.query()
hght.variables('Geopotential_height_isobaric')
hght.add_lonlat().vertical_level(500 * 100)
hght.time(now)
hght.lonlat_box(north=55, south=20, east=281, west=230)
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
ntime = vtime[0]
datatime = ntime.strftime("%H:%M" + "Z")

# Use MetPy to parse the wind data.
wndspeed = mpcalc.wind_speed(fnl_uwnd, fnl_vwnd).to('kt')

# Define the projection.
ax = plt.axes(projection=ccrs.LambertConformal(central_latitude=35, central_longitude=-101,
                                               standard_parallels=(30, 60)))

# Create the map figure.
fig = plt.figure(1, figsize=(10,10))
ax.set_extent([-125, -89, 25, 50], ccrs.PlateCarree())

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

# Remove border from plot.
ax.background_patch.set_facecolor('none')
ax.outline_patch.set_edgecolor('none')

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


step_wndspeed = np.arange(30, 160, 10)
cstep_wndspeed = np.arange(30, 160, 10)
fill_wndspeed = ax.contourf(lon, lat, wndspeed, step_wndspeed, cmap='PuBu',
                            vmin=-5,vmax=150,zorder=3,transform=ccrs.PlateCarree())
contr_wndspeed = ax.contour(lon, lat, wndspeed, cstep_wndspeed, linewidths=.5,
                            colors='black', zorder=3, transform=ccrs.PlateCarree())
cwndspeedlbl = ax.clabel(contr_wndspeed, fontsize=5, colors='black', inline=1, inline_spacing=1,
          fmt='%i')

for l in cwndspeedlbl:
    l.set_rotation(0)

# Use the cartopy shapefile reader to import FORECAST AREA.
reader = shpreader.Reader('/home/victoraalvarez/Documents/pythonScripts/'
                          'pythonPlayground/mapFiles/fa/fa3.shp')
fa = list(reader.geometries())
FA = cfeature.ShapelyFeature(fa, ccrs.PlateCarree())

ax.add_feature(FA,linewidth=1.5,facecolor='none',edgecolor='black',zorder=6,
                  capstyle='round')
ax.add_feature(FA,linewidth=.5,facecolor='none',edgecolor='white',zorder=7)

# Add title & colorbar.
df = '%m/%d/%Y %H:%M'

plt.title("500MB WINDS",loc='left',fontsize=8,fontweight='bold',
          y=-0.09)
timestamp = datetime.utcnow().strftime(df)+"Z"
plt.title(timestamp,loc='right',fontsize=8,fontweight='bold',
          y=-0.09)
plt.suptitle("DATA VALID: " + datatime,fontsize=6,ha='right',fontweight='bold',
          x=0.764,y=0.094)

cbar = fig.colorbar(fill_wndspeed, shrink=.896, anchor=0.1, pad=0.025)
cbar.ax.tick_params(labelsize=7)
cbar.outline.set_visible(False)
cbar.ax.tick_params(length=0)

# Plot!
plt.savefig('./images/500MB_WIND.png', dpi=300, bbox_inches='tight')
