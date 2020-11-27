import gdal
import common_utils as cu
import time
import os


# 流向数据重分类：原数据路径 重分类数据路径
def dir_reclassify(old_tif_path, updated_tif_path):
    update_value_2array = [1, 2, 4, 8, 16, 32, 64, 128]
    new_value_array = [1, 8, 7, 6, 5, 4, 3, 2]

    old_ds = gdal.Open(old_tif_path)

    print("Create Classified Raster")
    # 创建坡面提取结果数据
    no_data_value = 0
    file_format = "GTiff"
    full_geotransform = old_ds.GetGeoTransform()
    driver = gdal.GetDriverByName(file_format)
    result_data_path = updated_tif_path
    copy_ds = driver.Create(result_data_path, old_ds.RasterXSize, old_ds.RasterYSize, 1, gdal.GDT_Int16)
    copy_ds.SetGeoTransform(full_geotransform)
    copy_ds.SetProjection(old_ds.GetProjection())
    copy_ds.GetRasterBand(1).SetNoDataValue(no_data_value)

    print("Direction Raster Classify...")
    for j in range(copy_ds.RasterYSize):
        for i in range(copy_ds.RasterXSize):
            data_value = cu.get_raster_un_int_value(old_ds, i, j)
            if data_value in update_value_2array:
                index = update_value_2array.index(data_value)
                new_value = new_value_array[index]
                cu.set_raster_int_value(copy_ds, i, j, new_value)
            else:
                cu.set_raster_int_value(copy_ds, i, j, no_data_value)
    old_ds = None
    copy_ds = None


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "D:/Graduation/Program/Data/20"

    process_path = workspace_path + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)
    work_path = workspace_path + "/result"
    if not os.path.exists(work_path):
        os.makedirs(work_path)

    dir_tif_path = workspace_path + "/dir.tif"
    # 流向数据重分类
    stage_time = time.perf_counter()
    dir_reclass_tif = work_path + "/dir_reclass.tif"
    dir_reclassify(dir_tif_path, dir_reclass_tif)
    over_time = time.perf_counter()
    print("Run time: ", over_time - stage_time, 's')

    end = time.perf_counter()
    print('Run', end - start, 's')
