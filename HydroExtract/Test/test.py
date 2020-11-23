import common_utils as cu
import taudem_utils as tu
import os
import time


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "D:/Graduation/Program/Data/14/test_ws_recode"
    process_path = workspace_path + "/preprocess"
    data_path = workspace_path + "/data"
    # cu.raster_clip_mask(process_path + "/stream.tif", process_path + "/water_slope_surface.tif", data_path + "/stream.tif")
    # cu.raster_clip_mask(process_path + "/acc.tif", process_path + "/water_slope_surface.tif", data_path + "/acc.tif")
    # cu.raster_clip_mask(process_path + "/dir.tif", process_path + "/water_slope_surface.tif", data_path + "/dir.tif")
    # cu.raster_clip_mask(process_path + "/dem_fill.tif", process_path + "/water_slope_surface.tif", data_path + "/dem_fill.tif", "float")

    work_path = workspace_path + "/result"
    if not os.path.exists(work_path):
        os.makedirs(work_path)

    # 提取子流域
    print("Stream Reach And Watershed")
    # DEM数据
    dem_tif_path = data_path + "/dem_fill.tif"
    # 流向数据
    dir_tif_path = data_path + "/dir.tif"
    # 汇流累积数据
    acc_tif_path = data_path + "/acc.tif"
    # 河网数据
    str_tif_path = data_path + "/stream.tif"
    # 河网分级数据
    str_order_path = work_path + "/ord.tif"
    # 河网连接树文本
    str_tree_txt_path = work_path + "/tree.dat"
    # 河网投影列表
    str_coord_txt_path = work_path + "/coord.dat"
    # 河网矢量数据
    str_shp_path = work_path + "/stream_shp.shp"
    # 子流域数据
    ws_tif_path = work_path + "/watershed.tif"
    # 调用方法
    tu.stream_reach_and_watershed(dem_tif_path, dir_tif_path, acc_tif_path, str_tif_path, str_order_path,
                                  str_tree_txt_path, str_coord_txt_path, str_shp_path, ws_tif_path)

    end = time.perf_counter()
    print('Run', end - start, 's')

