from osgeo import gdal
from osgeo import osr
import xarray as xr
import numpy as np
from datetime import datetime, timedelta
import requests
import re
from bs4 import BeautifulSoup
import json
# exec(open("convert_coamps_grib2nc.py").read())

##- Suppress warning from GDAL
gdal.PushErrorHandler('CPLQuietErrorHandler')

##- Create a list of terms to search directories
#keys = ["wnd_ucmp","wnd_vcmp","wnd_vtru","wnd_utru","geop_ht"]
keys = ["wnd_ucmp","wnd_vcmp","wnd_vtru","wnd_utru"]

##- For subsetting purposes, declare lat/lon lims
lat_lims = [36, 39];
lon_lims = [-125, -121];

##- Declare file type
ftype = 'US058GMET-GR1dyn.COAMPS-CENCOOS_CENCOOS-n3-c1_'

##- Figure out how many time-steps there will be
sdate = "20230520"
sdt = datetime.strptime(sdate,'%Y%m%d')
edate = "2023071923"
edt = datetime.strptime(edate,'%Y%m%d%H')
NT = ((edt-sdt).days  + 1)* 24

##- Get metadata file, Note: manually created using Panopoly to read variable attributes
met_fname = './input/metadata.json'
f = open(met_fname)
meta = json.load(f)

##- Open up url and get a list of available directories in YYYYMMDDHH format
url = 'https://usgodae.org/pub/outgoing/fnmoc/models/coamps/calif/cencoos/cencoos_4km/2023/'
page = requests.get(url)

def search_list(key,values):
    result = [x for x in values if key in x]
    return result

def gdal_array(fname,band=1,dtype='float32'):
    ds = gdal.Open(fname,gdal.GA_ReadOnly)
    arr = ds.GetRasterBand(band).ReadAsArray().astype(dtype)
    return arr

##- function to use variable key name and return a list of files to process
def get_relevant_fnames(key, refdate, file_list):
    fnames = [] 
    result = search_list(key,file_list)
    ref_dt = datetime.strptime(refdate,'%Y%m%d%H')
    for f in result:
        ##- Compute datetime of time-step 
        step = f[len(ftype):len(ftype)+3]		#-- 0
        file_dt = ref_dt + timedelta(hours=int(step))
        new_fname = f.replace('2023052000',refdate)
        ##- Check to see if this is surface (10m) level 
        lvl = f.split('_')[3]
        if( (lvl == '0105') and (int(step) <= 11) ):
            fnames.append(new_fname)
    return fnames

##- Get lat/lon coordinates from static file
lat_fname = './input/US058GMET-GR1dyn.COAMPS-CENCOOS_CENCOOS-n3-c1_latitude'
lon_fname = './input/US058GMET-GR1dyn.COAMPS-CENCOOS_CENCOOS-n3-c1_longitude'
yi = gdal_array(lat_fname,1,'float32')
xi = gdal_array(lon_fname,1,'float32')
if (xi[0][0] > 0):
    xi = (xi + 180) % 360 - 180
lats = np.unique(yi)
lons = np.unique(xi)
NY,NX = yi.shape


##- Get source projection information: looks like Mercator (2SP) EPSG: 9805
##- Note: Don't neead to do this because there are lat/lon coordinates in files
#src_prj = ds.GetProjection()

##- Get a list of directories to process (YYYYMMDDHH)
dir_list = []
html_text = page.text
soup = BeautifulSoup(page.content, 'html.parser')
tag_list = soup.find_all("a" )
for i in range(5,len(tag_list)):
    info = tag_list[i]
    YYYYMMDDHH = info.text.replace('/','')
    dt = datetime.strptime(YYYYMMDDHH,'%Y%m%d%H')
    if ((dt >= sdt) and (dt <= edt)):
        dir_list.append(YYYYMMDDHH)

##- Now get a sample file list in one directory that we can duplicate
file_list = []
YYYYMMDDHH = sdate+'00'
src_url = url+YYYYMMDDHH+"/"
page = requests.get(src_url)
html_text = page.text
soup = BeautifulSoup(page.content, 'html.parser')
tag_list = soup.find_all("a" )
for j in range(5,len(tag_list)):
    info = tag_list[j]
    fname = info.text
    file_list.append(fname)


##- Iterate over variables and then each remote YYYYMMDDHH directory and grab relevant data
##- Fill up a 3-D array called D, which has (NT,NY,NX) dimensions
array_dict = {}
for key in keys:
    idx = 0
    times = []
    D = np.zeros((NT,NY,NX),'float32')
    for i in range(len(dir_list)):
        YYYYMMDDHH = dir_list[i]
        fnames = get_relevant_fnames(key, YYYYMMDDHH, file_list)
        dt = datetime.strptime(YYYYMMDDHH,'%Y%m%d%H')
        src_url = url+YYYYMMDDHH+"/"
        for f in fnames: 
            step = f[len(ftype):len(ftype)+3]		#-- 0
            file_dt = dt + timedelta(hours=int(step))
            times.append(file_dt)
            ##- prepend w/ vsicurl for external files
            data = gdal_array('/vsicurl/'+src_url+f,1,'float32')
            D[idx,:,:] = data
            idx = idx + 1

    ##- Create individual xarray DataArray for each variable/parameter 
    da = xr.DataArray(
      data = D,
      dims=["time","latitude","longitude"],
      coords= {'time':times, 'latitude':lats, 'longitude':lons},
      attrs=meta[key]
    )        
    da.rename(key)
    array_dict[key] = da
    da.to_netcdf('./output/'+key+'.nc')


print("Creating DataSet")
##- Setup input for DataArray
out_fname = './output/'+ftype+sdate+'-'+edate[:-2]+".nc"
global_attrs = {'Originating_Center':"Fleet Numerical Meteorology and Oceanography Center, Monterey, CA, United States",
                'Data_Source':'https://usgodae.org',
                'Description':'Coupled Ocean/Atmosphere Mesoscale Prediction System (COAMPS®) are used operationally by the U.S. Navy for short-term numerical weather prediction for various regions around the world.' }
out_dset = xr.Dataset(array_dict,global_attrs)
out_dset.to_netcdf(out_fname)

##- Subset to ROI
out_fname = './output/coamps_cencoos_subset.nc'
sm_dset = out_dset.sel(latitude=slice(lat_lims[0],lat_lims[1]), longitude=slice(lon_lims[0],lon_lims[1]))
sm_dset.to_netcdf(out_fname)

