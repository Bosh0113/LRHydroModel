import os
import geopyspark as gps
from pyspark import SparkContext
import clip_tif_saga as cts
import pfafstetter_coding as pc
import custom_from_RDD as cfR
import shutil
import raster_polygonize as rp

# 基础数据
total_dem_tif = '/home/liujz/data/Large_Scale_Watershed/Test/case5.3/nested/dem.tif'
total_dir_o_tif = '/home/liujz/data/Large_Scale_Watershed/Test/case5.3/nested/dir_o.tif'
total_acc_tif = '/home/liujz/data/Large_Scale_Watershed/Test/case5.3/nested/acc.tif'
river_th = 100.0
lakes_area_threshold = 10

if __name__ == '__main__':
    conf = gps.geopyspark_conf(master="local[*]", appName="master")
    pysc = SparkContext(conf=conf)
    workspace = '/home/liujz/data/Large_Scale_Watershed/Test/case5.3/nested/slope_surface/lv7'
    basins_folder = workspace + '/' + 'basins_geoj'
    slope_surface_folder = workspace + '/' + 'slope_surface'
    lake_folder = workspace + '/' + 'lake'

    basins_geojs = os.listdir(basins_folder)
    # 遍历含有湖泊/水库的流域单元
    for basins_geoj in basins_geojs:
        basins_geoj_path = basins_folder + '/' + basins_geoj
        current_path = os.path.abspath(os.path.dirname(__file__))
        temp_folder = current_path + '/temp'
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        # 获取范围内的数据
        dem_tif = temp_folder + '/dem_p.tif'
        dir_tif = temp_folder + '/dir_p.tif'
        acc_tif = temp_folder + '/acc_p.tif'
        cts.geojson_clip_tif(basins_geoj_path, total_dem_tif, dem_tif)
        cts.geojson_clip_tif(basins_geoj_path, total_dir_o_tif, dir_tif)
        cts.geojson_clip_tif(basins_geoj_path, total_acc_tif, acc_tif)
        # 进行pfafstetter编码次分处理
        pfaf_1 = temp_folder + '/pfaf_1.tif'
        no_sub_basin = pc.get_pfafstetter_code(dir_tif, acc_tif, pfaf_1, river_th)
        # 若没有次级划分
        if no_sub_basin:
            river_th = 100.0
        else:
            river_th = 2000000.0
        cfR.start_main(temp_folder, basins_geoj_path, lakes_area_threshold, river_th)
        slope_surface_tif = temp_folder + '/result/slope.tif'
        lake_tif = temp_folder + '/result/lake_revised.tif'
        pfaf_id = basins_geoj.split('.')[0]
        slope_surface_geoj = slope_surface_folder + '/' + pfaf_id + '.geojson'
        rp.polygonize_to_geojson(slope_surface_tif, slope_surface_geoj)
        lake_geoj = lake_folder + '/' + pfaf_id + '.geojson'
        rp.polygonize_to_geojson(lake_tif, lake_geoj)
        # 删除临时文件夹
        shutil.rmtree(temp_folder)