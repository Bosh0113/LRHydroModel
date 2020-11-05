import os
import time
import gdal
import taudem_utils as tu
import common_utils as cu

water_value = -99


# 判断索引的像元是否为湖泊/水库：湖泊水库数据集 x索引 y索引
def is_water_cell(water_dataset, xoff, yoff):
    global water_value
    # 判断是否在water数据中
    judge_in_data = cu.in_data(xoff, yoff, water_dataset.RasterXSize, water_dataset.RasterYSize)
    # 如果在water数据内
    if judge_in_data:
        # 获取water内像元值
        water_data_value = cu.get_raster_int_value(water_dataset, xoff, yoff)
        # 如果像元为湖泊/水库则判断当前河流像元是否与湖泊/水库邻接
        if water_data_value == water_value:
            return 1
    return 0


# 结合河流修正湖泊/水库边界：湖泊/水库数据路径 河网数据路径 流向数据路径
def water_revise(water_tif_path, river_tif_path, dir_tif_path):
    global water_value

    # 创建数据集
    water_ds = gdal.OpenEx(water_tif_path, 1)
    river_ds = gdal.Open(river_tif_path)
    dir_ds = gdal.Open(dir_tif_path)

    # 河流在water中的索引数组
    river_in_water_data = []
    # 遍历水体数据搜索范围内河流
    for i in range(water_ds.RasterYSize):
        for j in range(water_ds.RasterXSize):
            # 获取该点x,y在river中的索引
            river_off = cu.off_transform(j, i, water_ds, river_ds)
            # 获取river中该点的值
            river_value = cu.get_raster_int_value(river_ds, river_off[0], river_off[1])
            # 判断是否为河流
            if river_value == 1:
                # 记录河流在water中的索引
                river_in_water_data.append([j, i])

    # 根据与河流的邻近关系更新水体边界
    update_flag = 1
    while update_flag:
        # 标记是否更新完成
        update_flag = 0
        print("update")
        # 根据水体与河流邻接更新水体
        for index in range(len(river_in_water_data)):
            river_in_water_x = river_in_water_data[index][0]
            river_in_water_y = river_in_water_data[index][1]
            # 获取该点在water中的值
            water_data_value = cu.get_raster_int_value(water_ds, river_in_water_x, river_in_water_y)
            # 判断若不在水体内
            if water_data_value != water_value:
                # 获取该点x,y在river中的索引
                river_off = cu.off_transform(river_in_water_x, river_in_water_y, water_ds, river_ds)
                # 获取该处流向
                dir_off = cu.off_transform(river_in_water_x, river_in_water_y, water_ds, dir_ds)
                dir_value = cu.get_raster_int_value(dir_ds, dir_off[0], dir_off[1])
                # 获取该处在river的下一个像元索引
                to_river_point = cu.get_to_point(river_off[0], river_off[1], dir_value)
                # 获取该点在water中的索引
                w_n_off = cu.off_transform(to_river_point[0], to_river_point[1], river_ds, water_ds)
                to_point_is_water = is_water_cell(water_ds, w_n_off[0], w_n_off[1])
                if to_point_is_water:
                    # 若当前像元与下游像元x相同
                    if river_in_water_x == w_n_off[0]:
                        # 判断当前像元y方向上下是否为湖泊/水库
                        r_in_w_n0_is_water = is_water_cell(water_ds, river_in_water_x - 1, river_in_water_y)
                        r_in_w_n1_is_water = is_water_cell(water_ds, river_in_water_x + 1, river_in_water_y)
                        if r_in_w_n0_is_water or r_in_w_n1_is_water:
                            # 更新water此处为湖泊/水库
                            cu.set_raster_int_value(water_ds, river_in_water_x, river_in_water_y, water_value)
                            update_flag = 1
                    # 若当前像元与下游像元y相同
                    elif river_in_water_y == w_n_off[1]:
                        # 判断当前像元y方向上下是否为湖泊/水库
                        r_in_w_n0_is_water = is_water_cell(water_ds, river_in_water_x, river_in_water_y - 1)
                        r_in_w_n1_is_water = is_water_cell(water_ds, river_in_water_x, river_in_water_y + 1)
                        if r_in_w_n0_is_water or r_in_w_n1_is_water:
                            # 更新water此处为湖泊/水库
                            cu.set_raster_int_value(water_ds, river_in_water_x, river_in_water_y, water_value)
                            update_flag = 1
                    # 若当前像元与下游像元不在xy轴共线
                    else:
                        # 判断两像元公共邻接像元是否为湖泊/水库
                        r_in_w_n0_is_water = is_water_cell(water_ds, river_in_water_x, w_n_off[1])
                        r_in_w_n1_is_water = is_water_cell(water_ds, w_n_off[0], river_in_water_y)
                        if r_in_w_n0_is_water or r_in_w_n1_is_water:
                            # 更新water此处为湖泊/水库
                            cu.set_raster_int_value(water_ds, river_in_water_x, river_in_water_y, water_value)
                            update_flag = 1

    water_ds = None
    river_ds = None
    dir_ds = None


# 河流修正入口函数：工作空间路径 高程数据路径 水体数据路径
def water_revise_prepare(work_path, dem_tif_path, water_tif_path, extract_threshold):

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
    extract_threshold = str(extract_threshold)
    # 调用方法
    tu.stream_definition_by_threshold(total_upstream_path, str_tif_path, extract_threshold)

    # 新建结果数据
    water_copy_path = work_path + '/water_revised.tif'
    cu.copy_tif_data(water_tif_path, water_copy_path)

    # 修正水体
    water_revise(water_copy_path, str_tif_path, dir_tif_path)


if __name__ == '__main__':
    start = time.perf_counter()
    base_path = "D:/Graduation/Program/Data/3"
    workspace_path = base_path + "/result"
    water_revise_prepare(workspace_path, base_path + "/dem_fill.tif", base_path + "/tashan_99.tif", 300000)
    end = time.perf_counter()
    print('Run', end - start, 's')
