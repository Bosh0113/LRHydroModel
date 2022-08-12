from operator import le
import os
import numpy
import geopyspark as gps
from pyspark import SparkContext
import test_custom_from_RDD as tcfR
import raster_polygonize as rp
import shutil
# import pfafstetter_coding as pc

conf = gps.geopyspark_conf(master="local[*]", appName="master")
pysc = SparkContext(conf=conf)

if __name__ == '__main__':
    basin_error_record_filename = '/disk1/workspace/20220729/error_basin_record.npy'
    basin_error_record = numpy.load(basin_error_record_filename)
    ws_folder = '/disk1/workspace/20220811/temp'
    for basin_error_idx in range(2, len(basin_error_record)):
    # for basin_error_idx in range(3, 4):
        basins_geoj_filename = basin_error_record[basin_error_idx]
        basins_geoj = basins_geoj_filename.split('/')[len(basins_geoj_filename.split('/')) - 1]
        pfaf_id = basins_geoj.split('.')[0]
        temp_folder = os.path.join(ws_folder, pfaf_id)
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        tcfR.start_main(temp_folder, basins_geoj_filename, 10, 100.)
        slope_surface_tif = temp_folder + '/result/slope.tif'
        lake_tif = temp_folder + '/process/lake_revised.tif'
        slope_surface_geoj = temp_folder + '/' + pfaf_id + '_slope.geojson'
        rp.polygonize_to_geojson(slope_surface_tif, slope_surface_geoj)
        lake_geoj = temp_folder + '/' + pfaf_id + '_lake.geojson'
        rp.polygonize_to_geojson(lake_tif, lake_geoj)


    # basins_geoj_filename = basin_error_record[3]
    # basins_geoj = basins_geoj_filename.split('/')[len(basins_geoj_filename.split('/')) - 1]
    # pfaf_id = basins_geoj.split('.')[0]
    # temp_folder = os.path.join(ws_folder, pfaf_id)
    # if not os.path.exists(temp_folder):
    #     os.makedirs(temp_folder)
    # tcfR.start_main(temp_folder, basins_geoj_filename, 10, 100.)
    # slope_surface_tif = temp_folder + '/result/slope.tif'
    # lake_tif = temp_folder + '/process/lake_revised.tif'
    # slope_surface_geoj = temp_folder + '/' + pfaf_id + '_slope.geojson'
    # rp.polygonize_to_geojson(slope_surface_tif, slope_surface_geoj)
    # lake_geoj = temp_folder + '/' + pfaf_id + '_lake.geojson'
    # rp.polygonize_to_geojson(lake_tif, lake_geoj)
    # shutil.rmtree(temp_folder)


    # pfaf_1 = temp_folder + '/pfaf_1.tif'
    # data_folder = '/home/beichen/workspace/Git/LRHydroModel/HydroExtract/lv_slope_surface/temp'
    # no_sub_basin = pc.get_pfafstetter_code(data_folder + '/dir_p.tif', data_folder + '/acc_p.tif', pfaf_1, 20000000.0)
    # print(no_sub_basin)