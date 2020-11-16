import gdal
import os
import time
import common_utils as cu

dataset_res = None
dataset_dir = None
dataset_acc = None

dataset_ol = None
dataset_ro = None
river_th = 0

# 水体河道出入流处
water_channel = []
# 一像元宽水体外边界集合
water_ol_bufs = []

no_data_value = -9999
water_value = -99
water_buffer_value = -1
surface_route_value = 1


# 获取某点流向指向的点其在结果数据的值：x索引 y索引 某点流向指向的点其在结果数据的值(返回值)
def get_to_point_ol_data(xoff, yoff):
    global dataset_dir, dataset_ol
    dir_data_value = cu.get_raster_int_value(dataset_dir, xoff, yoff)
    to_point = cu.get_to_point(xoff, yoff, dir_data_value)
    if len(to_point) < 1:
        return no_data_value
    else:
        return cu.get_raster_int_value(dataset_ol, to_point[0], to_point[1])


# 对水体的坡面提取排序：原水体外边界集合 排序后的水体外边界集合 各水体外边界最大汇流累积点位置集合(返回值)
def water_order(old_water_bufs, new_water_bufs):
    global dataset_acc
    recode_acc = []
    new_water_bufs.clear()
    # 各水体外边界上最大汇流累积量位置的集合
    surface_route_start = []
    for water_buf in old_water_bufs:
        # 获取此水体外边界最大汇流累积量
        max_acc = 0.0
        # 记录最大汇流累积量位置索引
        max_acc_point = water_buf[0]
        for point in water_buf:
            # 获得汇流累积量
            acc_value = cu.get_raster_float_value(dataset_acc, point[0], point[1])
            # 更新最大值记录
            if acc_value > max_acc:
                max_acc = acc_value
                max_acc_point = point
        # 插入排序
        if len(recode_acc) == 0:
            recode_acc.append(max_acc)
            new_water_bufs.append(water_buf)
            surface_route_start.append(max_acc_point)
        else:
            for index in range(len(recode_acc)):
                if recode_acc[index] > max_acc:
                    recode_acc.insert(index, max_acc)
                    new_water_bufs.insert(index, water_buf)
                    surface_route_start.insert(index, max_acc_point)
                    break
                if index == len(recode_acc) - 1 and recode_acc[index] < max_acc:
                    recode_acc.append(max_acc)
                    new_water_bufs.append(water_buf)
                    surface_route_start.append(max_acc_point)

    return surface_route_start


# 提取坡面：原中心点x索引 原中心点y索引 点x索引 点y索引 坡面id
def extract_slope_surface(o_xoff, o_yoff, xoff, yoff, slope_surface_id, water_buf, upstream_inflow):
    global dataset_ol, dataset_dir, water_value
    # 判断不在水体内则继续
    data_value = cu.get_raster_int_value(dataset_ol, xoff, yoff)
    if data_value != water_value:
        # 判断是否流向原中心点
        dir_data_value = cu.get_raster_int_value(dataset_dir, xoff, yoff)
        to_point = cu.get_to_point(xoff, yoff, dir_data_value)
        # 若流向中心点
        if to_point[0] == o_xoff and to_point[1] == o_yoff:
            # 标记坡面id
            cu.set_raster_int_value(dataset_ol, xoff, yoff, slope_surface_id)
            # 若在水体的外边界上则记录为外边界上的上游入流点
            if [xoff, yoff] in water_buf:
                upstream_inflow.append([xoff, yoff])
            # 继续遍历相邻像元
            slope_surface_search(xoff, yoff, slope_surface_id, water_buf, upstream_inflow)


# 遍历边界线构建坡面：边界点x索引 边界点y索引 坡面id
def slope_surface_search(xoff, yoff, slope_surface_id, water_buf, upstream_inflow):
    global dataset_dir
    ol_dir_array = cu.get_8_dir(xoff, yoff)
    for index in range(0, 8, 1):
        n_xoff = ol_dir_array[index][0]
        n_yoff = ol_dir_array[index][1]
        judge_in_data = cu.in_data(n_xoff, n_yoff, dataset_dir.RasterXSize, dataset_dir.RasterYSize)
        # 判断像元是否在数据集内且是否为有效流向
        dir_data_value = cu.get_raster_int_value(dataset_dir, n_xoff, n_yoff)
        to_point = cu.get_to_point(n_xoff, n_yoff, dir_data_value)
        if judge_in_data and len(to_point) != 0:
            extract_slope_surface(xoff, yoff, n_xoff, n_yoff, slope_surface_id, water_buf, upstream_inflow)


# 获取与某入流点相邻的水体外边界上游的未被记录坡面合并的入流点集：x索引 y索引 某水外边界上游入流点的集合 如函数描述(返回值)
def get_new_slope_surface(xoff, yoff, upstream_inflow, inflow_points):
    global dataset_acc, river_th, dataset_ol
    # 初始化搜索数组
    search_array = [[xoff, yoff]]
    # 若继续搜索
    while len(search_array) > 0:
        cell_xy = search_array.pop()
        neighbor_points = cu.get_8_dir(cell_xy[0], cell_xy[1])
        # 遍历周边点
        for points in neighbor_points:
            judge_in_data = cu.in_data(points[0], points[1], dataset_ol.RasterXSize, dataset_ol.RasterYSize)
            if judge_in_data:
                # 若该点为水体入流点且未记录合并
                if points in upstream_inflow and points not in inflow_points:
                    # 判断两点间是否穿插河道
                    # 两点若不存在中间点
                    if points[0] == cell_xy[0] or points[1] == cell_xy[1]:
                        no_river = 1
                    else:
                        # 判断中间点是否为河道
                        between_data_value1 = cu.get_raster_int_value(dataset_acc, cell_xy[0], points[1])
                        between_data_value2 = cu.get_raster_int_value(dataset_acc, points[0], cell_xy[1])
                        no_river = between_data_value1 < river_th and between_data_value2 < river_th
                    # 若未穿插河道
                    if no_river:
                        # 记录到当前坡面入流点集
                        inflow_points.append(points)
                        # 以此点继续遍历
                        search_array.append(points)
    return inflow_points


# 获取需要更新的坡面像元：x索引 y索引 需要更新的id 需要更新的像元的集合
def get_neighbor_update_points(x, y, old_id, to_update_points):
    global dataset_ol
    # 获取邻近像元
    neighbor_points = cu.get_8_dir(x, y)
    # 判断各像元是否需要更新
    for point in neighbor_points:
        point_x = point[0]
        point_y = point[1]
        judge_in_data = cu.in_data(point_x, point_y, dataset_ol.RasterXSize, dataset_ol.RasterYSize)
        if judge_in_data:
            data_value = cu.get_raster_int_value(dataset_ol, point_x, point_y)
            # 若需要则加入待更新数组
            if data_value == old_id:
                to_update_points.append(point)
    return to_update_points


# 判断是否为水体流出点：x索引 y索引 判断结果(返回值)
def judge_from_water(xoff, yoff):
    global dataset_dir, dataset_ol, water_value
    neighbor_points = cu.get_8_dir(xoff, yoff)
    for point in neighbor_points:
        dir_value = cu.get_raster_int_value(dataset_dir, point[0], point[1])
        to_point = cu.get_to_point(point[0], point[1], dir_value)
        ol_value = cu.get_raster_int_value(dataset_ol, point[0], point[1])
        if ol_value == water_value and to_point[0] == xoff and to_point[1] == yoff:
            return 1
    return 0


# 合并相邻坡面：某水体的上游外边界
def surface_merge(upstream_inflow):
    global dataset_ol, dataset_dir, water_buffer_value
    # 定义合并后的坡面分组
    slope_surface_unit = []
    # 定义合并坡面的id集
    slope_surface_ids = []
    # 遍历上游流入点对坡面与水体相交处的入流口分组
    for upstream_point in upstream_inflow:
        # 判断坡面入流点已参与合并
        not_in_unit = 1
        for index in range(0, len(slope_surface_unit), 1):
            if upstream_point in slope_surface_unit[index]:
                not_in_unit = 0
                break
        # 若坡面入流点未参与合并
        if not_in_unit:
            # 获取新坡面集合的id
            slope_surface_id = cu.get_raster_int_value(dataset_ol, upstream_point[0], upstream_point[1])
            # 记录新的坡面id
            slope_surface_ids.append(slope_surface_id)
            # 创建新坡面集合并添加新坡面的首个水体入流点
            slope_surface = [upstream_point]
            # 获取新坡面集合的入流点集
            slope_surface = get_new_slope_surface(upstream_point[0], upstream_point[1], upstream_inflow, slope_surface)
            # 将新坡面放入合并后的坡面集合中
            slope_surface_unit.append(slope_surface)

    # 以各合并坡面的入口点集开始合并坡面
    # print(slope_surface_ids)
    for index in range(0, len(slope_surface_unit), 1):
        # print(slope_surface_unit[index])
        # 获取合并后新坡面的id
        new_slope_surface_id = slope_surface_ids[index]
        # 获取合并后新坡面与水体的交界点
        slope_surface_inflows = slope_surface_unit[index]
        for inflow_point in slope_surface_inflows:
            old_slope_surface_id = cu.get_raster_int_value(dataset_ol, inflow_point[0], inflow_point[1])
            # 若坡面id需要更新
            if old_slope_surface_id != new_slope_surface_id:
                # 获取需要更新的像元集
                to_update_points = [inflow_point]
                # 循环直到待更新数组为空
                while len(to_update_points) > 0:
                    # 取出第一个点
                    to_update_point = to_update_points.pop()
                    # 更新此点id
                    cu.set_raster_int_value(dataset_ol, to_update_point[0], to_update_point[1], new_slope_surface_id)
                    # 获取此点周边需要更新的像元集
                    to_update_points = get_neighbor_update_points(to_update_point[0], to_update_point[1], old_slope_surface_id, to_update_points)


# 获取坡面的入口函数：某水体外边界像元集 起始坡面id 某水体外边界上游入流像元集 使用的id最大值(返回值)
def slope_surface_extract(water_buf, current_id, upstream_inflows):
    global dataset_ol, dataset_dir, dataset_acc, water_buffer_value, river_th
    # 定义非河道出入流处的外边界点集
    upstream_inflow = []

    # 遍历水体的外边线更新由边界线直接流入水体的部分
    for x_y_couple in water_buf:
        xoff = x_y_couple[0]
        yoff = x_y_couple[1]
        # 判断是否为边界上的非河道出入流处且未被标记
        ol_data_value = cu.get_raster_int_value(dataset_ol, xoff, yoff)
        acc_data_value = cu.get_raster_float_value(dataset_acc, xoff, yoff)
        not_is_channel = ol_data_value == water_buffer_value and acc_data_value < river_th
        # 若为非河道出入流处
        if not_is_channel:
            # 判断是否指向水体
            to_point_data = get_to_point_ol_data(xoff, yoff)
            judge_to_water = to_point_data == water_value
            # 若流向水体
            if judge_to_water:
                current_id = current_id + 1
                # 记录为水体外边界上的直接入流点
                upstream_inflow.append(x_y_couple)
                # 外边界点标记坡面id
                cu.set_raster_int_value(dataset_ol, xoff, yoff, current_id)
                slope_surface_search(xoff, yoff, current_id, water_buf, upstream_inflow)

    upstream_inflows.append(upstream_inflow)

    # 返回使用的id最大值
    return current_id


# 3*3网格遍历：水体数据的x索引 水体数据的y索引 此水体外边界数组
def buffer_search(o_res_xoff, o_res_yoff, water_ol_buf):
    global dataset_res, dataset_acc, dataset_ol, river_th, water_channel, no_data_value
    # 存储需要遍历的水体像元
    water_points = [[o_res_xoff, o_res_yoff]]
    # 循环方式遍历水体像元
    while len(water_points) > 0:
        current_point = water_points.pop()
        res_dir_array = cu.get_8_dir(current_point[0], current_point[1])
        for index in range(0, 8, 1):
            # 水体数据中的索引
            res_xoff = res_dir_array[index][0]
            res_yoff = res_dir_array[index][1]
            # 结果数据的该点索引
            ol_point_off = cu.off_transform(res_xoff, res_yoff, dataset_res, dataset_ol)
            re_xoff = ol_point_off[0]
            re_yoff = ol_point_off[1]

            # 若在数据内
            if cu.in_data(re_xoff, re_yoff, dataset_ol.RasterXSize, dataset_ol.RasterYSize):
                # 判断是否已经在破面数据记录
                ol_data_value = cu.get_raster_int_value(dataset_ol, re_xoff, re_yoff)
                not_recode_result = ol_data_value == no_data_value
                # 判断是否在水体数据范围内
                in_water_data = cu.in_data(res_xoff, res_yoff, dataset_res.RasterXSize, dataset_res.RasterYSize)
                # 若在水体数据中进一步判断是否为水体内像元
                if in_water_data:
                    data_value = cu.get_raster_int_value(dataset_res, res_xoff, res_yoff)
                    not_in_water = data_value != water_value
                else:
                    not_in_water = True
                # 若不是水体像元且未记录则记录，即记录新边界点
                if not_recode_result and not_in_water:
                    # 添加缓冲区数组记录
                    water_ol_buf.append([re_xoff, re_yoff])
                    # 标记为水体外边界
                    cu.set_raster_int_value(dataset_ol, re_xoff, re_yoff, water_buffer_value)
                # 若是水体且未记录，则继续搜索
                if not_recode_result and not not_in_water:
                    cu.set_raster_int_value(dataset_ol, re_xoff, re_yoff, water_value)
                    water_points.append([res_xoff, res_yoff])


# 提取坡面流路
def get_surface_route(surface_route_start):
    global dataset_acc, dataset_dir, dataset_ro, dataset_ol, water_value, river_th, surface_route_value
    # 提取各水体的坡面流路
    for route_start_point in surface_route_start:
        # 初始化流路追踪数组
        judge_route = [route_start_point]
        while len(judge_route) > 0:
            current_point = judge_route.pop()
            xoff = current_point[0]
            yoff = current_point[1]
            # 获取此点其汇流累积量
            acc_value = cu.get_raster_float_value(dataset_acc, xoff, yoff)
            # 获取此点在结果数据的值
            ol_value = cu.get_raster_int_value(dataset_ol, xoff, yoff)
            # 若流向的点不为水体且不为河道则继续
            if ol_value != water_value and acc_value < river_th:
                # 记录此点为坡面流路
                cu.set_raster_int_value(dataset_ro, xoff, yoff, surface_route_value)
            # 获取此点流向
            dir_value = cu.get_raster_int_value(dataset_dir, xoff, yoff)
            # 获取其流向的点
            to_point = cu.get_to_point(xoff, yoff, dir_value)
            if len(to_point) > 0:
                # 加入判断数组
                judge_route.append(to_point)


# 清除边界线标记：某水体的外边界
def clear_buffer(water_buf):
    global water_buffer_value, no_data_value, dataset_ol
    for cell in water_buf:
        data_value = cu.get_raster_int_value(dataset_ol, cell[0], cell[1])
        if data_value == water_buffer_value:
            cu.set_raster_int_value(dataset_ol, cell[0], cell[1], no_data_value)


# 参数分别为：工作空间 水体数据 流向数据 汇流累积量数据
def get_slope_surface(work_path, res_data_path, dir_data_path, acc_data_path, river_threshold):
    print("Extract Start")
    global dataset_res, dataset_dir, dataset_acc, dataset_ol, dataset_ro, river_th, water_ol_bufs
    river_th = river_threshold

    if not os.path.exists(work_path):
        os.makedirs(work_path)

    dataset_res = gdal.Open(res_data_path)
    dataset_dir = gdal.Open(dir_data_path)
    dataset_acc = gdal.Open(acc_data_path)

    dir_geotransform = dataset_dir.GetGeoTransform()

    full_geotransform = dir_geotransform

    # 创建坡面提取结果数据
    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    result_data_path = work_path + "/water_slope_surface.tif"
    dataset_ol = driver.Create(result_data_path, dataset_dir.RasterXSize, dataset_dir.RasterYSize, 1, gdal.GDT_Int32)
    dataset_ol.SetGeoTransform(full_geotransform)
    dataset_ol.SetProjection(dataset_dir.GetProjection())
    dataset_ol.GetRasterBand(1).SetNoDataValue(no_data_value)

    # 创建坡面流路结果数据
    route_data_path = work_path + "/slope_surface_route.tif"
    dataset_ro = driver.Create(route_data_path, dataset_dir.RasterXSize, dataset_dir.RasterYSize, 1, gdal.GDT_Int16)
    dataset_ro.SetGeoTransform(full_geotransform)
    dataset_ro.SetProjection(dataset_dir.GetProjection())
    dataset_ro.GetRasterBand(1).SetNoDataValue(no_data_value)

    print("Get lakes' outline...")
    for i in range(dataset_res.RasterYSize):
        for j in range(dataset_res.RasterXSize):
            # 获取水体数据某点的值
            scan_value = cu.get_raster_int_value(dataset_res, j, i)

            # 若是水体内的像元
            if scan_value == water_value:
                # 计算水体数据的x,y坐标
                off_point = cu.off_transform(j, i, dataset_res, dataset_ol)
                re_xoff = off_point[0]
                re_yoff = off_point[1]
                # 若在数据集内
                if cu.in_data(re_xoff, re_yoff, dataset_ol.RasterXSize, dataset_ol.RasterYSize):
                    # 获取结果数据的值
                    re_data_value = cu.get_raster_int_value(dataset_ol, re_xoff, re_yoff)
                    # 若未记录则继续

                    if re_data_value != water_value:
                        # 新建数组用于记录此水体外边界
                        water_ol_buf = []
                        # 结果数据记录水体
                        cu.set_raster_int_value(dataset_ol, re_xoff, re_yoff, water_value)
                        # 使用3*3区域生成水体外包围像元集
                        buffer_search(j, i, water_ol_buf)

                        # 若有新的水体外边界则记录到集合
                        if len(water_ol_buf) > 0:
                            # 将此水体的外边界记录到集合中
                            water_ol_bufs.append(water_ol_buf)

    print("Order lakes' slope surface...")
    # 对水体的坡面提取排序
    water_ol_bufs_ordered = []
    surface_route_start = water_order(water_ol_bufs, water_ol_bufs_ordered)

    print("Get slope surface...")
    # 沿水体外边界直接非河道入流点提取坡面
    # 坡面id初始化
    start_id = 0
    # 上游流入点的集合
    upstream_inflows = []
    for water_ol_buf in water_ol_bufs_ordered:
        start_id = slope_surface_extract(water_ol_buf, start_id, upstream_inflows)

    print("Union lakes' slope surface...")
    # 合并坡面入流口相邻的坡面
    for upstream_inflow in upstream_inflows:
        surface_merge(upstream_inflow)

    print("Get slope surface route...")
    # 提取坡面流路
    get_surface_route(surface_route_start)

    print("Clear marks...")
    # 清除边界线标记
    for water_ol_buf in water_ol_bufs_ordered:
        clear_buffer(water_ol_buf)

    dataset_res = None
    dataset_dir = None
    dataset_acc = None
    dataset_ol = None
    dataset_ro = None
    print("Extract End")


# 提取结果为坡面和湖泊/水库的tif数据以及坡面流路的tif数据
if __name__ == '__main__':
    start = time.perf_counter()
    # base_path = "D:/Graduation/Program/Data/3"
    # base_path = "D:/Graduation/Program/Data/8/process"
    base_path = "D:/Graduation/Program/Data/15/process"
    workspace_path = base_path + "/result"
    # get_slope_surface(workspace_path, base_path + "/tashan_99.tif", base_path + "/dir.tif", base_path + "/acc.tif", 300000)
    get_slope_surface(workspace_path, base_path + "/water_revised.tif", base_path + "/dir.tif", base_path + "/acc.tif", 300000)
    # for array in water_ol_bufs:
    #     print(array)
    end = time.perf_counter()
    print('Run', end - start, 's')
