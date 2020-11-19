import os
import time
import taudem_utils as tu


# 提取子流域入口函数：工作空间 高程数据路径 流向数据路径 汇流累积量数据路径 河网提取阈值
def get_watershed(work_path, dem_tif_path, dir_tif_path, acc_tif_path, river_threshold):

    # 创建结果数据文件夹
    if not os.path.exists(work_path):
        os.makedirs(work_path)

    # 提取河流
    print("Stream Definition By Threshold")
    # 河网数据
    str_tif_path = work_path + "/stream.tif"
    # 提取阈值
    extract_threshold = str(river_threshold)
    # 调用方法
    tu.stream_definition_by_threshold(acc_tif_path, str_tif_path, extract_threshold)

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
    tu.stream_reach_and_watershed(dem_tif_path, dir_tif_path, acc_tif_path, str_tif_path, str_order_path,
                                  str_tree_txt_path, str_coord_txt_path, str_shp_path, ws_tif_path)


# 此程序可用cmd调用python执行
# 提取子流域为tif，过程数据中包含河网的tif和shp类型数据
if __name__ == '__main__':
    start = time.perf_counter()
    base_path = "D:/Graduation/Program/Data/14/yamazaki"
    workspace_path = base_path + "/result"
    get_watershed(workspace_path, base_path + "/dem_fill.tif", base_path + "/dir.tif", base_path + "/acc.tif", 20)
    end = time.perf_counter()
    print('Run', end - start, 's')
