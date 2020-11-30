import os
import time
import gdal
import common_utils as cu
import direction_reclassify as dr


def test(work_path):

    # process_path = work_path + "/process"
    # if not os.path.exists(process_path):
    #     os.makedirs(process_path)
    # result_path = work_path + "/result"
    # if not os.path.exists(result_path):
    #     os.makedirs(result_path)

    lake_path = work_path + "/lakes.tif"
    lake_ds = gdal.Open(lake_path)
    for i in range(lake_ds.RasterYSize):
        for j in range(lake_ds.RasterXSize):
            int_value = cu.get_raster_int_value(lake_ds, j, i)
            unint_value = cu.get_raster_un_int_value(lake_ds, j, i)
            if int_value != unint_value and int_value != -9:
                print("signed int -> ", int_value)
                print("unsigned int -> ", unint_value)

    print("test")


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "D:/Graduation/Program/Data/21"
    test(workspace_path)
    end = time.perf_counter()
    print('Run', end - start, 's')
