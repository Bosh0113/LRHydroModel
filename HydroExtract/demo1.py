import watershed_extract as we
import water_revise as wr
import slope_surface_extract as sse
import common_utils as cu
import os
import time
import shutil
import gdal


# 示例
def demo1():
    # 数据基本路径
    base_path = "D:/Graduation/Program/Data/4"
    # 工作空间路径
    workspace_path = base_path + "/process"
    # 河流提取阈值
    river_threshold = 300000
    # 提取子流域
    print("----------------------------------Get Watershed----------------------------------")
    we.get_watershed(workspace_path, base_path + "/dem_fill.tif", river_threshold)
    # 修正湖泊/水库边界
    print("----------------------------------Get Revised Water----------------------------------")
    water_revised_path = workspace_path + "/water_revised.tif"
    cu.copy_tif_data(base_path + "/tashan_99.tif", water_revised_path)
    wr.water_revise(water_revised_path, workspace_path + "/stream.tif", workspace_path + "/dir.tif")
    # 提取坡面和湖泊/水库
    print("----------------------------------Get Slope Surface----------------------------------")
    sse.get_slope_surface(workspace_path, workspace_path + "/water_revised.tif", workspace_path + "/dir.tif",
                          workspace_path + "/acc.tif", river_threshold)

    # 结果文件夹
    print("----------------------------------Copy Result Data----------------------------------")
    result_path = base_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    # 复制修正后的湖泊/水库以及河网矢量结果数据到文件夹
    file_list = os.listdir(workspace_path)
    result_files = ["water_revised", "stream_shp"]
    for file in file_list:
        file_info = file.split(".")
        if file_info[0] in result_files:
            shutil.copy(workspace_path + "/" + file, result_path + "/" + file)

    # 对子流域结果掩膜输出至结果文件夹
    cu.raster_mask(workspace_path + "/watershed.tif", workspace_path + "/water_slope_surface.tif",
                   result_path + "/watershed.tif")

    # 复制河网栅格结果数据和重分类
    river_ds = gdal.Open(workspace_path + "/stream.tif")
    no_data_value = river_ds.GetRasterBand(1).GetNoDataValue()
    cu.tif_reclassify(workspace_path + "/stream.tif", result_path + "/stream.tif", [[0]], [int(no_data_value)])
    river_ds = None

    # 复制坡面结果数据和重分类
    w_w_surface_ds = gdal.Open(workspace_path + "/water_slope_surface.tif")
    no_data_value = w_w_surface_ds.GetRasterBand(1).GetNoDataValue()
    cu.tif_reclassify(workspace_path + "/water_slope_surface.tif", result_path + "/slope_surface.tif",
                      [[-99]], [int(no_data_value)])
    w_w_surface_ds = None


if __name__ == '__main__':
    start = time.perf_counter()
    demo1()
    end = time.perf_counter()
    print('Run', end - start, 's')
