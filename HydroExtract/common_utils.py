import struct
import gdal


# 获取栅格数据值：数据集 x索引 y索引
def get_raster_value(dataset, x, y):
    return int.from_bytes(dataset.GetRasterBand(1).ReadRaster(x, y, 1, 1), 'little', signed=True)


# 写入栅格数据值：数据集 x索引 y索引 值
def set_raster_value(dataset, x, y, value):
    dataset.GetRasterBand(1).WriteRaster(x, y, 1, 1, struct.pack("i", value))


# 判断是否超出数据范围：x索引 y索引 x最大值 y最大值
def in_data(x, y, x_size, y_size):
    # 左侧超出
    if x < 0:
        return False
    # 上方超出
    if y < 0:
        return False
    # 右侧超出
    if x >= x_size:
        return False
    # 下方超出
    if y >= y_size:
        return False
    return True


# 根据流向得到指向的栅格索引
def get_to_point(x, y, o_dir):
    dir = abs(o_dir)
    # if dir == 1:
    #     return [x + 1, y]
    # elif dir == 2:
    #     return [x + 1, y + 1]
    # elif dir == 4:
    #     return [x, y + 1]
    # elif dir == 8:
    #     return [x - 1, y + 1]
    # elif dir == 16:
    #     return [x - 1, y]
    # elif dir == 32:
    #     return [x - 1, y - 1]
    # elif dir == 64:
    #     return [x, y - 1]
    # elif dir == 128:
    #     return [x + 1, y - 1]
    # else:
    #     return []
    if dir == 1:
        return [x + 1, y]
    elif dir == 8:
        return [x + 1, y + 1]
    elif dir == 7:
        return [x, y + 1]
    elif dir == 6:
        return [x - 1, y + 1]
    elif dir == 5:
        return [x - 1, y]
    elif dir == 4:
        return [x - 1, y - 1]
    elif dir == 3:
        return [x, y - 1]
    elif dir == 2:
        return [x + 1, y - 1]
    else:
        return []


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


# 转换不同数据集的索引
def off_transform(o_xoff, o_yoff, o_dataset, n_dataset):
    # 获取数据集信息
    o_geotransform = o_dataset.GetGeoTransform()
    n_geotransform = n_dataset.GetGeoTransform()

    # 获取该点x,y坐标
    x_coord = o_geotransform[0] + o_xoff * o_geotransform[1] + o_yoff * o_geotransform[2]
    y_coord = o_geotransform[3] + o_xoff * o_geotransform[4] + o_yoff * o_geotransform[5]
    # 获取该点在river中的索引
    n_xoff = int((x_coord - n_geotransform[0]) / n_geotransform[1] + 0.5)
    n_yoff = int((y_coord - n_geotransform[3]) / n_geotransform[5] + 0.5)
    return [n_xoff, n_yoff]


# 复制tif数据到新路径
def copy_tif_data(old_path, copy_path):
    old_ds = gdal.Open(old_path)
    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    copy_ds = driver.CreateCopy(copy_path, old_ds)
    old_ds = None
    copy_ds = None


# 重分类：原数据路径 重分类数据路径 需要更新的像元值数组(二维数组) 新像元值数组(一维数组)
def tif_reclassify(old_tif_path, updated_tif_path, update_value_2array, new_value_array):
    old_ds = gdal.Open(old_tif_path)
    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    copy_ds = driver.CreateCopy(updated_tif_path, old_ds)
    for j in range(copy_ds.RasterYSize):
        for i in range(copy_ds.RasterXSize):
            data_value = get_raster_value(copy_ds, i, j)
            for k in range(len(update_value_2array)):
                if data_value in update_value_2array[k]:
                    index = update_value_2array[k].index(data_value)
                    new_value = new_value_array[index]
                    set_raster_value(copy_ds, i, j, new_value)
                    break
    old_ds = None
    copy_ds = None
