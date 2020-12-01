import direction_reclassify as dc
import river_extract as re
import watershed_extract as we
import water_revise as wr
import slope_surface_extract as sse
import common_utils as cu
import record_rivers as rr
import os
import time
import shutil
import gdal


# 示例：工作空间路径 DEM数据路径 流向数据路径 汇流累积量数据路径 湖泊/水库数据路径 河流提取阈值
def demo3(workspace_path, dem_tif_path, dir_tif_path, acc_tif_path, water_tif_path, river_threshold):

    start = time.perf_counter()

    # 工作空间路径
    process_path = workspace_path + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)

    # 流向数据重分类
    print("--------------------------------Reclassify Direction--------------------------------")
    stage_time = time.perf_counter()
    dir_reclass_tif = process_path + "/dir_reclass.tif"
    dc.dir_reclassify(dir_tif_path, dir_reclass_tif)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 提取河系
    print("-------------------------------------Get Rivers-------------------------------------")
    stage_time = time.perf_counter()
    re.get_river(process_path, acc_tif_path, river_threshold)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 记录河系信息
    print("------------------------------------Record Rivers------------------------------------")
    stage_time = time.perf_counter()
    river_tif_path = process_path + "/stream.tif"
    rr.record_rivers(process_path, river_tif_path, acc_tif_path)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 修正湖泊/水库边界
    print("----------------------------------Get Revised Water----------------------------------")
    stage_time = time.perf_counter()
    water_revised_path = process_path + "/water_revised.tif"
    cu.copy_tif_data(water_tif_path, water_revised_path)
    wr.water_revise(water_revised_path, river_tif_path, process_path + "/river_record.txt", dir_reclass_tif)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 提取坡面和湖泊/水库
    print("----------------------------------Get Slope Surface----------------------------------")
    stage_time = time.perf_counter()
    sse.get_slope_surface(process_path, water_revised_path, dir_reclass_tif, acc_tif_path, river_threshold, -9)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    # 提取子流域
    print("------------------------------------Get Watershed-----------------------------------")
    stage_time = time.perf_counter()
    water_s_s_tif_path = process_path + "/water_slope_surface.tif"
    we.watershed_extract(process_path, dem_tif_path, dir_reclass_tif, acc_tif_path, river_tif_path, water_s_s_tif_path)
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
    cu.tif_reclassify(water_s_s_tif_path, result_path + "/slope_surface.tif",
                      [[-99]], [int(no_data_value)])
    w_w_surface_ds = None
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    print("------Over------")
    end = time.perf_counter()
    print('Total time: ', end - start, 's')


# 测试直接使用DEM、汇流、原始流向等得到结果数据
if __name__ == '__main__':
    demo_start = time.perf_counter()
    # 数据基本路径
    base_path = "D:/Graduation/Program/Data/21"
    # DEM数据路径
    dem_data_path = base_path + "/dem.tif"
    # 流向数据路径
    dir_data_path = base_path + "/dir.tif"
    # 汇流累积量数据路径
    acc_data_path = base_path + "/acc.tif"
    # 湖泊/水库数据路径
    lake_data_path = base_path + "/lakes.tif"
    # 河流提取阈值
    extract_threshold = 20
    # 生成示例结果
    demo3(base_path, dem_data_path, dir_data_path, acc_data_path, lake_data_path, extract_threshold)
    demo_end = time.perf_counter()
    print('Demo total time: ', demo_end - demo_start, 's')
