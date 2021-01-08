# coding=utf-8
import os
import time
import raster_polygonize as rp
import watershed_extract as we
import get_dir_acc as gda
import river_extract as re


def test(work_path):

    process_path = work_path + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)
    result_path = work_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    print("Get Dir and Acc...")
    dem_tif = work_path + "/preprocess/n35e115_elv.tif"
    dir_tif = process_path + "/dir.tif"
    acc_tif = process_path + "/acc.tif"
    gda.get_dir_acc(process_path, dem_tif, dir_tif, acc_tif)

    print("Get Stream...")
    str_tif = process_path + "/stream.tif"
    str_th = 30000
    re.get_river(process_path, acc_tif, str_th)

    print("Get Watershed...")
    we.get_watershed(process_path, dem_tif, dir_tif, acc_tif, str_tif)


    print("Get Watershed GeoJSON/SHP.")
    watershed_tif = process_path + "/watershed.tif"
    watershed_geoj = process_path + "/watersheds.geojson"
    watershed_shp = process_path + "/watersheds.shp"
    rp.polygonize_to_geojson(watershed_tif, watershed_geoj)
    rp.polygonize_to_shp(watershed_tif, watershed_shp)

    print("test")


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "D:/Graduation/Program/Data/32"
    test(workspace_path)
    end = time.perf_counter()
    print('Run', end - start, 's')
