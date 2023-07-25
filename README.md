##FNMOC COAMPS Data Extraction and Conversion

Aggregate and Convert GRIB files into NetCDF format

* GDAL seemed best suited to work with GRIB files
* Tried using ECCODES, Xarray, and CFGRIB to no avail


## Data are archived and sourced here:
https://usgodae.org/pub/outgoing/fnmoc/models/coamps/calif/cencoos/cencoos_4km/2023/

### Variables are stored in individual GRIB 1 files and time-steps, example:
US058GMET-GR1dyn.COAMPS-CENCOOS_CENCOOS-n3-c1_00000F0NL2023052012_0100_002000-000000wnd_ucmp
US058GMET-GR1dyn.COAMPS-CENCOOS_CENCOOS-n3-c1_00000F0NL2023052012_0100_002000-000000wnd_tru
US058GMET-GR1dyn.COAMPS-CENCOOS_CENCOOS-n3-c1_00000F0NL2023052012_0100_002000-000000wnd_vcmp
US058GMET-GR1dyn.COAMPS-CENCOOS_CENCOOS-n3-c1_00000F0NL2023052012_0100_002000-000000wnd_vtru

### Unique variable names are located in file: 'coamps_variables.txt'
Note: these variables are stored as separate files for each isobaric/atmospheric level

### Latitude/Longitude coordinates are stored in files (found these late in the game!):
US058GMET-GR1dyn.COAMPS-CENCOOS_CENCOOS-n3-c1_00000F0NL2023052012_0001_000000-000000latitude 
US058GMET-GR1dyn.COAMPS-CENCOOS_CENCOOS-n3-c1_00000F0NL2023052012_0001_000000-000000longitude

The surface level (10m) is indicated by the numbers 0105_000100

## Installation

```
conda create -n grib pip
conda activate grib
pip install -r requirements.txt
```
