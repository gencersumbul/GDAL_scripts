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

parser = argparse.ArgumentParser(description='GeoTiff Multi Spectral Image to NDVI Image Conversion Script with Normalized Difference Vegetation Index Measurement')
parser.add_argument('-in', '--input_file', help='GeoTiff multi band image file', required=True)
parser.add_argument('-out', '--output_file', help='Where NDVI image is to be saved', required=True)
args = parser.parse_args()

multi_band_file = args.input_file
NDVI_file = args.output_file

multi_band_dataset = gdal.Open(multi_band_file, GA_ReadOnly)
if multi_band_dataset is None:
    print "ERROR:", multi_band_file, "cannot be opened"
else:
    print "INFO: opening", multi_band_file, "is done"
    print "INFO:"
    print multi_band_file, "Driver:", multi_band_dataset.GetDriver().ShortName, "/", multi_band_dataset.GetDriver().LongName
    print multi_band_file, "Size:", multi_band_dataset.RasterXSize, "x", multi_band_dataset.RasterYSize, "x", multi_band_dataset.RasterCount

    red_band = multi_band_dataset.GetRasterBand(5)
    infrared_band = multi_band_dataset.GetRasterBand(7)

    block_sizes = red_band.GetBlockSize()
    x_block_size = block_sizes[0]
    y_block_size = block_sizes[1]

    xsize = red_band.XSize
    ysize = red_band.YSize

    driver = gdal.GetDriverByName('GTiff')
    NDVI_dataset = driver.Create(
        NDVI_file,
        multi_band_dataset.RasterXSize,
        multi_band_dataset.RasterYSize,
        1,
        6,)#float32
    NDVI_dataset.SetGeoTransform(multi_band_dataset.GetGeoTransform())
    NDVI_dataset.SetProjection(multi_band_dataset.GetProjection())

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

    red_band = None
    infrared_band = None
    multi_band_dataset = None
    NDVI_dataset = None
