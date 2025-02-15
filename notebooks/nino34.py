import xarray as xr
import numpy as np
import numpy.ma as ma
import matplotlib as plt
import matplotlib.pyplot as plt
import os
import cftime
import nc_time_axis
import numpy.matlib
from season_util import season_mean
from wgt_areaave import wgt_areaave as wa

def nino34(ds,var,seas):
    
    """
    calculates Nino 3.4 from monthly mean gridded data
    Args: ds (xarray.Dataset): dataset (needs to be 3-d, e.g. [time x lat x lon])
          var (str): variable to use
          seas (str): season to calculate Nino 3.4 for
                      (options: 'monthly'-->no seasonal average, returns
                      monthly mean anomalies; 'DJF'; 'MAM'; JJA'; 'SON')
    Comment: currently, the time coordinates for the 'monthly' case and 'DJF', 'MAM', etc cases
            are not the same when they come out at the end, need to revisit
    Import: from nino34 import nino34
    Usage example: nino = nino34(da,'ts','DJF')
    """
    
    minlat = -5
    maxlat = 5
    minlon = -170+360
    maxlon = -120+360
    
    # -- spatial average in nino34 region
    nino_raw = wa(ds,'ts',minlat,maxlat,minlon,maxlon)

    # -- compute anomalies (I think this can be made much more efficient/elegant)
    if seas == 'monthly':
        climo = xr.DataArray(np.random.rand(12, 1))
        for m in range(0,12):
             climo[m] = np.mean(nino_raw[m::12])
        climo_ds = numpy.matlib.repmat(climo,50,1)
        nino = nino_raw-np.squeeze(climo_ds)
    else:
        nino = nino_raw.where(nino_raw['time.season'] == seas)
        nino = nino.rolling(min_periods=3, center=True, time=3).mean()
        nino = nino.groupby('time.year').mean('time')
        nino = nino-np.mean(nino)

    # -- standardize
    nino = nino/np.std(nino)
        
    return (nino)