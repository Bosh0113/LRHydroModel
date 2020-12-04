import common_utils as cu
import gdal


# 提取内流区终点的像元: yamazaki流向数据重分类后的数据 yamazaki流向原数据 内流区终点像元集合
def get_seaside(dir_tif, flag_tif, final_tif):

    final_value = -1

    dir_ds = gdal.Open(dir_tif)
    flag_ds = gdal.Open(flag_tif)

    # 创建seaside数据
    print("Create Final file...")
    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    full_geotransform = dir_ds.GetGeoTransform()
    final_ds = driver.Create(final_tif, dir_ds.RasterXSize, dir_ds.RasterYSize, 1, gdal.GDT_Int32)
    final_ds.SetGeoTransform(full_geotransform)
    final_ds.SetProjection(dir_ds.GetProjection())
    final_ds.GetRasterBand(1).SetNoDataValue(0)

    # 遍历基础数据记录seaside
    print("Get Final data...")
    for i in range(flag_ds.RasterYSize):
        for j in range(flag_ds.RasterXSize):
            # 获取流向的值
            flag_value = cu.get_raster_int_value(flag_ds, j, i)
            # 如果是coastline
            if flag_value == final_value:
                # 获取周边像元索引
                neibor_cells = cu.get_8_dir(j, i)
                # 遍历
                for n_cell in neibor_cells:
                    # 判断是否在数据内
                    in_data = cu.in_data(n_cell[0], n_cell[1], dir_ds.RasterXSize, dir_ds.RasterYSize)
                    # 若在数据内
                    if in_data:
                        # 获取流向值
                        dir_value = cu.get_raster_int_value(dir_ds, n_cell[0], n_cell[1])
                        # 获取流向的像元索引
                        n_to_point = cu.get_to_point(n_cell[0], n_cell[1], dir_value)
                        # 若为当前上游像元
                        if n_to_point == [j, i]:
                            # 记录为seaside
                            cu.set_raster_int_value(final_ds, n_cell[0], n_cell[1], 1)
    dir_ds = None
    flag_ds = None
    final_ds = None


if __name__ == '__main__':
    workspace = "D:/Graduation/Program/Data/24"
    dir_data = workspace + "/process/dir_reclass.tif"
    coastline_data = workspace + "/preprocess/dir.tif"
    final_path = workspace + "/process/final.tif"
    get_seaside(dir_data, coastline_data, final_path)
