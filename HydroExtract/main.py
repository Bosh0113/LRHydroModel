from osgeo import gdal
import numpy as np
import os
import struct
import sys

dataset_res = None
dataset_dir = None
dataset_acc = None

dataset_ol = None
river_th = 0

# 一像元宽的外包围线
water_buffers = []
# 水体出入流处
water_channel = []

water_value = -99
water_buffer_value = -1


# 判断是否超出数据范围：x索引 y索引 x最大值 y最大值
def in_data(x, y, x_size, y_size):
    # 左侧超出
    if x < 0:
        return False
    # 上方超出
    if y < 0:
        return False
    # 右侧超出
    if x > x_size:
        return False
    # 下方超出
    if y > y_size:
        return False
    return True


# 根据流向得到指向的栅格索引
def get_to_point(x, y, o_dir):
    dir = abs(o_dir)
    if dir == 1:
        return [x + 1, y]
    elif dir == 2:
        return [x + 1, y + 1]
    elif dir == 4:
        return [x, y + 1]
    elif dir == 8:
        return [x - 1, y + 1]
    elif dir == 16:
        return [x - 1, y]
    elif dir == 32:
        return [x - 1, y - 1]
    elif dir == 64:
        return [x, y - 1]
    elif dir == 128:
        return [x + 1, y - 1]
    else:
        print("direction fail!")
        print(dir)
        sys.exit(0)


# 返回8个方向的索引
def get_8_dir(x, y):
    return [[x - 1, y - 1],
            [x, y - 1],
            [x + 1, y - 1],
            [x - 1, y],
            [x + 1, y],
            [x - 1, y + 1],
            [x, y + 1],
            [x + 1, y + 1]]


# 判断是否指向水体内
def is_to_water(xoff, yoff):
    global dataset_dir, dataset_ol
    dir_data_value = int.from_bytes(dataset_dir.GetRasterBand(1).ReadRaster(xoff, yoff, 1, 1), 'little', signed=True)
    to_point = get_to_point(xoff, yoff, dir_data_value)
    res_data_value = int.from_bytes(dataset_ol.GetRasterBand(1).ReadRaster(to_point[0], to_point[1], 1, 1), 'little',
                                    signed=True)
    return res_data_value == water_value


# 提取坡面：原中心点x索引 原中心点y索引 点x索引 点y索引 坡面id
def extract_slope_surface(o_xoff, o_yoff, xoff, yoff, slope_surface_id):
    global dataset_ol, water_value, water_buffer_value, dataset_dir
    # 判断不在水体内则继续
    data_value = int.from_bytes(dataset_ol.GetRasterBand(1).ReadRaster(xoff, yoff, 1, 1), 'little', signed=True)
    if data_value != water_value:
        # 若在外边界线且未标记
        if data_value == water_buffer_value:
            judge_to_water = is_to_water(xoff, yoff)
            if judge_to_water:
                # 外边界点标记坡面id
                dataset_ol.GetRasterBand(1).WriteRaster(xoff, yoff, 1, 1, struct.pack("i", slope_surface_id))
                # 继续遍历相邻像元
                slope_surface_search(xoff, yoff, slope_surface_id)
        # 不在边界线且未标记
        if data_value == 0:
            # 判断是否流向原中心点
            dir_data_value = int.from_bytes(dataset_dir.GetRasterBand(1).ReadRaster(xoff, yoff, 1, 1), 'little',
                                            signed=True)
            to_point = get_to_point(xoff, yoff, dir_data_value)
            # 若流向中心点
            if to_point[0] == o_xoff and to_point[1] == o_yoff:
                # 标记坡面id
                dataset_ol.GetRasterBand(1).WriteRaster(xoff, yoff, 1, 1, struct.pack("i", slope_surface_id))
                # 继续遍历相邻像元
                slope_surface_search(xoff, yoff, slope_surface_id)


# 遍历边界线构建坡面：边界点x索引 边界点y索引 坡面id
def slope_surface_search(xoff, yoff, slope_surface_id):
    global dataset_dir
    ol_dir_array = get_8_dir(xoff, yoff)
    for index in range(0, 8, 1):
        n_xoff = ol_dir_array[index][0]
        n_yoff = ol_dir_array[index][1]
        x_size = dataset_dir.RasterXSize
        y_size = dataset_dir.RasterYSize
        judge_in_data = in_data(n_xoff, n_yoff, x_size, y_size)
        # 判断像元是否在数据集内且是否为有效流向
        dir_data_value = int.from_bytes(dataset_dir.GetRasterBand(1).ReadRaster(n_xoff, n_yoff, 1, 1), 'little',
                                        signed=True)
        if judge_in_data and dir_data_value != 0:
            extract_slope_surface(xoff, yoff, n_xoff, n_yoff, slope_surface_id)


# 获取坡面的入口函数
def get_slope_surface():
    global dataset_ol, dataset_dir, water_buffers, water_buffer_value
    slope_surface_id = 0
    # 遍历水体的外边线更新由边界线直接流入水体的部分
    for x_y_couple in water_buffers:
        xoff = x_y_couple[0]
        yoff = x_y_couple[1]
        # 判断是否为边界上的非出入流处且未被标记
        ol_data_value = int.from_bytes(dataset_ol.GetRasterBand(1).ReadRaster(xoff, yoff, 1, 1), 'little', signed=True)
        not_is_channel = ol_data_value == water_buffer_value
        # 若为非出入流处且未标记
        if not_is_channel:
            # 判断是否指向水体
            judge_to_water = is_to_water(xoff, yoff)
            # 若流向水体
            if judge_to_water:
                slope_surface_id = slope_surface_id + 1
                # 外边界点标记坡面id
                dataset_ol.GetRasterBand(1).WriteRaster(xoff, yoff, 1, 1, struct.pack("i", slope_surface_id))
                slope_surface_search(xoff, yoff, slope_surface_id)
    # 遍历水体外边线更新由边界线先流入其他坡面的部分
    update_ol_flag = 1
    while update_ol_flag:
        update_ol_flag = 0
        for x_y_couple in water_buffers:
            xoff = x_y_couple[0]
            yoff = x_y_couple[1]
            # 判断是否为边界上的非出入流处且未被标记
            ol_data_value = int.from_bytes(dataset_ol.GetRasterBand(1).ReadRaster(xoff, yoff, 1, 1), 'little',
                                           signed=True)
            not_is_channel = ol_data_value == water_buffer_value
            # 若为非出入流处且未标记
            if not_is_channel:
                dir_data_value = int.from_bytes(dataset_dir.GetRasterBand(1).ReadRaster(xoff, yoff, 1, 1), 'little', signed=True)
                to_point = get_to_point(xoff, yoff, dir_data_value)
                res_data_value = int.from_bytes(dataset_ol.GetRasterBand(1).ReadRaster(to_point[0], to_point[1], 1, 1), 'little', signed=True)
                is_to_ss = res_data_value > 0
                if is_to_ss:
                    slope_surface_id = res_data_value
                    # 标记外边界点有更新
                    update_ol_flag = 1
                    # 外边界点标记坡面id
                    dataset_ol.GetRasterBand(1).WriteRaster(xoff, yoff, 1, 1, struct.pack("i", slope_surface_id))
                    slope_surface_search(xoff, yoff, slope_surface_id)
        # print(update_ol_flag)


# 生成水体外包围：水体数据的x索引 水体数据的y索引 结果数据的x索引 结果数据的y索引
def water_buffer(res_xoff, res_yoff, re_xoff, re_yoff):
    global dataset_res, dataset_acc, dataset_ol, river_th, water_buffers, water_channel
    res_x_size = dataset_res.RasterXSize
    res_y_size = dataset_res.RasterYSize

    # 判断是否已经记录
    ol_data_value = int.from_bytes(dataset_ol.GetRasterBand(1).ReadRaster(re_xoff, re_yoff, 1, 1), 'little',
                                   signed=True)
    not_recode_result = ol_data_value == 0
    # 判断是否在水体数据范围内
    in_water_data = in_data(res_xoff, res_yoff, res_x_size, res_y_size)
    # 若在水体数据中进一步判断是否为水体内像元
    if in_water_data:
        data_value = int.from_bytes(dataset_res.GetRasterBand(1).ReadRaster(res_xoff, res_yoff, 1, 1), 'little',
                                    signed=True)
        not_in_water = data_value != water_value
    else:
        not_in_water = True
    # 若不是水体像元且未记录则记录，即记录新边界点
    if not_recode_result and not_in_water:
        # 添加缓冲区数组记录
        water_buffers.append([re_xoff, re_yoff])
        # 获取该点汇流累积量
        acc_data = dataset_acc.GetRasterBand(1).ReadRaster(re_xoff, re_yoff, 1, 1)
        acc_data_value = struct.unpack('f', acc_data)[0]
        # 若汇流累积量大于阈值则记录为出入流口
        if acc_data_value >= river_th:
            # dataset_ol.GetRasterBand(1).WriteRaster(re_xoff, re_yoff, 1, 1, struct.pack("i", int(acc_data_value)))
            water_channel.append([re_xoff, re_yoff])
        else:
            # 标记为非出入流处的水体外边界
            dataset_ol.GetRasterBand(1).WriteRaster(re_xoff, re_yoff, 1, 1, struct.pack("i", water_buffer_value))


# 3*3网格遍历：水体数据的x索引 水体数据的y索引 结果数据的x索引 结果数据的y索引
def buffer_search(res_xoff, res_yoff, re_xoff, re_yoff):
    res_dir_array = get_8_dir(res_xoff, res_yoff)
    re_dir_array = get_8_dir(re_xoff, re_yoff)
    for index in range(0, 8, 1):
        water_buffer(res_dir_array[index][0], res_dir_array[index][1], re_dir_array[index][0], re_dir_array[index][1])


# 参数分别为：工作空间 水体数据 流向数据 汇流累积量数据
def hydro_extract(base_path, reservoir_tif, dir_tif, acc_tif, river_threshold):
    global dataset_res, dataset_dir, dataset_acc, dataset_ol, river_th
    river_th = river_threshold

    result_path = base_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    # Reservoir path
    res_data_path = base_path + "/" + reservoir_tif
    # Direction path
    dir_data_path = base_path + "/" + dir_tif
    # Accumulation path
    acc_data_path = base_path + "/" + acc_tif

    np.set_printoptions(threshold=np.inf)
    dataset_res = gdal.Open(res_data_path)
    dataset_dir = gdal.Open(dir_data_path)
    dataset_acc = gdal.Open(acc_data_path)

    res_geotransform = dataset_res.GetGeoTransform()
    dir_geotransform = dataset_dir.GetGeoTransform()

    res_x_size = dataset_res.RasterXSize
    res_y_size = dataset_res.RasterYSize
    count = 0

    full_geotransform = dir_geotransform

    full_tl_x = full_geotransform[0]
    full_tl_y = full_geotransform[3]

    # 创建结果数据
    fileformat = "GTiff"
    driver = gdal.GetDriverByName(fileformat)
    result_data_path = result_path + "/" + "result.tif"
    dataset_ol = driver.Create(result_data_path, dataset_dir.RasterXSize, dataset_dir.RasterYSize, 1, gdal.GDT_Int16)
    dataset_ol.SetGeoTransform(full_geotransform)
    dataset_ol.SetProjection(dataset_dir.GetProjection())

    for i in range(res_y_size):
        for j in range(res_x_size):
            count += 1
            res_px = res_geotransform[0] + j * res_geotransform[1] + i * res_geotransform[2]
            res_py = res_geotransform[3] + j * res_geotransform[4] + i * res_geotransform[5]

            scan_data = dataset_res.GetRasterBand(1).ReadRaster(j, i, 1, 1)
            scan_value = int.from_bytes(scan_data, 'little', signed=True)

            # 若是水体内的像元
            if scan_value == water_value:
                # 获取当前水体像元在结果数据中的索引
                re_xoff = int((res_px - full_tl_x) / full_geotransform[1] + 0.5)
                re_yoff = int((res_py - full_tl_y) / full_geotransform[5] + 0.5)

                # 结果数据记录水体
                dataset_ol.GetRasterBand(1).WriteRaster(re_xoff, re_yoff, 1, 1, struct.pack("i", water_value))
                # 使用3*3区域生成水体外包围像元集
                buffer_search(j, i, re_xoff, re_yoff)

    # 提取坡面
    get_slope_surface()

    dataset_res = None
    dataset_dir = None
    dataset_acc = None
    dataset_ol = None


if __name__ == '__main__':
    hydro_extract("D:/Graduation/Program/Data/1", "tashan_99.tif", "dir.tif", "acc.tif", 300)
    # print(water_buffers)
