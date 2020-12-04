import common_utils as cu
import gdal


# 提取陆地上入流到海洋的像元: yamazaki流向数据重分类后的数据 yamazaki流向原数据 流入海岸线的第一级陆上像元集合
def get_seaside(dir_tif, coastline_tif, seaside_tif):

    coastline_value = 0

    dir_ds = gdal.Open(dir_tif)
    cl_ds = gdal.Open(coastline_tif)

    # 创建seaside数据
    print("Create Seaside file...")
    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    full_geotransform = dir_ds.GetGeoTransform()
    seaside_ds = driver.Create(seaside_tif, dir_ds.RasterXSize, dir_ds.RasterYSize, 1, gdal.GDT_Int32)
    seaside_ds.SetGeoTransform(full_geotransform)
    seaside_ds.SetProjection(dir_ds.GetProjection())
    seaside_ds.GetRasterBand(1).SetNoDataValue(0)

    # 遍历基础数据记录seaside
    print("Get Seaside data...")
    for i in range(cl_ds.RasterYSize):
        for j in range(cl_ds.RasterXSize):
            # 获取流向的值
            cl_value = cu.get_raster_int_value(cl_ds, j, i)
            # 如果是coastline
            if cl_value == coastline_value:
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
                            cu.set_raster_int_value(seaside_ds, n_cell[0], n_cell[1], 1)
    dir_ds = None
    cl_ds = None
    seaside_ds = None


if __name__ == '__main__':
    workspace = "D:/Graduation/Program/Data/23"
    dir_data = workspace + "/process/dir_reclass.tif"
    coastline_data = workspace + "/preprocess/dir.tif"
    seaside_path = workspace + "/process/seaside.tif"
    get_seaside(dir_data, coastline_data, seaside_path)
