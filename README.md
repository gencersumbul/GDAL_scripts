# GDAL_scripts
Python scripts benefiting GDAL (Geospatial Data Abstraction Library) python library for general needs in remote sensing research

Below, you can find my post from my personal website about GDAL: 

GDAL (Geospatial Data Abstraction Library) is a very powerful tool for researchers interested in remote sensing while editing rasters and vectors with many geospatial data formats like GeoTIFF. You can easily use GDAL utilities in C, C++ or Python. In this post, I explained one of my GDAL python scripts. I usually try to generate such scripts when I need at first to reuse later. For others, you can look at [the GitHub repository](https://github.com/gencersumbul/GDAL_scripts). I hope this post will also give you some initial ideas about how to use GDAL python library. 

NDVI (Normalized Difference Vegetation Index) is very informative indicator in order to decide whether an area in a remote sensing image contain green vegetation or not. It can eaily be calculated as difference of near-infared and red bands values divided by their sum. Thus, if you have a multi spectral image -containing both near-infared and red bands- you can benefitted this information. For instance, it is generally used in 8-band WorldView-2 imagery. 

Lets's start to explain the python script:

```python
from gdalconst import *
import argparse, numpy as np,  gdal, struct, sys

GDAL2NUMPY_DATA_TYPE_CONVERSION = {
  1: "uint8",
  2: "uint16",
  3: "int16",
  4: "uint32",
  5: "int32",
  6: "float32",
  7: "float64",
  10: "complex64",
  11: "complex128",
}
```
After importing libraries, the dictionary gives the data type conversion scheme between GDAL and numpy. It is very useful for data-type conversion issues.

Let's get the multi-band raster and output file names from the user:

```python
parser = argparse.ArgumentParser(description='GeoTiff Multi Spectral Image to NDVI Image Conversion Script with Normalized Difference Vegetation Index Measurement')
parser.add_argument('-in', '--input_file', help='GeoTiff multi band image file', required=True)
parser.add_argument('-out', '--output_file', help='Where NDVI image is to be saved', required=True)
args = parser.parse_args()

multi_band_file = args.input_file
NDVI_file = args.output_file
``` 
Later then, we can open the raster with GDAL and create a new raster for output:

```python
#Open multi-band file
multi_band_dataset = gdal.Open(multi_band_file, GA_ReadOnly)
print multi_band_file, "Driver:", multi_band_dataset.GetDriver().ShortName, "/", multi_band_dataset.GetDriver().LongName
print multi_band_file, "Size:", multi_band_dataset.RasterXSize, "x", multi_band_dataset.RasterYSize, "x", multi_band_dataset.RasterCount

#Take the red and near-infrared bands
red_band = multi_band_dataset.GetRasterBand(5)
infrared_band = multi_band_dataset.GetRasterBand(7)

xsize = red_band.XSize
ysize = red_band.YSize

#Create NVDI output raster with specific raster format 
driver = gdal.GetDriverByName('GTiff')

NDVI_dataset = driver.Create(
    NDVI_file,
    multi_band_dataset.RasterXSize,
    multi_band_dataset.RasterYSize,
    1,
    6,)#float32
NDVI_dataset.SetGeoTransform(multi_band_dataset.GetGeoTransform())
NDVI_dataset.SetProjection(multi_band_dataset.GetProjection())
```
Note that we should know which bands correspond to red and near-infrared bands. In WorldView-2 imagery, for instance, 5th band is red and 7th band is near-infrared. After than, when we create a new output raster, we must select the data format named as driver in GDAL. In this script, GeoTIFF is used as output format. Additionally, for the raster creation, last two arguments of create method represent number of bands and data type. Since only one band is enough for NDVI values, number of bands is selected as 1. For the data type, 6 is selected for the data type float32 since we can decide this value by looking at the data type converison scheme. After then, we must also set geotransform and projection which are the same as multi-band raster.      

Finally, we can populate output raster with NDVI values:

```python
block_sizes = red_band.GetBlockSize()
x_block_size = block_sizes[0]
y_block_size = block_sizes[1]

blocks = 0

for y in xrange(0, ysize, y_block_size):
    if y + y_block_size < ysize:
        rows = y_block_size
    else:
        rows = ysize - y
    for x in xrange(0, xsize, x_block_size):
        if x + x_block_size < xsize:
            cols = x_block_size
        else:
            cols = xsize - x
        red_band_array = red_band.ReadAsArray(x, y, cols, rows).astype('float32')
        infrared_band_array = infrared_band.ReadAsArray(x, y, cols, rows).astype('float32')

        mask_array = np.not_equal((red_band_array + infrared_band_array), 0)
        ndvi_array = np.choose(mask_array, (0.0, (infrared_band_array - red_band_array) / (infrared_band_array + red_band_array)))
        NDVI_dataset.GetRasterBand(1).WriteArray(ndvi_array.astype('float32'), x, y)

        del red_band_array
        del infrared_band_array
        del mask_array
        del ndvi_array

        blocks += 1
```
Note that this is not the only way for populating raster. However, using data blocks, rather than reading all values or reading frames having different values than block sizes, can be the most memory-friendly and quick way. 

For the NDVI calculation, mask array is used for the values which is undefined due to division by zero. 

At the end, if your code continues, you should equalize dataset and bands to None because of memory usage.

```python
red_band = None
infrared_band = None
multi_band_dataset = None
NDVI_dataset = None
```

I hope this post is able to give ideas about the usage of GDAL in Python. For the all parts of the code: [create_NDVI.py](https://github.com/gencersumbul/GDAL_scripts/blob/master/create_NDVI.py)
