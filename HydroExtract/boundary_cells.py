# coding=utf-8
import gdal
import common_utils as cu


# 提取数据边界的像元点集合(int): 数据路径(已重分类) 边界点数据路径
def get_data_boundary_cells(data_tif, boundary_tif):
    data_ds = gdal.Open(data_tif)

    # 创建边界点数据
    print("Create Boundary file...")
    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    full_geotransform = data_ds.GetGeoTransform()
    b_ds = driver.Create(boundary_tif, data_ds.RasterXSize, data_ds.RasterYSize, 1, gdal.GDT_Byte, options=['COMPRESS=DEFLATE'])
    b_ds.SetGeoTransform(full_geotransform)
    b_ds.SetProjection(data_ds.GetProjection())
    b_ds.GetRasterBand(1).SetNoDataValue(0)

    # 遍历基础数据记录边界点
    print("Get Boundary Cells...")
    # nodata值
    no_data = int(data_ds.GetRasterBand(1).GetNoDataValue())
    for i in range(data_ds.RasterYSize):
        # 前个像元点
        f_point_value = None
        for j in range(data_ds.RasterXSize):
            # 若为首尾行
            if i == 0 or i == data_ds.RasterYSize - 1:
                c_point_value = cu.get_raster_int_value(data_ds, j, i)
                # 若为数据点则记录
                if c_point_value != no_data:
                    cu.set_raster_int_value(b_ds, j, i, 1)
            else:
                # 若为第一个点或为行最后一个点
                if j == 0 or j == data_ds.RasterXSize - 1:
                    c_point = [j, i]
                    f_point_value = cu.get_raster_int_value(data_ds, c_point[0], c_point[1])
                    # 若为数据点则记录
                    if f_point_value != no_data:
                        cu.set_raster_int_value(b_ds, c_point[0], c_point[1], 1)
                # 若不为第一个点
                else:
                    c_point = [j, i]
                    # 获取当前点的值
                    c_point_value = cu.get_raster_int_value(data_ds, c_point[0], c_point[1])
                    # 若当前点为数据点
                    if c_point_value != no_data:
                        # 获取周边邻接像元
                        n_points = cu.get_8_dir(c_point[0], c_point[1])
                        # 若周边存在无数据像元则记录
                        for n_point in n_points:
                            n_point_value = cu.get_raster_int_value(data_ds, n_point[0], n_point[1])
                            if n_point_value == no_data:
                                cu.set_raster_int_value(b_ds, c_point[0], c_point[1], 1)
                                break


if __name__ == '__main__':
    workspace = "D:/Graduation/Program/Data/30/7/5"
    data = workspace + "/dir_reclass.tif"
    boundary_data = workspace + "/boundary.tif"
    get_data_boundary_cells(data, boundary_data)
