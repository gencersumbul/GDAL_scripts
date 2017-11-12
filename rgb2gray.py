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

parser = argparse.ArgumentParser(description='GeoTiff RGB to Gray Scale Conversion Script with Standard NTSC Conversion Formula')
parser.add_argument('-in', '--input_file', help='GeoTiff RGB image file', required=True)
parser.add_argument('-out', '--output_file', help='Where gray scale image is to be saved', required=True)
args = parser.parse_args()

rgb_file = args.input_file
gray_file = args.output_file

rgb_dataset = gdal.Open(rgb_file, GA_ReadOnly)
if rgb_dataset is None:
    print "ERROR:", rgb_file, "cannot be opened"
elif not rgb_dataset.RasterCount == 3:
    print "ERROR:", rgb_file, "has no 3 bands"
else:
    print "INFO: opening", rgb_file, "is done"
    print "INFO:"
    print rgb_file, "Driver:", rgb_dataset.GetDriver().ShortName, "/", rgb_dataset.GetDriver().LongName
    print rgb_file, "Size:", rgb_dataset.RasterXSize, "x", rgb_dataset.RasterYSize, "x", rgb_dataset.RasterCount

    red_band = rgb_dataset.GetRasterBand(1)
    green_band = rgb_dataset.GetRasterBand(2)
    blue_band = rgb_dataset.GetRasterBand(3)

    block_sizes = red_band.GetBlockSize()
    x_block_size = block_sizes[0]
    y_block_size = block_sizes[1]

    xsize = red_band.XSize
    ysize = red_band.YSize

    driver = gdal.GetDriverByName('GTiff')
    gray_dataset = driver.Create(
        gray_file,
        rgb_dataset.RasterXSize,
        rgb_dataset.RasterYSize,
        1,
        red_band.DataType,)#gdal.GDT_UInt16, )
    gray_dataset.SetGeoTransform(rgb_dataset.GetGeoTransform())
    gray_dataset.SetProjection(rgb_dataset.GetProjection())

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
            red_band_array = red_band.ReadAsArray(x, y, cols, rows)
            green_band_array = green_band.ReadAsArray(x, y, cols, rows)
            blue_band_array = blue_band.ReadAsArray(x, y, cols, rows)
            gray_dataset.GetRasterBand(1).WriteArray((red_band_array*0.2989 + green_band_array*0.5870 + blue_band_array*0.1140).astype(GDAL2NUMPY_DATA_TYPE_CONVERSION[red_band.DataType]), x, y)

            del red_band_array
            del green_band_array
            del blue_band_array

            blocks += 1

    red_band = None
    green_band = None
    blue_band = None
    rgb_dataset = None
    gray_dataset = None
