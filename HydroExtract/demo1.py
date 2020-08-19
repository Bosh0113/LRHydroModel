import watershed_extract as we
import water_revise as wr
import slope_surface_extract as sse
import common_utils as cu
import os
import time


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
    result_path = base_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    # 河网数据结果
    cu.copy_tif_data(workspace_path + "/stream.tif", result_path + "/stream.tif")
    # 子流域数据结果
    cu.copy_tif_data(workspace_path + "/watershed.tif", result_path + "/watershed.tif")
    # 湖泊/水库和坡面结果
    cu.copy_tif_data(workspace_path + "/water_slope_surface.tif", result_path + "/water_slope_surface.tif")


if __name__ == '__main__':
    start = time.perf_counter()
    demo1()
    end = time.perf_counter()
    print('Run', end - start, 's')
