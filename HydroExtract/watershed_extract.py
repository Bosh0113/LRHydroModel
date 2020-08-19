import os
import time


# 计算流向：DEM(input) 流向(output) 坡度(output)
def d8_flow_directions(dem_tif_path, dir_tif_path, slope_output_path):
    print("D8 Flow Directions")
    # 当前路径
    current_path = os.getcwd().replace("\\", "/")
    # cmd语句调用TauDEM的D8 Flow Directions程序
    dir_cmd = 'mpiexec -n ' + str(5) + ' ' + current_path + '/TauDEM/D8Flowdir -fel ' + dem_tif_path + ' -p ' + \
              dir_tif_path + ' -sd8 ' + slope_output_path
    d = os.system(dir_cmd)
    print(d)


# 计算贡献区：流向(input) 贡献区(output)
def d8_contributing_area(dir_tif_path, contributing_area_path):
    print("D8 Contributing Area")
    # 当前路径
    current_path = os.getcwd().replace("\\", "/")
    # cmd语句调用TauDEM的D8 Contributing Area程序
    con_cmd = 'mpiexec -np ' + str(4) + ' ' + current_path + '/TauDEM/AreaD8 -p ' + dir_tif_path + ' -ad8 ' + \
              contributing_area_path
    d = os.system(con_cmd)
    print(d)


# 计算汇流累积量：流向(input) 最长流长(output) 总流长(output) 河流分级(output)
def grid_network(dir_tif_path, longest_upstream_path, total_upstream_path, str_order_acc_path):
    print("Grid Network")
    # 当前路径
    current_path = os.getcwd().replace("\\", "/")
    # cmd语句调用TauDEM的Stream Definition By Threshold程序
    acc_cmd = 'mpiexec -n ' + str(5) + ' ' + current_path + '/TauDEM/Gridnet -p ' + dir_tif_path + ' -plen ' + \
              longest_upstream_path + ' -tlen ' + total_upstream_path + ' -gord ' + str_order_acc_path
    d = os.system(acc_cmd)
    print(d)


# 提取河流：汇流累积量(input) 河流(output) 提取阈值(input)
def stream_definition_by_threshold(total_upstream_path, str_tif_path, extract_threshold):
    print("Stream Definition By Threshold")
    # 当前路径
    current_path = os.getcwd().replace("\\", "/")
    # cmd语句调用TauDEM的Stream Definition By Threshold程序
    str_cmd = 'mpiexec -n ' + str(5) + ' ' + current_path + '/TauDEM/Threshold -ssa ' + total_upstream_path + \
              ' -src ' + str_tif_path + ' -thresh ' + extract_threshold
    d = os.system(str_cmd)
    print(d)


# 提取子流域： DEM(input) 流向(input) 贡献区(input) 河流(input) 河流分级(output) 河流树状记录(output) 河流坐标(output)
# 矢量河流(output) 子流域(output)
def stream_reach_and_watershed(dem_tif_path, dir_tif_path, contributing_area_path, str_tif_path, str_order_path,
                               str_tree_txt_path, str_coord_txt_path, str_shp_path, ws_tif_path):
    print("Stream Reach And Watershed")
    # cmd语句调用TauDEM的Stream Reach And Watershed程序
    # 当前路径
    current_path = os.getcwd().replace("\\", "/")
    ws_cmd = 'mpiexec -n ' + str(5) + ' ' + current_path + '/TauDEM/Streamnet -fel ' + dem_tif_path + ' -p ' + \
             dir_tif_path + ' -ad8 ' + contributing_area_path + ' -src ' + str_tif_path + ' -ord ' + \
             str_order_path + ' -tree ' + str_tree_txt_path + ' -coord ' + str_coord_txt_path + ' -net ' + \
             str_shp_path + ' -w ' + ws_tif_path
    d = os.system(ws_cmd)
    print(d)


# 提取子流域入口函数：工作空间 高程数据 河网提取阈值
def get_watershed(base_path, dem_tif, river_threshold):
    # 当前路径
    current_path = os.getcwd().replace("\\", "/")

    # 创建结果数据文件夹
    result_path = base_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    # 高程数据路径
    dem_tif_path = base_path + "/" + dem_tif

    # 计算流向
    # 流向数据
    dir_tif_path = result_path + "/dir.tif"
    # 斜率
    slope_output_path = result_path + "/slopes.tif"
    # 调用方法
    d8_flow_directions(dem_tif_path, dir_tif_path, slope_output_path)

    # 计算共享区
    print("D8 Contributing Area")
    # D8贡献区数据
    contributing_area_path = result_path + "/con_area.tif"
    # 调用方法
    d8_contributing_area(dir_tif_path, contributing_area_path)

    # 计算汇流累积量
    print("Grid Network")
    # 上游最长流长
    longest_upstream_path = result_path + "/longest_flow.tif"
    # 上游总流长，即汇流累积量
    total_upstream_path = result_path + "/acc.tif"
    # 河网分级数据
    str_order_acc_path = result_path + "/ord_acc.tif"
    # 调用方法
    grid_network(dir_tif_path, longest_upstream_path, total_upstream_path, str_order_acc_path)

    # 提取河流
    print("Stream Definition By Threshold")
    # 河网数据
    str_tif_path = result_path + "/stream.tif"
    # 提取阈值
    extract_threshold = str(river_threshold)
    # 调用方法
    stream_definition_by_threshold(total_upstream_path, str_tif_path, extract_threshold)

    # 提取子流域
    print("Stream Reach And Watershed")
    # 河网分级数据
    str_order_path = result_path + "/ord.tif"
    # 河网连接树文本
    str_tree_txt_path = result_path + "/tree.dat"
    # 河网投影列表
    str_coord_txt_path = result_path + "/coord.dat"
    # 河网矢量数据
    str_shp_path = result_path + "/stream_shp.shp"
    # 子流域数据
    ws_tif_path = result_path + "/watershed.tif"
    # 调用方法
    stream_reach_and_watershed(dem_tif_path, dir_tif_path, contributing_area_path, str_tif_path, str_order_path,
                               str_tree_txt_path, str_coord_txt_path, str_shp_path, ws_tif_path)


# 此程序可用cmd调用python执行
# 提取子流域为tif，过程数据中包含河网的tif和shp类型数据
if __name__ == '__main__':
    start = time.perf_counter()
    get_watershed("D:/Graduation/Program/Data/3", "dem_fill.tif", 300000)
    end = time.perf_counter()
    print('Run', end - start, 's')
