import gdal
import common_utils as cu


# 将内流区域终点更新到河流数据: 终点索引参考的流向数据 记录终点索引的txt 需要更新的河系数据
def add_final_to_river(dir_tif, final_points_txt, river_tif):
    dir_ds = gdal.Open(dir_tif)
    rt_ds = gdal.Open(river_tif, 1)

    # 将内流区域终点更新到河流数据
    with open(final_points_txt, 'r') as final_file:
        for line in final_file.readlines():
            final_info_str = line.strip('\n')
            final_info = final_info_str.split(',')
            # 将final像元的x,y索引
            final_xoff = int(final_info[0])
            final_yoff = int(final_info[1])
            # 得到在河流中对应的索引
            r_off = cu.off_transform(final_xoff, final_yoff, dir_ds, rt_ds)
            # 若在数据内
            if cu.in_data(r_off[0], r_off[1], rt_ds.RasterXSize, rt_ds.RasterYSize):
                # 记录Final point到河流
                cu.set_raster_int_value(rt_ds, r_off[0], r_off[1], 1)


if __name__ == '__main__':
    dir_file = "D:/Graduation/Program/Data/25/process/dir_reclass.tif"
    txt_path = "D:/Graduation/Program/Data/25/process/final_record.txt"

    river_file = "D:/Graduation/Program/Data/25/process/result/river_temp.tif"

    dir_ds = gdal.Open(dir_file)
    # 创建river临时数据
    print("Create Trace file...")
    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    full_geotransform = dir_ds.GetGeoTransform()
    trace_ds = driver.Create(river_file, dir_ds.RasterXSize, dir_ds.RasterYSize, 1, gdal.GDT_Int32)
    trace_ds.SetGeoTransform(full_geotransform)
    trace_ds.SetProjection(dir_ds.GetProjection())
    trace_ds.GetRasterBand(1).SetNoDataValue(0)

    dir_ds = None
    trace_ds = None

    add_final_to_river(dir_file, txt_path, river_file)
