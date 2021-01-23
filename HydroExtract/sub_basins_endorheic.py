# coding=utf-8
import time
import sub_basins_utils as sbu
import common_utils as cu
import gdal
import heapq
import temp2 as t2


# 根据连续三个像元的索引判断溢出方向: 第一个点索引 第二个点索引 第三个点索引 溢出方向(返回)
def judge_spill_dir(last_i, current_i, next_i):
    # 方向代号参考TauDEM

    # 三点关系参照文档/论文中关系表
    # 上上
    if sbu.second_point_orientation(last_i, current_i) == 1 and sbu.second_point_orientation(current_i, next_i) == 1:
        return 5
    # 上右
    elif sbu.second_point_orientation(last_i, current_i) == 1 and sbu.second_point_orientation(current_i, next_i) == 2:
        return 4
    # 上左
    elif sbu.second_point_orientation(last_i, current_i) == 1 and sbu.second_point_orientation(current_i, next_i) == 4:
        return 6
    # 右上
    elif sbu.second_point_orientation(last_i, current_i) == 2 and sbu.second_point_orientation(current_i, next_i) == 1:
        return 4
    # 右右
    elif sbu.second_point_orientation(last_i, current_i) == 2 and sbu.second_point_orientation(current_i, next_i) == 2:
        return 3
    # 右下
    elif sbu.second_point_orientation(last_i, current_i) == 2 and sbu.second_point_orientation(current_i, next_i) == 3:
        return 2
    # 下右
    elif sbu.second_point_orientation(last_i, current_i) == 3 and sbu.second_point_orientation(current_i, next_i) == 2:
        return 2
    # 下下
    elif sbu.second_point_orientation(last_i, current_i) == 3 and sbu.second_point_orientation(current_i, next_i) == 3:
        return 1
    # 下左
    elif sbu.second_point_orientation(last_i, current_i) == 3 and sbu.second_point_orientation(current_i, next_i) == 4:
        return 8
    # 左上
    elif sbu.second_point_orientation(last_i, current_i) == 4 and sbu.second_point_orientation(current_i, next_i) == 1:
        return 6
    # 左下
    elif sbu.second_point_orientation(last_i, current_i) == 4 and sbu.second_point_orientation(current_i, next_i) == 3:
        return 8
    # 左左
    elif sbu.second_point_orientation(last_i, current_i) == 4 and sbu.second_point_orientation(current_i, next_i) == 4:
        return 7
    return 0


# 计算溢出方向: 内边界栅格追踪数组 溢出点在数组中的索引 溢出方向(返回)
def get_spill_dir(inner_ras_indexes, spill_pt_index):
    # 当前像元索引
    current_cell = inner_ras_indexes[spill_pt_index]
    # 得到上一个像元
    if spill_pt_index > 0:
        last_cell = inner_ras_indexes[spill_pt_index - 1]
    else:
        last_cell = inner_ras_indexes[len(inner_ras_indexes) - 1]
    # 得到下一个像元
    if spill_pt_index != len(inner_ras_indexes) - 1:
        next_cell = inner_ras_indexes[spill_pt_index + 1]
    else:
        next_cell = inner_ras_indexes[0]

    # 获得溢出点溢出方向
    pour_dir = judge_spill_dir(last_cell, current_cell, next_cell)

    return pour_dir


# 计算溢出位置和方向: 流域内边界栅格索引 DEM数据DataSet 溢出位置(返回) 溢出方向(返回)
def spill_point_dir(inner_ras_indexes, dem_ds):
    # 内边界的高程
    inner_dem = []
    for ras_index in inner_ras_indexes:
        dem_value = cu.get_raster_float_value(dem_ds, ras_index[0], ras_index[1])
        inner_dem.append(dem_value)
    # 获得最低位置的索引
    spill_pt_index = list(map(inner_dem.index, heapq.nsmallest(1, inner_dem)))[0]
    spill_pt = inner_ras_indexes[spill_pt_index]
    # 获得溢出方向
    spill_dir = get_spill_dir(inner_ras_indexes, spill_pt_index)
    # 得到接收点索引
    reception_pt = cu.get_to_point(spill_pt[0], spill_pt[1], spill_dir)

    # # 输出到tif
    # temp_path = r'G:\Graduation\Program\Data\41\endorheic_area0\outlet_dir.tif'
    # file_format = "GTiff"
    # driver = gdal.GetDriverByName(file_format)
    # temp_ds = driver.Create(temp_path, dem_ds.RasterXSize, dem_ds.RasterYSize, 1, gdal.GDT_Int16, options=['COMPRESS=DEFLATE'])
    # temp_ds.SetGeoTransform(dem_ds.GetGeoTransform())
    # temp_ds.SetProjection(dem_ds.GetProjection())
    # temp_ds.GetRasterBand(1).SetNoDataValue(-1)
    # cu.set_raster_int_value(temp_ds, spill_pt[0], spill_pt[1], spill_dir)
    # temp_ds = None

    return spill_pt, spill_dir, reception_pt


# 返回内流区溢满出流位置及出流方向: 流域边界GeoJSON路径 DEM数据路径 溢出位置(返回) 溢出方向(返回) 接收点坐标(返回)
def basin_spill(boundary_geoj, dem_tif):
    polygons_points = sbu.get_polygon_points(boundary_geoj)
    if len(polygons_points) == 1:
        polygon_pts = polygons_points[0]
    else:
        polygon_pts = sbu.update_boundary_polygon(polygons_points)
    dem_ds = gdal.Open(dem_tif)

    p_clockwise = sbu.is_clockwise(polygon_pts)
    # 边界为顺时针多边形
    if p_clockwise:
        # 获取多边形顶点在栅格数据中的索引
        p_offs = []
        for point in polygon_pts:
            p_offs.append(cu.coord_to_off(point, dem_ds))
        # 获取多边形其边对应的所有栅格索引的集合
        polygon_ras_indexes = sbu.raster_index_on_polygon(p_offs)
        # 得到多边形边界内部邻接栅格像元的索引
        inner_ras_indexes = sbu.inner_boundary_raster_indexes(polygon_ras_indexes)

        # 得到流域内边界最低点及出流方向
        spill_point, spill_dir, reception_pt = spill_point_dir(inner_ras_indexes, dem_ds)
        # 得到接受点的坐标
        reception_pt_coord = cu.off_to_coord(reception_pt, dem_ds)
        return spill_point, spill_dir, reception_pt_coord
    else:
        print('No support anticlockwise!')
    dem_ds = None

    return [], 0, []


if __name__ == '__main__':
    start = time.perf_counter()

    workspace = r'G:\Graduation\Program\Data\41\endorheic_area0\test4'
    boundary_geoj_path = workspace + '/data/basin4.geojson'
    dem_tif_path = workspace + '/data/dem4.tif'
    s_pt, s_dir, reception_coord = basin_spill(boundary_geoj_path, dem_tif_path)
    if len(s_pt) > 0:
        print('raster index: ', s_pt, ' direction: ', s_dir, 'next point location: ', reception_coord)

    end = time.perf_counter()
    print('Run', end - start, 's')
