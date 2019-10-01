import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as PathEffects
import numpy as np
import shapefile

# Define the projection.
ax = plt.axes(projection=ccrs.LambertConformal(central_latitude=35, central_longitude=-98,
                                               standard_parallels=(30, 60)))

# Create the map figure.
fig = plt.figure(1, figsize=(10,10))
ax.set_extent([-104.1, -95.5, 32.1, 39.1], ccrs.PlateCarree())

# Create the map features.
ax.add_feature(cfeature.OCEAN.with_scale('50m'),facecolor='grey',edgecolor='none',zorder=5)
ax.add_feature(cfeature.LAND.with_scale('50m'),edgecolor='black',
                                               facecolor='grey',
                                               zorder=1)
ax.add_feature(cfeature.BORDERS.with_scale('50m'),zorder=2)
ax.add_feature(cfeature.LAKES.with_scale('50m'),linewidth=.5,
                                                facecolor='grey',
                                                edgecolor='black',
                                                zorder=3)
ax.add_feature(cfeature.STATES.with_scale('50m'),linewidth=.5,
                                                 edgecolor='black',
                                                 zorder=6)

# Use the cartopy shapefile reader to import custom county map.
reader = shpreader.Reader('/home/victoraalvarez/Documents/pythonScripts'
                          '/pythonPlayground/mapFiles/county_map/countyl010g.shp')
counties = list(reader.geometries())
COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())

ax.add_feature(COUNTIES,linewidth=.5,facecolor='none',edgecolor='black',zorder=4,
                        alpha=.2)

# Use the cartopy shapefile reader to import FORECAST AREA.
reader = shpreader.Reader('/home/victoraalvarez/Documents/pythonScripts/'
                          'pythonPlayground/mapFiles/fa/fa3.shp')
fa = list(reader.geometries())
FA = cfeature.ShapelyFeature(fa, ccrs.PlateCarree())

ax.add_feature(FA,linewidth=2.5,facecolor='none',edgecolor='black',zorder=7,
                  capstyle='round')
ax.add_feature(FA,linewidth=.5,facecolor='none',edgecolor='white',zorder=8)

# Remove border from plot.
ax.background_patch.set_facecolor('none')
ax.outline_patch.set_edgecolor('none')

# Use the shapefile readers to import low forecast confidence outline.
try:
    lc_sf = shapefile.Reader('./files/conf/lowConfidence.shp')
    lc_sf_shp = lc_sf.shapes()
    lc_nm = len(lc_sf_shp)-1
    lon_lat_lc = lc_sf_shp[lc_nm].points[5]
    lclon, lclat = lon_lat_lc

    low_txt = plt.text(lclon-0.1,lclat-0.1,'LOW',size=7,fontweight='bold',
                            transform=ccrs.PlateCarree(),zorder=49,color='deepskyblue')
    low_txt.set_path_effects([PathEffects.withStroke(linewidth=3, foreground='black')])

    reader = shpreader.Reader('./files/conf/lowConfidence.shp')
    lowConfidence = list(reader.geometries())
    lco = cfeature.ShapelyFeature(lowConfidence, ccrs.PlateCarree())

    ax.add_feature(lco,linewidth=3,facecolor='none',edgecolor='black',zorder=8)
    ax.add_feature(lco,linewidth=1,facecolor='none',edgecolor='deepskyblue'
                         ,zorder=9)
except:
     pass

# Use the shapefile readers to import medium forecast confidence outline.
try:
    md_sf = shapefile.Reader('./files/conf/medConfidence.shp')
    md_sf_shp = md_sf.shapes()
    md_nm = len(md_sf_shp)-1
    lon_lat_md = md_sf_shp[md_nm].points[5]
    mdlon, mdlat = lon_lat_md

    med_txt = plt.text(mdlon-0.1,mdlat-0.1,'MED',size=7,fontweight='bold',
                            transform=ccrs.PlateCarree(),zorder=49,color='gold')
    med_txt.set_path_effects([PathEffects.withStroke(linewidth=3, foreground='black')])

    reader = shpreader.Reader('./files/conf//medConfidence.shp')
    medConfidence = list(reader.geometries())
    mco = cfeature.ShapelyFeature(medConfidence, ccrs.PlateCarree())

    ax.add_feature(mco,linewidth=3,facecolor='none',edgecolor='black',zorder=8)
    ax.add_feature(mco,linewidth=1,facecolor='none',edgecolor='gold'
                     ,zorder=9)
except:
    pass

# Use the cartopy shapefile reader to import high forecast confidence outline.
try:
    hi_sf = shapefile.Reader('./files/conf/hiConfidence.shp')
    hi_sf_shp = hi_sf.shapes()
    hi_nm = len(hi_sf_shp)-1
    lon_lat_hi = hi_sf_shp[hi_nm].points[7]
    hilon, hilat = lon_lat_hi

    hi_txt = plt.text(hilon-0.1,hilat-0.1,'HIGH',size=7,fontweight='bold',
                            transform=ccrs.PlateCarree(),zorder=49,color='crimson')
    hi_txt.set_path_effects([PathEffects.withStroke(linewidth=3, foreground='black')])

    reader = shpreader.Reader('./files/conf/hiConfidence.shp')
    hiConfidence = list(reader.geometries())
    hco = cfeature.ShapelyFeature(hiConfidence, ccrs.PlateCarree())

    ax.add_feature(hco,linewidth=3,facecolor='none',edgecolor='black',zorder=8)
    ax.add_feature(hco,linewidth=1,facecolor='none',edgecolor='crimson'
                     ,zorder=9)
except:
    pass

# Use the cartopy shapefile reader to import highlighted feature hash.
try:
    hf_sf = shapefile.Reader('./files/conf/highlightedArea.shp')
    hf_sf_shp = hf_sf.shapes()
    hf_nm = len(hf_sf_shp)-1
    lon_lat_hf = hf_sf_shp[hf_nm].points[4]
    hflon, hflat = lon_lat_hf

    reader = shpreader.Reader('./files/conf/highlightedArea.shp')
    hfHash = list(reader.geometries())
    hfo = cfeature.ShapelyFeature(hfHash, ccrs.PlateCarree())

    ax.add_feature(hfo,linewidth=0,facecolor='none',edgecolor='seashell',
                      zorder=7,hatch='//////')
except:
    pass

# Add title & discussion information.
plt.title("DAY 1 FORECAST CONFIDENCE",loc='left',fontsize=8,fontweight='bold',
          y=-0.09)
timestamp = datetime.utcnow().strftime('%m/%d/%Y %H:%M')+"Z"
plt.title(timestamp,loc='right',fontsize=8,fontweight='bold',
          y=-0.09)

# Plot!
plt.savefig('./images/DAY1_FORECAST.png', dpi=300, bbox_inches='tight')
