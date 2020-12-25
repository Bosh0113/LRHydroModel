import os
import gdal
import time
import taudem_utils as tu
import common_utils as cu

# 是否考虑边界污染(默认不考虑)
nc = 0

# dataset_ol = None
update_index = 0


# 判断点坐标是否在范围内: 点坐标 范围左上角 范围右下角 判断结果(返回)
def is_in_scale(point, scale_ft, scale_rb):
    if scale_ft[0] <= point[0] <= scale_rb[0] and scale_ft[1] >= point[1] >= scale_rb[1]:
        return 1
    else:
        return 0


# 查询点所处数据块: 点坐标 数据索引 数据路径(返回)
def find_data_by_point(point, data_index):
    # 遍历数据索引
    for key, value in data_index.items():
        scale = value
        if is_in_scale(point, scale[0], scale[1]):
            return key
    return ""


# 记录geoTif数据块路径及其空间范围: 数据路径集合 数据范围描述(返回)
def record_data_scale(tif_paths):
    data_scale = {}
    for tif_path in tif_paths:
        t_ds = gdal.Open(tif_path)
        transform = t_ds.GetGeoTransform()
        # 数据块左上角坐标
        left_top = [transform[0], transform[3]]
        # 数据块右下角像元的左上角坐标
        right_bottom = [transform[0] + (t_ds.RasterXSize - 1) * transform[1],
                        transform[3] + (t_ds.RasterYSize - 1) * transform[5]]
        # 数据块范围记录
        scale = [left_top, right_bottom]
        data_scale[tif_path] = scale
        t_ds = None
    return data_scale


# # 记录数据有效nodata: acc数据块路径集合 参考流向数据集的范围描述 有效nodata坐标索引(返回) 边界nodata坐标索引(返回)
# def record_temp_nodata(acc_paths, dir_ref_scales):
# 记录数据有效nodata: acc数据块路径集合 参考流向数据集的范围描述(暂使用合并结果) 有效nodata坐标索引(返回) 边界nodata坐标索引(返回)
def record_temp_nodata(acc_paths, dir_paths):
    # 初始化有效nodata的坐标索引集合
    temp_nodata = []
    # 遍历数据块
    for index in range(0, len(acc_paths)):
        acc_tif = acc_paths[index]
        dir_tif = dir_paths[index]
        acc_ds = gdal.Open(acc_tif)
        dir_ds = gdal.Open(dir_tif)
        acc_nodata = acc_ds.GetRasterBand(1).GetNoDataValue()
        # # 遍历数据块的像元
        for y in range(acc_ds.RasterYSize):
            for x in range(acc_ds.RasterXSize):
                # 判断是否为nodata
                acc_value = cu.get_raster_float_value(acc_ds, x, y)
                if acc_value == acc_nodata:
                    # 判断是否为有效nodata
                    dir_off = cu.off_transform(x, y, acc_ds, dir_ds)
                    dir_value = cu.get_raster_int_value(dir_ds, dir_off[0], dir_off[1])
                    # 若是有效nodata则记录其左上角坐标索引
                    if dir_value in [1, 2, 3, 4, 5, 6, 7, 8]:
                        # 当前像元的左上角坐标
                        transform = acc_ds.GetGeoTransform()
                        xy_current = [transform[0] + x * transform[1], transform[3] + y * transform[5]]
                        # 记录到数组
                        temp_nodata.append(xy_current)
        acc_ds = None
        dir_ds = None
    return temp_nodata


# 判断是否在整体数据的边界: 当前点坐标 整体数据左上角坐标 整体数据右下角像元的左上角坐标 判断值(返回)
def in_edge(point, extent_lt, extent_rb):
    if point[0] == extent_lt[0] or point[1] == extent_lt[1] or point[0] == extent_rb[0] or point[1] == extent_rb[1]:
        return 1


# 判断是否可以更新当前汇流累积量: 当前点坐标对 像元x宽 像元y长 acc索引 dir索引 当前acc值(返回)
def able_update_acc(b_point, x_size, y_size, acc_index, dir_index):
    global nc
    # 获取acc整体数据边界
    total_lt = list(acc_index.values())[0][0][:]
    total_rb = list(acc_index.values())[0][0][:]
    for value in acc_index.values():
        if total_lt[0] >= value[0][0]:
            total_lt[0] = value[0][0]
        if total_lt[1] <= value[0][1]:
            total_lt[1] = value[0][1]
        if total_rb[0] <= value[1][0]:
            total_rb[0] = value[1][0]
        if total_rb[1] >= value[1][1]:
            total_rb[1] = value[1][1]

    # 初始化上游像元汇流累积量(初始化为0)
    up_cells_acc = 0
    # 初始化标记存在上游像元(初始化为不存在)
    up_cell_flag = 0
    # 初始化标记存在上游像元acc暂为nodata(初始化为存在nodata上游点)
    up_nodata_flag = 0
    # 获取周边像元坐标(左上角)从邻近像元搜索
    n_cells = cu.get_8_dir_coord(b_point[0], b_point[1], x_size, y_size)
    for n_cell in n_cells:
        # 得到所处数据块
        acc_path = find_data_by_point(n_cell, acc_index)
        dir_path = find_data_by_point(n_cell, dir_index)
        if acc_path != "" and dir_path != "":
            # 判断是否为上游点
            dir_ds = gdal.Open(dir_path)
            # 根据坐标转为索引
            n_off = cu.coord_to_off(n_cell, dir_ds)
            # 获得此处流向值
            dir_value = cu.get_raster_int_value(dir_ds, n_off[0], n_off[1])
            # 获得下游像元索引
            d_off = cu.get_to_point(n_off[0], n_off[1], dir_value)
            # 若为有下游像元
            if d_off:
                # 获取该下游像元的坐标
                d_coord = cu.off_to_coord(d_off, dir_ds)
                # 若该下游像元坐标与当前坐标相同则此邻近像元为上游像元
                if d_coord == b_point:
                    up_cell_flag = 1
                    # 获取此上游像元处的汇流累积量值
                    acc_ds = gdal.Open(acc_path)
                    n_acc_off = cu.coord_to_off(n_cell, acc_ds)
                    n_acc = cu.get_raster_float_value(acc_ds, n_acc_off[0], n_acc_off[1])
                    # 若此acc值为nodata则标记存在上游像元acc暂为nodata
                    if int(n_acc) <= 0:
                        up_nodata_flag = 1
                        break
                    # 否则记录当前值到总上游累积量
                    else:
                        up_cells_acc += n_acc
                    acc_ds = None
            dir_ds = None
    # 若存在上游像元
    if up_cell_flag:
        # 若上游像元均有有效acc值
        if up_nodata_flag == 0:
            # 更新上游acc总值和自身累积量值到当前像元
            current_acc = up_cells_acc + 1.0
            return current_acc
        # 存在上游像元暂为nodata
        else:
            return 0
    # 若不存在上游像元
    else:
        # 若考虑边界污染
        if nc:
            # 若在边界上
            if in_edge(b_point, total_lt, total_rb):
                return 0
            else:
                # 否则作为汇流起始点
                return 1.0
        # 若不考虑边界污染
        else:
            return 1.0


# 根据坐标更新对应acc值: 点坐标对 acc数据索引 acc值
def update_acc_by_coord(point, acc_index, acc_value):
    current_acc_path = find_data_by_point(point, acc_index)
    cu_acc_ds = gdal.Open(current_acc_path, 1)
    cu_off = cu.coord_to_off(point, cu_acc_ds)
    cu.set_raster_float_value(cu_acc_ds, cu_off[0], cu_off[1], acc_value)
    cu_acc_ds = None
    # 另行记录更新的像元
    global update_index
    update_index += 1
    # check_off = cu.coord_to_off(point, dataset_ol)
    # cu.set_raster_float_value(dataset_ol, check_off[0], check_off[1], acc_value)
    print("\r", point, "->", acc_value, " Updated Num: ", update_index, end="")


# 得到下游像元的坐标: 当前点坐标 dir索引 下游像元坐标(返回)
def down_point_coord(b_point, dir_index):
    current_dir_path = find_data_by_point(b_point, dir_index)
    cu_dir_ds = gdal.Open(current_dir_path)
    dir_off = cu.coord_to_off(b_point, cu_dir_ds)
    dir_value = cu.get_raster_int_value(cu_dir_ds, dir_off[0], dir_off[1])
    to_off = cu.get_to_point(dir_off[0], dir_off[1], dir_value)
    to_coord = cu.off_to_coord(to_off, cu_dir_ds)
    cu_dir_ds = None
    return to_coord


# 更新汇流累积量数据中的有效nodata值: acc数据块的范围索引 dir数据的范围索引 像元x距离 像元y距离 有效nodata数组 有效边界nodata数组 考虑边界污染(默认不考虑)
def update_acc_nodata(acc_index, dir_index, x_size, y_size, temp_nodata, nc_p=0):
    global nc
    # 标识是否考虑边界污染
    nc = nc_p
    # 初始化被更新标识
    update_flag = 1
    # 初始化循环时初始记录
    o_b_nodata = temp_nodata[:]
    # 检查更新
    while update_flag:
        # 重置更新标识
        update_flag = 0
        print("change flag")
        # 获得要遍历的有效边界nodata数组
        t_b_nodata = o_b_nodata[:]
        # 遍历有效边界nodata数组
        print("Current Num of NoData: ", len(t_b_nodata))
        print("")
        for b_point in t_b_nodata:
            current_acc = able_update_acc(b_point, x_size, y_size, acc_index, dir_index)
            # 若为有效acc值
            if current_acc:
                # 若还未更新
                if b_point in o_b_nodata:
                    # 标识存在更新
                    update_flag = 1
                    # 根据坐标更新对应acc值
                    update_acc_by_coord(b_point, acc_index, current_acc)
                    # 在nodata数据记录中删除此点
                    o_b_nodata.remove(b_point)
                    # 对其下游像元检查更新
                    # 得到下游像元的坐标
                    to_coord = down_point_coord(b_point, dir_index)
                    # 初始化更新追踪数组
                    down_points = [to_coord]
                    while len(down_points) > 0:
                        d_point = down_points.pop()
                        # 若为nodata数组中值
                        if d_point in o_b_nodata:
                            current_acc = able_update_acc(d_point, x_size, y_size, acc_index, dir_index)
                            if current_acc:
                                # 更新当前坐标的acc值
                                update_acc_by_coord(d_point, acc_index, current_acc)
                                # 删除此处nodata的记录
                                o_b_nodata.remove(d_point)
                                # 将下游点放入追踪数组
                                to_coord = down_point_coord(d_point, dir_index)
                                down_points.append(to_coord)


if __name__ == '__main__':
    start = time.perf_counter()

    workspace = "D:/Graduation/Program/Data/32"
    process_path = workspace + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)

    dir_tifs = []
    acc_tifs = []
    print("Dir and Acc")
    for i in range(1, 4):
        for j in range(1, 4):
            dem_tif = workspace + "/data/dem/" + str(i) + "_" + str(j) + ".tif"
            dir_tif = workspace + "/data/dir/" + str(i) + "_" + str(j) + ".tif"
            slope_tif = workspace + "/data/slope/" + str(i) + "_" + str(j) + ".tif"
            # tu.d8_flow_directions(dem_tif, dir_tif, slope_tif)

            acc_tif = workspace + "/data/acc/" + str(i) + "_" + str(j) + ".tif"
            # tu.d8_contributing_area(dir_tif, acc_tif, 1)

            dir_tifs.append(dir_tif)
            acc_tifs.append(acc_tif)

    print("Record Scale")
    acc_scale = record_data_scale(acc_tifs)

    # 根据原始数据块生成连接处数据
    # 代码暂略
    dir_refs = []
    for i in range(1, 4):
        for j in range(1, 4):
            dir_tif = workspace + "/data/dir_ref/" + str(i) + "_" + str(j) + ".tif"
            dir_refs.append(dir_tif)
    dir_scale = record_data_scale(dir_refs)

    print("Record nodata")
    t_nodata = record_temp_nodata(acc_tifs, dir_refs)

    # 检查记录的结果
    # ref_dir_path = "D:/Graduation/Program/Data/32/preprocess1/acc.tif"
    # temp_tif_path = "D:/Graduation/Program/Data/32/dif/update_nodata0.tif"
    # ref_ds = gdal.Open(ref_dir_path)
    # dir_geotransform = ref_ds.GetGeoTransform()
    # file_format = "GTiff"
    # driver = gdal.GetDriverByName(file_format)
    # dataset_ol = driver.Create(temp_tif_path, ref_ds.RasterXSize, ref_ds.RasterYSize, 1, gdal.GDT_Float32)
    # dataset_ol.SetGeoTransform(dir_geotransform)
    # dataset_ol.SetProjection(ref_ds.GetProjection())
    # dataset_ol.GetRasterBand(1).SetNoDataValue(0)
    # ref_ds = None

    print("Update Acc")
    data_ds = gdal.Open(dir_tifs[0])
    transform = data_ds.GetGeoTransform()
    x_cell_size = transform[1]
    y_cell_size = transform[5]
    data_ds = None
    update_acc_nodata(acc_scale, dir_scale, x_cell_size, y_cell_size, t_nodata, 0)
    # update_acc_nodata(acc_scale, dir_scale, x_cell_size, y_cell_size, t_nodata, 1)

    # dataset_ol = None

    end = time.perf_counter()
    print('Run', end - start, 's')
