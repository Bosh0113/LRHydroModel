# coding=utf-8
import time
import common_utils as cu
import json
import gdal


# 从GeoJSON数据中获取多边形点集: GeoJSON路径
def get_polygon_points(geojson_path):
    polygons_array = []
    # Creates a MultiPolygon from Geojson
    with open(geojson_path) as f:
        js = json.load(f)
        FeatureObj = None
        if js['type'] == 'FeatureCollection':
            FeatureObj = js['features'][0]
        elif js['type'] == 'Feature':
            FeatureObj = js
        if FeatureObj['geometry']['type'] == 'MultiPolygon':
            polygons = FeatureObj['geometry']['coordinates']
            for polygon in polygons:
                polygon_points = []
                for point in polygon[0]:
                    polygon_points.append(point)
                polygons_array.append(polygon_points)
        elif FeatureObj['geometry']['type'] == 'Polygon':
            polygon = FeatureObj['geometry']['coordinates']
            points = polygon[0]
            polygon_points = []
            for point in points:
                polygon_points.append(point)
            polygons_array.append(polygon_points)
    return polygons_array


# 判断点集顺序(Green方法): 点集 判断结果(返回，-1逆时针/1顺时针)
def is_clockwise(points):
    d = 0
    for i in range(len(points) - 1):
        x_i1 = points[i+1][0]
        y_i1 = points[i+1][1]
        x_i = points[i][0]
        y_i = points[i][1]
        d += -0.5*(y_i1 + y_i)*(x_i1-x_i)
    if d > 0:
        return 0
    else:
        return 1


# 获取多边形边缘栅格点对应点集: 多边形顶点对应栅格数据的索引集合 多边形边界上对应栅格数据的索引集合(返回)
def raster_index_on_polygon(polygon_pts_index):
    polygon_ras_indexes = []
    for i in range(len(polygon_pts_index) - 1):
        current_point = polygon_pts_index[i]
        if i == 0:
            polygon_ras_indexes.append(current_point)
        next_point = polygon_pts_index[i + 1]
        # 若在同一y轴
        if current_point[1] == next_point[1]:
            # 求x轴距离差
            diff = next_point[0] - current_point[0]
            # 得到相隔像元数
            count = int(diff / 1)
            for x_i in range(1, abs(count)):
                polygon_ras_indexes.append([current_point[0] + x_i * int(count/abs(count)), current_point[1]])
            polygon_ras_indexes.append(next_point)
        # 若在同一x轴
        elif current_point[0] == next_point[0]:
            # 求y轴距离差
            diff = next_point[1] - current_point[1]
            # 得到相隔像元数
            count = int(diff / 1)
            for y_i in range(1, abs(count)):
                polygon_ras_indexes.append([current_point[0], current_point[1] + y_i * int(count/abs(count))])
            polygon_ras_indexes.append(next_point)
        else:
            polygon_ras_indexes.append(next_point)

    return polygon_ras_indexes


# 判断第二个点在第一个点的方位(栅格索引): 第一个点 第二个点 方向标识(返回，上右下左：1234)
def second_point_orientation(point_f, point_s):
    f_x = point_f[0]
    f_y = point_f[1]
    s_x = point_s[0]
    s_y = point_s[1]
    # 上
    if f_x == s_x and f_y > s_y:
        return 1
    # 右
    elif f_x < s_x and f_y == s_y:
        return 2
    # 下
    elif f_x == s_x and f_y < s_y:
        return 3
    # 左
    elif f_x > s_x and f_y == s_y:
        return 4
    return 0


# 根据连续三个点获得中间点所关联的栅格像元索引: 第一个点索引 第二个点索引 第三个点索引 栅格像元索引数组(返回)
def get_inner_boundary_raster_index(last_i, current_i, next_i):

    raster_indexes = []
    x_2 = current_i[0]
    y_2 = current_i[1]

    # 三点关系参照文档/论文中关系表
    # 上上
    if second_point_orientation(last_i, current_i) == 1 and second_point_orientation(current_i, next_i) == 1:
        raster_indexes.append([x_2, y_2 - 1])
    # 上右
    elif second_point_orientation(last_i, current_i) == 1 and second_point_orientation(current_i, next_i) == 2:
        pass
    # 上左
    elif second_point_orientation(last_i, current_i) == 1 and second_point_orientation(current_i, next_i) == 4:
        raster_indexes.append([x_2, y_2 - 1])
        raster_indexes.append([x_2 - 1, y_2 - 1])
    # 右上
    elif second_point_orientation(last_i, current_i) == 2 and second_point_orientation(current_i, next_i) == 1:
        raster_indexes.append([x_2, y_2])
        raster_indexes.append([x_2, y_2 - 1])
    # 右右
    elif second_point_orientation(last_i, current_i) == 2 and second_point_orientation(current_i, next_i) == 2:
        raster_indexes.append([x_2, y_2])
    # 右下
    elif second_point_orientation(last_i, current_i) == 2 and second_point_orientation(current_i, next_i) == 3:
        pass
    # 下右
    elif second_point_orientation(last_i, current_i) == 3 and second_point_orientation(current_i, next_i) == 2:
        raster_indexes.append([x_2 - 1, y_2])
        raster_indexes.append([x_2, y_2])
    # 下下
    elif second_point_orientation(last_i, current_i) == 3 and second_point_orientation(current_i, next_i) == 3:
        raster_indexes.append([x_2 - 1, y_2])
    # 下左
    elif second_point_orientation(last_i, current_i) == 3 and second_point_orientation(current_i, next_i) == 4:
        pass
    # 左上
    elif second_point_orientation(last_i, current_i) == 4 and second_point_orientation(current_i, next_i) == 1:
        pass
    # 左下
    elif second_point_orientation(last_i, current_i) == 4 and second_point_orientation(current_i, next_i) == 3:
        raster_indexes.append([x_2 - 1, y_2 - 1])
        raster_indexes.append([x_2 - 1, y_2])
    # 左左
    elif second_point_orientation(last_i, current_i) == 4 and second_point_orientation(current_i, next_i) == 4:
        raster_indexes.append([x_2 - 1, y_2 - 1])
    return raster_indexes


# 计算多边形内部边缘栅格点左上角索引: 多边形边界上对应栅格数据的索引集合 多边形内部边缘栅格点左上角索引集合(返回)
def inner_boundary_raster_indexes(polygon_ras_indexes):
    inner_ras_indexes = []
    for i in range(1, len(polygon_ras_indexes) - 1):
        last_index = polygon_ras_indexes[i - 1]
        current_index = polygon_ras_indexes[i]
        next_index = polygon_ras_indexes[i + 1]
        i_r_indexes = get_inner_boundary_raster_index(last_index, current_index, next_index)
        for inner_ras_index in i_r_indexes:
            inner_ras_indexes.append(inner_ras_index)
    i_r_indexes = get_inner_boundary_raster_index(polygon_ras_indexes[len(polygon_ras_indexes) - 2], polygon_ras_indexes[0], polygon_ras_indexes[1])
    for inner_ras_index in i_r_indexes:
        inner_ras_indexes.append(inner_ras_index)

    return inner_ras_indexes


# 得到流域集合边界上最佳出口栅格索引数组: 多边形内边界像元索引数组 流域出口数据DataSet 最佳排序的流域出口索引数组(返回)
def outlets_index_order(boundary_array, outlet_ds):
    outlet_order = []
    # 得到流域集合边界上出口栅格和其在多边形内边界上的追踪序号
    # 初始化记录出口点及其与前者出口点在追踪给数组中相差距离的数组
    record_distance = []
    # 初始化记录与前者出口点在追踪给数组中相差距离
    distance = 0
    for index in boundary_array:
        distance += 1
        # 获得此索引在出口点数据中的值
        trace_value = cu.get_raster_int_value(outlet_ds, index[0], index[1])
        # 若为出口点则记录
        if trace_value > 0:
            record_distance.append([index, distance])
            distance = 0
    # 更新第一个记录的点与前者间的距离
    record_distance[0][1] = record_distance[0][1] + distance

    # 根据得到的序号得到流域出口的最佳排序
    # 与前者距离最大的值
    max_distance_index = 0
    # 与前者距离最大的出口点在出口数组中的索引
    max_dis_index_mark = 0
    for i in range(len(record_distance)):
        distance = record_distance[i][1]
        if distance > max_distance_index:
            max_distance_index = distance
            max_dis_index_mark = i

    # 以标记的位置为起点记录出口点
    for i in range(max_dis_index_mark, len(record_distance)):
        outlet_order.append(record_distance[i][0])
    for i in range(0, max_dis_index_mark):
        outlet_order.append(record_distance[i][0])

    return outlet_order


# 对沿海流域集合进行次级流域分组
def basin_divide(work_space, boundary_geoj, trace_tif):
    polygons_points = get_polygon_points(boundary_geoj)
    if len(polygons_points) == 1:
        trace_ds = gdal.Open(trace_tif)
        polygon_pts = polygons_points[0]

        p_clockwise = is_clockwise(polygon_pts)
        # 边界为顺时针多边形
        if p_clockwise:
            # 获取多边形顶点在栅格数据中的索引
            p_offs = []
            for point in polygon_pts:
                p_offs.append(cu.coord_to_off(point, trace_ds))
            # 获取多边形其边对应的所有栅格索引的集合
            polygon_ras_indexes = raster_index_on_polygon(p_offs)
            # 得到多边形边界内部邻接栅格像元的索引
            inner_ras_indexes = inner_boundary_raster_indexes(polygon_ras_indexes)
            # 得到流域集合边界上出口栅格顺时针编号
            outlets_order = outlets_index_order(inner_ras_indexes, trace_ds)

            print("---------------------------------------")
            for point in outlets_order:
                print(point)

            # file_format = "GTiff"
            # driver = gdal.GetDriverByName(file_format)
            # temp_path = work_space + "/temp2.tif"
            # temp_ds = driver.Create(temp_path, trace_ds.RasterXSize, trace_ds.RasterYSize, 1, gdal.GDT_Int16, options=['COMPRESS=DEFLATE'])
            # temp_ds.SetGeoTransform(trace_ds.GetGeoTransform())
            # temp_ds.SetProjection(trace_ds.GetProjection())
            # temp_ds.GetRasterBand(1).SetNoDataValue(-1)
            #
            # for i in range(len(outlets_order)):
            #     xy_off = outlets_order[i]
            #     x_off = xy_off[0]
            #     y_off = xy_off[1]
            #     if cu.in_data(x_off, y_off, temp_ds.RasterXSize, temp_ds.RasterYSize):
            #         cu.set_raster_int_value(temp_ds, x_off, y_off, i)

        trace_ds = None
        temp_ds = None
    else:
        print('error!')


if __name__ == '__main__':
    start = time.perf_counter()
    workspace = r"G:\Graduation\Program\Data\40\order_outlet"
    # boundary_shp = workspace + '/data/test_boundary.shp'
    boundary_geoj = workspace + '/data/test_boundary.geojson'
    # cu.shp_to_geojson(boundary_shp, boundary_geoj)

    outlet_path = workspace + "/data/trace.tif"
    basin_divide(workspace, boundary_geoj, outlet_path)
    end = time.perf_counter()
    print('Run', end - start, 's')