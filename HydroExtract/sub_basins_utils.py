import json
import common_utils as cu


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
                polygon_array = []
                for polygon_item in polygon:
                    polygon_points = []
                    for point in polygon_item:
                        polygon_points.append(point)
                    polygon_array.append(polygon_points)
                polygons_array.append(polygon_array)
        elif FeatureObj['geometry']['type'] == 'Polygon':
            polygon = FeatureObj['geometry']['coordinates']
            polygon_array = []
            for polygon_item in polygon:
                polygon_points = []
                for point in polygon_item:
                    polygon_points.append(point)
                polygon_array.append(polygon_points)
            polygons_array.append(polygon_array)
    return polygons_array


# 找到主要多边形边界: 多边形数组 主要多边形外边界(返回) 主要多边形所在数组索引(返回)
def get_main_polygon(polygons_array):
    # 记录主要多边形边界
    main_polygon = []

    # 记录主要多边形边界在多边形集合的位置索引和多边形内的位置索引，并给出是否存在岛
    main_index = {
        'polygon_index': 0,
        'item_index': 0,
        'no_island': 1
    }

    # 记录多边形大小
    polygon_size = 0

    for polygon_index in range(len(polygons_array)):
        polygon = polygons_array[polygon_index]
        for item_index in range(len(polygon)):
            polygon_item = polygon[item_index]
            if len(polygon_item) > polygon_size:
                polygon_size = len(polygon_item)
                main_polygon = polygon_item[:]
                main_index['polygon_index'] = polygon_index
                main_index['item_index'] = item_index

    # 判断是否存在岛
    if len(polygons_array[main_index['polygon_index']]) > 1:
        main_index['no_island'] = 0

    return main_polygon, main_index


# 更新流域边界表达: 多边形数组(含岛) 更新后的多边形(返回，合并邻接岛的外边界)
def update_island2boundary(polygon_array):
    old_boundary = polygon_array[0]
    new_boundary = old_boundary[:]
    for index in range(1, len(polygon_array)):
        polygon_item = polygon_array[index][:]
        # 判断岛是否与外边界相邻
        on_point = []
        on_flag = 0
        for point in polygon_item:
            if point in new_boundary:
                on_flag = 1
                on_point = point[:]
        if on_flag:
            # print(len(new_boundary))
            on_index = new_boundary.index(on_point)
            # 貌似只存在一种情况
            polygon_item.remove(on_point)
            polygon_item.reverse()
            for item in polygon_item:
                new_boundary.insert(on_index + 1, item)
            # print(len(new_boundary))

    return new_boundary


# 将主边界外部细碎像元考虑进来: 多边形上对应栅格集的索引集合 索引参考数据集 所有多边形数据 主要多边形的索引 新的索引集合(返回)
def update_outer2polygons(polygon_ras_indexes, refer_ds, polygons_array, main_p_index):
    joint_offs = []
    for polygon_index in range(len(polygons_array)):
        # 遍历其他多边形
        if polygon_index != main_p_index:
            # 得到多边形
            polygon = polygons_array[polygon_index]
            # 若不存在岛
            if len(polygon) == 1:
                polygon = polygon[0]
                # 若为单个像元
                if len(polygon) == 5:
                    temp_list = polygon[:len(polygon) - 1]
                    for index in range(len(temp_list)):
                        polygon_pt = temp_list[index]
                        pt_off = cu.coord_to_off(polygon_pt, refer_ds)
                        # 若相邻
                        if pt_off in polygon_ras_indexes:
                            # 记录相邻点索引
                            joint_offs.append(pt_off)
                            # 获取插入到边界点集的位置
                            in_main_index = polygon_ras_indexes.index(pt_off)
                            # 初始化插入数组
                            join_off = []
                            for n_index in range(index, len(temp_list)):
                                pt = temp_list[n_index]
                                off = cu.coord_to_off(pt, refer_ds)
                                join_off.append(off)
                            for n_index in range(0, index):
                                pt = temp_list[n_index]
                                off = cu.coord_to_off(pt, refer_ds)
                                join_off.append(off)
                            join_off.reverse()
                            for off in join_off:
                                polygon_ras_indexes.insert(in_main_index, off)
                            break
                else:
                    print('暂不支持较大多边形')
            else:
                print('暂不支持含岛多边形')

    return polygon_ras_indexes, joint_offs


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


# 判断第二个点在第一个点的方位(栅格索引): 第一个点 第二个点 方向标识(返回，方向同TauDEM)
def second_point_orientation(point_f, point_s):
    f_x = point_f[0]
    f_y = point_f[1]
    s_x = point_s[0]
    s_y = point_s[1]
    # 右
    if f_x < s_x and f_y == s_y:
        return 1
    # 右上
    if f_x < s_x and f_y > s_y:
        return 2
    # 上
    elif f_x == s_x and f_y > s_y:
        return 3
    # 左上
    elif f_x > s_x and f_y > s_y:
        return 4
    # 左
    elif f_x > s_x and f_y == s_y:
        return 5
    # 左下
    elif f_x > s_x and f_y < s_y:
        return 6
    # 下
    elif f_x == s_x and f_y < s_y:
        return 7
    # 右下
    elif f_x < s_x and f_y < s_y:
        return 8
    return 0


# 根据连续三个点获得中间点所关联的栅格像元索引: 第一个点索引 第二个点索引 第三个点索引 多个多边形连接点索引 栅格像元索引数组(返回)
def get_inner_boundary_raster_index(last_i, current_i, next_i, joint_offs):

    raster_indexes = []
    x_2 = current_i[0]
    y_2 = current_i[1]

    # 三点关系参照文档/论文中关系表
    # 上上
    if second_point_orientation(last_i, current_i) == 3 and second_point_orientation(current_i, next_i) == 3:
        raster_indexes.append([x_2, y_2 - 1])
    # 上右
    elif second_point_orientation(last_i, current_i) == 3 and second_point_orientation(current_i, next_i) == 1:
        pass
    # 上左
    elif second_point_orientation(last_i, current_i) == 3 and second_point_orientation(current_i, next_i) == 5:
        if current_i not in joint_offs:
            raster_indexes.append([x_2, y_2 - 1])
        raster_indexes.append([x_2 - 1, y_2 - 1])
    # 右上
    elif second_point_orientation(last_i, current_i) == 1 and second_point_orientation(current_i, next_i) == 3:
        if current_i not in joint_offs:
            raster_indexes.append([x_2, y_2])
        raster_indexes.append([x_2, y_2 - 1])
    # 右右
    elif second_point_orientation(last_i, current_i) == 1 and second_point_orientation(current_i, next_i) == 1:
        raster_indexes.append([x_2, y_2])
    # 右下
    elif second_point_orientation(last_i, current_i) == 1 and second_point_orientation(current_i, next_i) == 7:
        pass
    # 下右
    elif second_point_orientation(last_i, current_i) == 7 and second_point_orientation(current_i, next_i) == 1:
        if current_i not in joint_offs:
            raster_indexes.append([x_2 - 1, y_2])
        raster_indexes.append([x_2, y_2])
    # 下下
    elif second_point_orientation(last_i, current_i) == 7 and second_point_orientation(current_i, next_i) == 7:
        raster_indexes.append([x_2 - 1, y_2])
    # 下左
    elif second_point_orientation(last_i, current_i) == 7 and second_point_orientation(current_i, next_i) == 5:
        pass
    # 左上
    elif second_point_orientation(last_i, current_i) == 5 and second_point_orientation(current_i, next_i) == 3:
        pass
    # 左下
    elif second_point_orientation(last_i, current_i) == 5 and second_point_orientation(current_i, next_i) == 7:
        if current_i not in joint_offs:
            raster_indexes.append([x_2 - 1, y_2 - 1])
        raster_indexes.append([x_2 - 1, y_2])
    # 左左
    elif second_point_orientation(last_i, current_i) == 5 and second_point_orientation(current_i, next_i) == 5:
        raster_indexes.append([x_2 - 1, y_2 - 1])
    return raster_indexes


# 计算多边形内部边缘栅格点左上角索引: 多边形边界上对应栅格数据的索引集合 多个多边形连接点索引 多边形内部边缘栅格点左上角索引集合(返回)
def inner_boundary_raster_indexes(polygon_ras_indexes, joint_offs):
    inner_ras_indexes = []
    for i in range(1, len(polygon_ras_indexes) - 1):
        last_index = polygon_ras_indexes[i - 1]
        current_index = polygon_ras_indexes[i]
        next_index = polygon_ras_indexes[i + 1]
        i_r_indexes = get_inner_boundary_raster_index(last_index, current_index, next_index, joint_offs)
        for inner_ras_index in i_r_indexes:
            inner_ras_indexes.append(inner_ras_index)
    i_r_indexes = get_inner_boundary_raster_index(polygon_ras_indexes[len(polygon_ras_indexes) - 2], polygon_ras_indexes[0], polygon_ras_indexes[1], joint_offs)
    for inner_ras_index in i_r_indexes:
        inner_ras_indexes.append(inner_ras_index)

    return inner_ras_indexes
