import os
import time


# 提取子流域：工作空间 高程数据 河网提取阈值
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
    print("D8 Flow Directions")
    # 流向数据
    dir_tif_path = result_path + "/dir.tif"
    # 斜率
    slope_output_path = result_path + "/slopes.tif"
    # cmd语句调用TauDEM的D8 Flow Directions程序
    dir_cmd = 'mpiexec -n ' + str(5) + ' ' + current_path + '/TauDEM/D8Flowdir -fel ' + dem_tif_path + ' -p ' + \
              dir_tif_path + ' -sd8 ' + slope_output_path

    # 计算共享区
    print("D8 Contributing Area")
    # D8贡献区数据
    contributing_area_path = result_path + "/con_area.tif"
    # cmd语句调用TauDEM的D8 Contributing Area程序
    con_cmd = 'mpiexec -np ' + str(4) + ' ' + current_path + '/TauDEM/AreaD8 -p ' + dir_tif_path + ' -ad8 ' + \
              contributing_area_path

    # 计算汇流累积量
    print("Grid Network")
    # 上游最长流长
    longest_upstream_path = result_path + "/longest_flow.tif"
    # 上游总流长，即汇流累积量
    total_upstream_path = result_path + "/acc.tif"
    # 河网分级数据
    str_order_acc_path = result_path + "/ord_acc.tif"
    # cmd语句调用TauDEM的Stream Definition By Threshold程序
    acc_cmd = 'mpiexec -n ' + str(5) + ' ' + current_path + '/TauDEM/Gridnet -p ' + dir_tif_path + ' -plen ' + \
              longest_upstream_path + ' -tlen ' + total_upstream_path + ' -gord ' + str_order_acc_path

    # 提取河流
    print("Stream Definition By Threshold")
    # 河网数据
    str_tif_path = result_path + "/stream.tif"
    # 提取阈值
    extract_threshold = str(river_threshold)
    # cmd语句调用TauDEM的Stream Definition By Threshold程序
    str_cmd = 'mpiexec -n ' + str(5) + ' ' + current_path + '/TauDEM/Threshold -ssa ' + total_upstream_path + \
              ' -src ' + str_tif_path + ' -thresh ' + extract_threshold

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
    # cmd语句调用TauDEM的Stream Reach And Watershed程序
    ws_cmd = 'mpiexec -n ' + str(5) + ' ' + current_path + '/TauDEM/Streamnet -fel ' + dem_tif_path + ' -p ' + \
             dir_tif_path + ' -ad8 ' + contributing_area_path + ' -src ' + str_tif_path + ' -ord ' + \
             str_order_path + ' -tree ' + str_tree_txt_path + ' -coord ' + str_coord_txt_path + ' -net ' + \
             str_shp_path + ' -w ' + ws_tif_path

    # 合并cmd命令
    print(dir_cmd)
    print(con_cmd)
    print(acc_cmd)
    print(str_cmd)
    print(ws_cmd)
    union_cmd = dir_cmd + ' && ' + con_cmd + ' &&' + acc_cmd + ' && ' + str_cmd + ' && ' + ws_cmd
    # 执行cmd
    d = os.system(union_cmd)
    print(d)


# 此程序可用cmd调用python执行
# 提取子流域为tif，过程数据中包含河网的tif和shp类型数据
if __name__ == '__main__':
    start = time.perf_counter()
    get_watershed("D:/Graduation/Program/Data/2", "dem_fill1.tif", 300000)
    end = time.perf_counter()
    print('Run', end - start, 's')
