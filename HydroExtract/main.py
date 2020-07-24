from osgeo import gdal
import numpy as np
import os
import struct


def hydro_extract(base_path, reservoir_tif, dir_tif, acc_tif):
    result_path = base_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    # Reservoir path
    res_data_path = base_path + "/" + reservoir_tif
    # Direction path
    dir_data_path = base_path + "/" + dir_tif

    np.set_printoptions(threshold=np.inf)
    dataset_res = gdal.Open(res_data_path)
    dataset_dir = gdal.Open(dir_data_path)

    res_geotransform = dataset_res.GetGeoTransform()
    dir_geotransform = dataset_dir.GetGeoTransform()
    band = dataset_res.GetRasterBand(1)

    cols = dataset_res.RasterXSize
    rows = dataset_res.RasterYSize
    count = 0

    dir_tl_x = dir_geotransform[0]
    dir_tl_y = dir_geotransform[3]

    fileformat = "GTiff"
    driver = gdal.GetDriverByName(fileformat)
    result_data_path = result_path + "/" + "result.tif"
    dataset_re = driver.Create(result_data_path, dataset_dir.RasterXSize, dataset_dir.RasterYSize)
    dataset_re.SetGeoTransform(dir_geotransform)
    dataset_re.SetProjection(dataset_dir.GetProjection())

    for i in range(rows):
        for j in range(cols):
            count += 1
            px = res_geotransform[0] + j * res_geotransform[1] + i * res_geotransform[2]
            py = res_geotransform[3] + j * res_geotransform[4] + i * res_geotransform[5]
            # print("{} ({}, {})".format(count, px, py))
            scan_data = band.ReadRaster(j, i, 1, 1)
            scan_value = int.from_bytes(scan_data, 'little', signed=True)
            if scan_value == -99:
                dir_xoff = int((px-dir_tl_x)/dir_geotransform[1] + 0.5)
                dir_yoff = int((py-dir_tl_y)/dir_geotransform[5] + 0.5)
                dataset_re.GetRasterBand(1).WriteRaster(dir_xoff, dir_yoff, 1, 1, struct.pack("B", 99))
                print(scan_value)
    # print("First location: {},{}".format(first_x, first_y))

    dataset_res = None
    dataset_dir = None
    dataset_re = None


if __name__ == '__main__':
    hydro_extract("D:/Graduation/Program/Data/1", "tashan_99.tif", "dir.tif", "acc.tif")
