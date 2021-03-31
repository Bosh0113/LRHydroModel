# coding=utf-8
import direction_reclassify as dc
import get_dir_acc as gda
import river_extract as re
import watershed_extract as we
import water_revise as wr
import slope_surface_extract as sse
import common_utils as cu
import record_rivers as rr
import clip_tif as ct
import data_search as ds
import os
import time
import shutil
import gdal


# 示例：工作空间路径 GeoJson范围数据路径 河流提取阈值
def demo6(workspace_path, catalog_path, geojson_path, river_threshold):

    start = time.perf_counter()

    # 工作空间路径
    data_path = workspace_path + "/data"
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    # 查询计算区域的数据
    print("----------------------------------Search Raster Data----------------------------------")
    stage_time = time.perf_counter()
    # DEM数据路径
    dem_tif_path = data_path + "/dem.tif"
    # 流向数据路径
    dir_tif_path = data_path + "/dir.tif"
    # 汇流累积量数据路径
    acc_tif_path = data_path + "/acc.tif"
    # 湖泊/水库数据路径
    water_tif_path = data_path + "/lakes.tif"
    print("Output Data.")
    ds.data_search(catalog_path, geojson_path, dem_tif_path, dir_tif_path, acc_tif_path, water_tif_path)

    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 工作空间路径
    process_path = workspace_path + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)


    # 裁剪研究区域的数据
    print("----------------------------------Crop Raster Data----------------------------------")
    stage_time = time.perf_counter()
    dem_clip = process_path + "/dem_clip.tif"
    dir_clip = process_path + "/dir_clip.tif"
    acc_clip = process_path + "/acc_clip.tif"
    lakes_clip = process_path + "/lakes_clip.tif"
    ct.geojson_clip_tif(geojson_path, dem_tif_path, dem_clip)
    ct.geojson_clip_tif(geojson_path, dir_tif_path, dir_clip)
    ct.geojson_clip_tif(geojson_path, acc_tif_path, acc_clip)
    ct.geojson_clip_tif(geojson_path, water_tif_path, lakes_clip)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 重新计算流向数据和汇流累积量
    print("--------------------------------TauDEM Direction and Accumulation--------------------------------")
    stage_time = time.perf_counter()
    dir_tau_tif = process_path + "/dir_tau.tif"
    acc_tau_tif = process_path + "/acc_tau.tif"
    gda.get_dir_acc(process_path, dem_clip, dir_tau_tif, acc_tau_tif)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 提取河系
    print("-------------------------------------Get Rivers-------------------------------------")
    stage_time = time.perf_counter()
    re.get_river(process_path, acc_tau_tif, river_threshold)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 记录河系信息
    print("------------------------------------Record Rivers------------------------------------")
    stage_time = time.perf_counter()
    river_tif_path = process_path + "/stream.tif"
    rr.record_rivers(process_path, river_tif_path, acc_tau_tif)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 修正湖泊/水库边界
    print("----------------------------------Get Revised Water----------------------------------")
    stage_time = time.perf_counter()
    water_revised_path = process_path + "/lake_revised.tif"
    cu.copy_tif_data(lakes_clip, water_revised_path)
    wr.water_revise(water_revised_path, river_tif_path, process_path + "/river_record.txt", dir_tau_tif)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 提取坡面和湖泊/水库
    print("----------------------------------Get Slope Surface----------------------------------")
    stage_time = time.perf_counter()
    sse.get_slope_surface(process_path, water_revised_path, dir_tau_tif, acc_tau_tif, river_threshold, -9)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 提取子流域
    print("------------------------------------Get Watershed-----------------------------------")
    stage_time = time.perf_counter()
    water_s_s_tif_path = process_path + "/water_slope.tif"
    we.watershed_extract(process_path, dem_clip, dir_tau_tif, acc_tau_tif, river_tif_path, water_s_s_tif_path)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')


    # 结果文件夹
    print("-----------------------------------Copy Result Data----------------------------------")
    result_path = workspace_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    # 复制修正后的湖泊/水库、坡面流路、子流域以及河网矢量结果数据到文件夹
    print("-> Copy Water/Slope surface route/Stream...")
    stage_time = time.perf_counter()
    file_list = os.listdir(process_path)
    result_files = ["water_revised", "slope_surface_route", "watershed", "stream_shp"]
    for file in file_list:
        file_info = file.split(".")
        if file_info[0] in result_files:
            shutil.copy(process_path + "/" + file, result_path + "/" + file)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 复制河网栅格结果数据和重分类
    print("-> Copy/Reclassify Stream...")
    stage_time = time.perf_counter()
    river_ds = gdal.Open(river_tif_path)
    no_data_value = river_ds.GetRasterBand(1).GetNoDataValue()
    cu.tif_reclassify(river_tif_path, result_path + "/stream.tif", [[0]], [int(no_data_value)])
    river_ds = None
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 复制坡面结果数据和重分类
    print("-> Copy/Reclassify Slope surface...")
    stage_time = time.perf_counter()
    w_w_surface_ds = gdal.Open(water_s_s_tif_path)
    no_data_value = w_w_surface_ds.GetRasterBand(1).GetNoDataValue()
    cu.tif_reclassify(water_s_s_tif_path, result_path + "/slope.tif",
                      [[-99]], [int(no_data_value)])
    w_w_surface_ds = None
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    print("---------------------------------Delete Temporary Files-----------------------------")
    stage_time = time.perf_counter()
    print("Delete Folders...")
    shutil.rmtree(process_path)
    shutil.rmtree(data_path)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')
    print("----------------------------------------Over----------------------------------------")
    end = time.perf_counter()
    print('Total time: ', end - start, 's')


# 测试直接使用DEM、汇流、原始流向等得到结果数据
if __name__ == '__main__':
    demo_start = time.perf_counter()
    # 数据基本路径
    base_path = "/usr/local/large_scale_hydro/Test/3"
    # base_path = "/home/liujz/data/Large_Scale_Watershed/Test/1"
    # 数据目录路径
    catalog = '/usr/local/large_scale_hydro/catalog'
    # catalog = '/home/liujz/data/Large_Scale_Watershed/catalog'
    # 范围数据(GeoJson)
    geojson_file_path = base_path + "/polygon.geojson"
    # 河流提取阈值
    extract_threshold = 800
    # 生成示例结果
    demo6(base_path, catalog, geojson_file_path, extract_threshold)
    demo_end = time.perf_counter()
    print('Demo total time: ', demo_end - demo_start, 's')
