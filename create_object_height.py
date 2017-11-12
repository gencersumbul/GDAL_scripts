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

parser = argparse.ArgumentParser(description='Takes bare earth and height image, subtract between them to achive object height')
parser.add_argument('-he', '--height_file', help='Height image file', required=True)
parser.add_argument('-be', '--bear_earth_file', help='Bear Earth image file', required=True)
parser.add_argument('-out', '--output_file', help='Where result image is to be saved', required=True)
args = parser.parse_args()

height_file = args.height_file
bear_earth_file = args.bear_earth_file
output_file = args.output_file

height_dataset = gdal.Open(height_file, GA_ReadOnly)
height_band = height_dataset.GetRasterBand(1)

bear_earth_dataset = gdal.Open(bear_earth_file, GA_ReadOnly)
bear_earth_band = bear_earth_dataset.GetRasterBand(1)


block_sizes = height_band.GetBlockSize()
x_block_size = block_sizes[0]
y_block_size = block_sizes[1]

xsize = height_band.XSize
ysize = height_band.YSize

driver = gdal.GetDriverByName('GTiff')
output_dataset = driver.Create(
    output_file,
    height_dataset.RasterXSize,
    height_dataset.RasterYSize,
    1,
    3,)#int16
output_dataset.SetGeoTransform(height_dataset.GetGeoTransform())
output_dataset.SetProjection(height_dataset.GetProjection())

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

        height_band_array = height_band.ReadAsArray(x, y, cols, rows).astype('int16')
        bear_earth_band_array = bear_earth_band.ReadAsArray(x, y, cols, rows).astype('int16')

        output_dataset.GetRasterBand(1).WriteArray((height_band_array-bear_earth_band_array), x, y)

        del height_band_array
        del bear_earth_band_array

        blocks += 1

height_band = None
bear_earth_band = None
height_dataset = None
bear_earth_dataset = None
