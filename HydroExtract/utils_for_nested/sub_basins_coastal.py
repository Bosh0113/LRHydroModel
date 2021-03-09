# coding=utf-8
import time
import common_utils as cu
import gdal
import heapq
import sub_basins_utils as sbu


# 得到流域集合边界上最佳出口栅格索引数组: 多边形内边界像元索引数组 流域出口数据DataSet 最佳排序的流域出口索引数组(返回)
def outlets_index_order(boundary_array, outlet_ds):
    outlet_order = []
    # 得到流域集合边界上出口栅格和其在多边形内边界上的追踪序号
    # 初始化记录出口点及其与前者出口点在追踪给数组中相差距离的数组
    record_distance = {}
    # 初始化记录与前者出口点在追踪给数组中相差距离
    distance = 0
    for index in boundary_array:
        distance += 1
        # 获得此索引在出口点数据中的值
        trace_value = cu.get_raster_int_value(outlet_ds, index[0], index[1])
        # 若为出口点则记录
        if trace_value > 0:
            key = ','.join(str(k) for k in index)
            record_distance[key] = distance
            distance = 0
    # 更新第一个记录的点与前者间的距离
    key_f = [key for key in record_distance.keys()][0]
    value_f = [value for value in record_distance.values()][0]
    record_distance[key_f] = value_f + distance

    # 根据得到的序号得到流域出口的最佳排序
    # 与前者距离最大的值
    max_distance_index = 0
    # 与前者距离最大的出口点在出口数组中的索引
    max_dis_index_mark = 0
    # 得到距离数组
    distance_array = [value for value in record_distance.values()]
    for i in range(len(distance_array)):
        distance = distance_array[i]
        if distance > max_distance_index:
            max_distance_index = distance
            max_dis_index_mark = i

    # 出口点集
    outlet_set = []
    point_off_str = [key for key in record_distance.keys()]
    for point_str in point_off_str:
        point_temp = point_str.split(',')
        point = [int(point_temp[0]), int(point_temp[1])]
        outlet_set.append(point)
    # 以标记的位置为起点记录出口点
    for i in range(max_dis_index_mark, len(outlet_set)):
        outlet_order.append(outlet_set[i])
    for i in range(0, max_dis_index_mark):
        outlet_order.append(outlet_set[i])

    return outlet_order


# 以四个大流域为界将流域出口分组: 排好序的流域出水口集合 汇流累积量数据DataSet 分组后的出水口集合(返回)
def divide_outlet_to_group(outlets_order, acc_ds):
    acc_array = []
    # 获得所有出口点的acc值
    for outlet in outlets_order:
        acc_value = cu.get_raster_float_value(acc_ds, outlet[0], outlet[1])
        acc_array.append(acc_value)
    # 得到最大4个acc值所对应的数组索引
    max_4_index = list(map(acc_array.index, heapq.nlargest(4, acc_array)))
    # 对4大acc对应索引从小到大排序
    max_4_index.sort()
    print(max_4_index)
    # 根据四大流域对夹杂的中间子流域分组
    odd_1 = outlets_order[0:max_4_index[0]]
    even_2 = [outlets_order[max_4_index[0]]]
    odd_3 = outlets_order[max_4_index[0] + 1:max_4_index[1]]
    even_4 = [outlets_order[max_4_index[1]]]
    odd_5 = outlets_order[max_4_index[1] + 1:max_4_index[2]]
    even_6 = [outlets_order[max_4_index[2]]]
    odd_7 = outlets_order[max_4_index[2] + 1:max_4_index[3]]
    even_8 = [outlets_order[max_4_index[3]]]
    odd_9 = outlets_order[max_4_index[3] + 1:]
    return [odd_1, even_2, odd_3, even_4, odd_5, even_6, odd_7, even_8, odd_9]


# 根据流域出水口追踪子流域: 出水口索引 结果数据DataSet 流域编号 流向数据DataSet
def outlet_basins(outlet, result_ds, s_id, dir_ds):
    # 创建追踪数组
    trace_array = [outlet]
    # 若需要继续追踪
    while len(trace_array) > 0:
        # 取出当前像元
        cur_cell = trace_array.pop()
        cur_x = cur_cell[0]
        cur_y = cur_cell[1]
        # 对当前像元赋值
        cu.set_raster_int_value(result_ds, cur_x, cur_y, s_id)
        # 获取周边像元索引
        n_8_cells = cu.get_8_dir(cur_x, cur_y)
        # 遍历8个像元
        for n_cell in n_8_cells:
            n_x = n_cell[0]
            n_y = n_cell[1]
            # 若在数据范围内
            if cu.in_data(n_x, n_y, dir_ds.RasterXSize, dir_ds.RasterYSize):
                # 获得当前点流向值
                dir_value = cu.get_raster_int_value(dir_ds, n_x, n_y)
                # 获得下游点索引
                to_point = cu.get_to_point_128(n_x, n_y, dir_value)
                # 若为当前点的上游点
                if to_point == cur_cell:
                    # 将此像元加入到流域追踪数组
                    trace_array.append(n_cell)


# 对沿海流域集合进行次级流域分组: 次级流域划分结果路径 原流域边界GeoJSON 流域集的出水口数据路径 汇流累积量数据路径 流向数据路径
def basin_divide(sub_basins_tif, boundary_geoj, trace_tif, acc_tif, dir_tif):
    # 获得多边形边界信息
    polygons_array = sbu.get_polygon_points(boundary_geoj)
    # 找到主要边界所在多边形
    main_polygon, main_index = sbu.get_main_polygon(polygons_array)
    # 判断是否需要更新岛到边界
    if main_index['no_island'] == 1:
        polygon_pts = main_polygon
    else:
        # 更新岛到主要外边界
        polygon_pts = sbu.update_island2boundary(polygons_array[main_index['polygon_index']])

    trace_ds = gdal.Open(trace_tif)
    acc_ds = gdal.Open(acc_tif)
    dir_ds = gdal.Open(dir_tif)

    p_clockwise = sbu.is_clockwise(polygon_pts)
    # 边界为顺时针多边形
    if p_clockwise:
        # 获取多边形顶点在栅格数据中的索引
        p_offs = []
        for point in polygon_pts:
            p_offs.append(cu.coord_to_off(point, trace_ds))
        # 获取多边形其边对应的所有栅格索引的集合
        polygon_ras_indexes = sbu.raster_index_on_polygon(p_offs)

        # 更新边界外部多边形内像元到内边界栅格集内
        # 记录多个多边形连接处索引
        joint_offs = []
        if len(polygons_array) > 1:
            polygon_ras_indexes, joint_offs = sbu.update_outer2polygons(polygon_ras_indexes, trace_ds, polygons_array, main_index['polygon_index'])

        # 得到多边形边界内部邻接栅格像元的索引
        inner_ras_indexes = sbu.inner_boundary_raster_indexes(polygon_ras_indexes, joint_offs)

        # # 输出到tif
        # temp_path = r'G:\Graduation\Program\Data\51\nested\5\56\566\process\boundary.tif'
        # file_format = "GTiff"
        # driver = gdal.GetDriverByName(file_format)
        # temp_ds = driver.Create(temp_path, trace_ds.RasterXSize, trace_ds.RasterYSize, 1, gdal.GDT_Float32, options=['COMPRESS=DEFLATE'])
        # temp_ds.SetGeoTransform(trace_ds.GetGeoTransform())
        # temp_ds.SetProjection(trace_ds.GetProjection())
        # temp_ds.GetRasterBand(1).SetNoDataValue(-1)
        # for off_index in range(len(inner_ras_indexes)):
        #     off = inner_ras_indexes[off_index]
        #     cu.set_raster_float_value(temp_ds, off[0], off[1], off_index*0.001)
        # temp_ds = None

        # 得到流域集合边界上出口栅格顺时针编号
        outlets_order = outlets_index_order(inner_ras_indexes, trace_ds)
        # 以四个大流域为界将流域出口分组
        outlet_groups = divide_outlet_to_group(outlets_order, acc_ds)

        file_format = "GTiff"
        driver = gdal.GetDriverByName(file_format)
        sub_ds = driver.Create(sub_basins_tif, trace_ds.RasterXSize, trace_ds.RasterYSize, 1, gdal.GDT_Int16, options=['COMPRESS=DEFLATE'])
        sub_ds.SetGeoTransform(trace_ds.GetGeoTransform())
        sub_ds.SetProjection(trace_ds.GetProjection())
        sub_ds.GetRasterBand(1).SetNoDataValue(-1)

        for i in range(len(outlet_groups)):
            outlet_group = outlet_groups[i]
            for outlet in outlet_group:
                x_off = outlet[0]
                y_off = outlet[1]
                if cu.in_data(x_off, y_off, sub_ds.RasterXSize, sub_ds.RasterYSize):
                    outlet_basins(outlet, sub_ds, i + 1, dir_ds)
    else:
        print('No support anticlockwise!')

    trace_ds = None
    sub_ds = None
    acc_ds = None
    dir_ds = None


if __name__ == '__main__':
    start = time.perf_counter()
    workspace = r"G:\Graduation\Program\Data\51\nested\5\56\566"
    boundary_geoj_path = workspace + '\\process\\566_land.geojson'

    data_path = workspace + '\\data'
    outlet_path = data_path + "\\566_trace_starts.tif"
    acc_path = data_path + "\\566_acc.tif"
    dir_path = workspace + "\\data\\566_dir.tif"
    sub_basins_path = workspace + "\\process\\566_sub_basins_test.tif"
    basin_divide(sub_basins_path, boundary_geoj_path, outlet_path, acc_path, dir_path)
    end = time.perf_counter()
    print('Run', end - start, 's')
