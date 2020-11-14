import os
import time
import taudem_utils as tu


# 提取子流域入口函数：工作空间 高程数据路径 河网提取阈值
def get_watershed(work_path, dem_tif_path, river_threshold):

    # 创建结果数据文件夹
    if not os.path.exists(work_path):
        os.makedirs(work_path)

    # 计算流向
    print("D8 Flow Directions")
    # 流向数据
    dir_tif_path = work_path + "/dir.tif"
    # 斜率
    slope_output_path = work_path + "/slopes.tif"
    # 调用方法
    tu.d8_flow_directions(dem_tif_path, dir_tif_path, slope_output_path)

    # 计算共享区
    print("D8 Contributing Area")
    # D8贡献区数据
    contributing_area_path = work_path + "/con_area.tif"
    # 调用方法
    tu.d8_contributing_area(dir_tif_path, contributing_area_path)

    # 计算汇流累积量
    print("Grid Network")
    # 上游最长流长
    longest_upstream_path = work_path + "/longest_flow.tif"
    # 上游总流长，即汇流累积量
    total_upstream_path = work_path + "/acc.tif"
    # 河网分级数据
    str_order_acc_path = work_path + "/ord_acc.tif"
    # 调用方法
    tu.grid_network(dir_tif_path, longest_upstream_path, total_upstream_path, str_order_acc_path)

    # 提取河流
    print("Stream Definition By Threshold")
    # 河网数据
    str_tif_path = work_path + "/stream.tif"
    # 提取阈值
    extract_threshold = str(river_threshold)
    # 调用方法
    tu.stream_definition_by_threshold(total_upstream_path, str_tif_path, extract_threshold)

    # 提取子流域
    print("Stream Reach And Watershed")
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
    tu.stream_reach_and_watershed(dem_tif_path, dir_tif_path, contributing_area_path, str_tif_path, str_order_path,
                                  str_tree_txt_path, str_coord_txt_path, str_shp_path, ws_tif_path)


# 此程序可用cmd调用python执行
# 提取子流域为tif，过程数据中包含河网的tif和shp类型数据
if __name__ == '__main__':
    start = time.perf_counter()
    # base_path = "D:/Graduation/Program/Data/3"
    base_path = "D:/Graduation/Program/Data/14/test/tauDEM"
    workspace_path = base_path + "/result"
    get_watershed(workspace_path, base_path + "/dem_fill.tif", 300000)
    end = time.perf_counter()
    print('Run', end - start, 's')
