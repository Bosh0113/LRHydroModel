import watershed_extract as we
import water_revise as wr
import slope_surface_extract as sse
import common_utils as cu
import os
import time
import shutil
import gdal


# 示例：工作空间路径 DEM数据路径 湖泊/水库数据路径 河流提取阈值
def demo1(workspace_path, dem_tif_path, water_tif_path, river_threshold):
    # 工作空间路径
    process_path = workspace_path + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)
    # 提取子流域
    print("----------------------------------Get Watershed----------------------------------")
    we.get_watershed(process_path, dem_tif_path, river_threshold)
    # 修正湖泊/水库边界
    print("----------------------------------Get Revised Water----------------------------------")
    water_revised_path = process_path + "/water_revised.tif"
    cu.copy_tif_data(water_tif_path, water_revised_path)
    wr.water_revise(water_revised_path, process_path + "/stream.tif", process_path + "/dir.tif")
    # 提取坡面和湖泊/水库
    print("----------------------------------Get Slope Surface----------------------------------")
    sse.get_slope_surface(process_path, process_path + "/water_revised.tif", process_path + "/dir.tif",
                          process_path + "/acc.tif", river_threshold)

    # 结果文件夹
    print("----------------------------------Copy Result Data----------------------------------")
    result_path = workspace_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    # 复制修正后的湖泊/水库以及河网矢量结果数据到文件夹
    file_list = os.listdir(process_path)
    result_files = ["water_revised", "stream_shp"]
    for file in file_list:
        file_info = file.split(".")
        if file_info[0] in result_files:
            shutil.copy(process_path + "/" + file, result_path + "/" + file)

    # 对子流域结果掩膜输出至结果文件夹
    cu.raster_mask(process_path + "/watershed.tif", process_path + "/water_slope_surface.tif",
                   result_path + "/watershed.tif")

    # 复制河网栅格结果数据和重分类
    river_ds = gdal.Open(process_path + "/stream.tif")
    no_data_value = river_ds.GetRasterBand(1).GetNoDataValue()
    cu.tif_reclassify(process_path + "/stream.tif", result_path + "/stream.tif", [[0]], [int(no_data_value)])
    river_ds = None

    # 复制坡面结果数据和重分类
    w_w_surface_ds = gdal.Open(process_path + "/water_slope_surface.tif")
    no_data_value = w_w_surface_ds.GetRasterBand(1).GetNoDataValue()
    cu.tif_reclassify(process_path + "/water_slope_surface.tif", result_path + "/slope_surface.tif",
                      [[-99]], [int(no_data_value)])
    w_w_surface_ds = None


if __name__ == '__main__':
    start = time.perf_counter()
    # 数据基本路径
    # base_path = "D:/Graduation/Program/Data/4"
    # base_path = "D:/Graduation/Program/Data/5"
    base_path = "D:/Graduation/Program/Data/6"
    # DEM数据路径
    dem_data_path = base_path + "/dem_fill.tif"
    # 湖泊/水库数据路径
    # lake_data_path = base_path + "/tashan_99.tif"
    lake_data_path = base_path + "/lake_99.tif"
    # 河流提取阈值
    extract_threshold = 300000
    # extract_threshold = 30000
    # 生成示例结果
    demo1(base_path, dem_data_path, lake_data_path, extract_threshold)
    end = time.perf_counter()
    print('Run', end - start, 's')
