from osgeo import gdal
import numpy as np
import os
import struct

dataset_res = None
dataset_dir = None
dataset_acc = None
dataset_re = None
river_th = 0

# 一像元的缓冲区
water_buffers = []


water_value = -99
water_buffer_value = -1


# 判断是否超出数据范围
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


# 生成水体外包围
def water_buffer(res_xoff, res_yoff, re_xoff, re_yoff):
    global dataset_res, dataset_dir, dataset_acc, dataset_re, river_th, water_buffers
    res_x_size = dataset_res.RasterXSize
    res_y_size = dataset_res.RasterYSize

    re_data_value = int.from_bytes(dataset_re.GetRasterBand(1).ReadRaster(re_xoff, re_yoff, 1, 1), 'little', signed = True)
    not_recode_result = re_data_value == 0
    in_water_data = in_data(res_xoff, res_yoff, res_x_size, res_y_size)
    if in_water_data:
        data_value = int.from_bytes(dataset_res.GetRasterBand(1).ReadRaster(res_xoff, res_yoff, 1, 1), 'little', signed = True)
        not_in_water = data_value != water_value
    else:
        not_in_water = True
    if not_recode_result and not_in_water:
        water_buffers.append((re_xoff, re_yoff))
        dataset_re.GetRasterBand(1).WriteRaster(re_xoff, re_yoff, 1, 1, struct.pack("i", water_buffer_value))
        acc_data = dataset_acc.GetRasterBand(1).ReadRaster(re_xoff, re_yoff, 1, 1)
        acc_data_value = struct.unpack('f', acc_data)[0]
        if acc_data_value >= river_th:
            dataset_re.GetRasterBand(1).WriteRaster(re_xoff, re_yoff, 1, 1, struct.pack("i", int(acc_data_value)))
            print(acc_data_value)


# 3*3网格遍历
def buffer_search(res_xoff, res_yoff, re_xoff, re_yoff):
    water_buffer(res_xoff - 1, res_yoff + 1, re_xoff - 1, re_yoff + 1)
    water_buffer(res_xoff, res_yoff + 1, re_xoff, re_yoff + 1)
    water_buffer(res_xoff + 1, res_yoff + 1, re_xoff + 1, re_yoff + 1)

    water_buffer(res_xoff - 1, res_yoff, re_xoff - 1, re_yoff)
    water_buffer(res_xoff + 1, res_yoff, re_xoff + 1, re_yoff)

    water_buffer(res_xoff - 1, res_yoff - 1, re_xoff - 1, re_yoff - 1)
    water_buffer(res_xoff, res_yoff - 1, re_xoff, re_yoff - 1)
    water_buffer(res_xoff + 1, res_yoff - 1, re_xoff + 1, re_yoff - 1)


# 参数分别为： 工作空间 水体数据 流向数据 汇流累积量数据
def hydro_extract(base_path, reservoir_tif, dir_tif, acc_tif, river_threshold):
    global dataset_res, dataset_dir, dataset_acc, dataset_re, river_th
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

    fileformat = "GTiff"
    driver = gdal.GetDriverByName(fileformat)
    result_data_path = result_path + "/" + "result.tif"
    dataset_re = driver.Create(result_data_path, dataset_dir.RasterXSize, dataset_dir.RasterYSize, 1, gdal.GDT_Int16)
    dataset_re.SetGeoTransform(full_geotransform)
    dataset_re.SetProjection(dataset_dir.GetProjection())

    for i in range(res_y_size):
        for j in range(res_x_size):
            count += 1
            res_px = res_geotransform[0] + j * res_geotransform[1] + i * res_geotransform[2]
            res_py = res_geotransform[3] + j * res_geotransform[4] + i * res_geotransform[5]
            # print("{} ({}, {})".format(count, res_xoff, res_yoff))
            scan_data = dataset_res.GetRasterBand(1).ReadRaster(j, i, 1, 1)
            scan_value = int.from_bytes(scan_data, 'little', signed=True)

            # 若是水体内的像元
            if scan_value == water_value:
                # 获取当前水体像元在结果数据中的索引
                re_xoff = int((res_px-full_tl_x)/full_geotransform[1] + 0.5)
                re_yoff = int((res_py-full_tl_y)/full_geotransform[5] + 0.5)
                # 使用3*3区域生成水体外包围像元集
                buffer_search(j, i, re_xoff, re_yoff)
                # print(scan_value)

    # print("First location: {},{}".format(first_x, first_y))

    dataset_res = None
    dataset_dir = None
    dataset_acc = None
    dataset_re = None


if __name__ == '__main__':
    hydro_extract("D:/Graduation/Program/Data/1", "tashan_99.tif", "dir.tif", "acc.tif", 300)
    # print(water_buffers)
