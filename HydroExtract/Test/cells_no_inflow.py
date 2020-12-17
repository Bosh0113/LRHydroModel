import gdal
import common_utils as cu


# 提取无流入的像元点集合: 流向数据路径(已重分类) 无流入点数据路径
def get_no_inflow_cells(dir_tif, no_inflow_tif):
    dir_ds = gdal.Open(dir_tif)

    # 创建无流入点数据
    print("Create No inflow file...")
    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    full_geotransform = dir_ds.GetGeoTransform()
    ni_ds = driver.Create(no_inflow_tif, dir_ds.RasterXSize, dir_ds.RasterYSize, 1, gdal.GDT_Int32)
    ni_ds.SetGeoTransform(full_geotransform)
    ni_ds.SetProjection(dir_ds.GetProjection())
    ni_ds.GetRasterBand(1).SetNoDataValue(0)

    # 遍历基础数据记录无流入点
    print("Get No Inflow Data...")
    for i in range(dir_ds.RasterYSize):
        for j in range(dir_ds.RasterXSize):
            c_point = [j, i]
            # 邻近像元索引
            n_points = cu.get_8_dir(c_point[0], c_point[1])
            # 初始化流入标记
            inflow_flag = 0
            for n_point in n_points:
                # 判断是否在数据内
                in_data = cu.in_data(n_point[0], n_point[1], dir_ds.RasterXSize, dir_ds.RasterYSize)
                if in_data:
                    # 判断是否流向原像元点
                    n_dir = cu.get_raster_int_value(dir_ds, n_point[0], n_point[1])
                    to_point = cu.get_to_point(n_point[0], n_point[1], n_dir)
                    if to_point == c_point:
                        inflow_flag = 1
                        break
            # 若无流入则记录
            if not inflow_flag:
                cu.set_raster_int_value(ni_ds, c_point[0], c_point[1], 1)


if __name__ == '__main__':
    workspace = "D:/Graduation/Program/Data/30/1"
    dir_data = workspace + "/dir_reclass.tif"
    no_inflow_data = workspace + "/no_inflow.tif"
    get_no_inflow_cells(dir_data, no_inflow_data)
