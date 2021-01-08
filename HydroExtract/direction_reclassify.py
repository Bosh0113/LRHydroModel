# coding=utf-8
import gdal
import common_utils as cu
import time
import os


# 流向数据重分类：原数据路径 重分类数据路径 记录内流终点(可选)
def dir_reclassify(old_tif_path, updated_tif_path, final_points_txt=None):
    update_value_2array = [1, 2, 4, 8, 16, 32, 64, 128]
    new_value_array = [1, 8, 7, 6, 5, 4, 3, 2]

    final_value = -1

    old_ds = gdal.Open(old_tif_path)

    print("Create Classified Raster")
    # 创建坡面提取结果数据
    no_data_value = 0
    file_format = "GTiff"
    full_geotransform = old_ds.GetGeoTransform()
    driver = gdal.GetDriverByName(file_format)
    result_data_path = updated_tif_path
    copy_ds = driver.Create(result_data_path, old_ds.RasterXSize, old_ds.RasterYSize, 1, gdal.GDT_Byte, options=['COMPRESS=DEFLATE'])
    copy_ds.SetGeoTransform(full_geotransform)
    copy_ds.SetProjection(old_ds.GetProjection())
    copy_ds.GetRasterBand(1).SetNoDataValue(no_data_value)

    txt_flag = 0
    final_f = None
    if final_points_txt is not None:
        print("Record Final Points.")
        txt_flag = 1
        if os.path.exists(final_points_txt):
            os.remove(final_points_txt)
    if txt_flag:
        final_f = open(final_points_txt, "a")

    print("Direction Raster Classify...")
    for j in range(copy_ds.RasterYSize):
        for i in range(copy_ds.RasterXSize):
            data_value = cu.get_raster_un_int_value(old_ds, i, j)
            if data_value in update_value_2array:
                index = update_value_2array.index(data_value)
                new_value = new_value_array[index]
                cu.set_raster_int_value(copy_ds, i, j, new_value)
            else:
                data_value = cu.get_raster_int_value(old_ds, i, j)
                # 如果是内流点则随意赋值流向
                if data_value == final_value and txt_flag:
                    # 拟为内流终点赋值流向
                    # cu.set_raster_int_value(copy_ds, i, j, 1)
                    # 记录内流区终点到txt
                    final_record_item = [i, j]
                    final_record_str = ','.join(str(k) for k in final_record_item)
                    final_f.write(final_record_str + '\n')
                else:
                    cu.set_raster_int_value(copy_ds, i, j, no_data_value)
    old_ds = None
    copy_ds = None
    final_f = None


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
