import gdal
import ogr
import os


# lake的shp文件栅格化: shp文件路径 参考Raster文件路径 结果输出路径
def lake_rasterize(shp_path, raster_path, result_path):

    print("Shapefile Rasterize.")

    ra_ds = gdal.Open(raster_path)
    shp = ogr.Open(shp_path, 0)
    shp_layer = shp.GetLayerByIndex(0)

    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    full_geotransform = ra_ds.GetGeoTransform()
    re_ds = driver.Create(result_path, ra_ds.RasterXSize, ra_ds.RasterYSize, 1, gdal.GDT_Int16, options=['COMPRESS=DEFLATE'])
    re_ds.SetGeoTransform(full_geotransform)
    re_ds.SetProjection(ra_ds.GetProjection())
    re_ds.GetRasterBand(1).SetNoDataValue(-9)

    # gdal.RasterizeLayer(re_ds, [1], shp_layer, options=["ATTRIBUTE=value"])
    gdal.RasterizeLayer(re_ds, [1], shp_layer, burn_values=[-99])

    ra_ds = None
    re_ds = None
    shp.Release()


if __name__ == '__main__':
    workspace = "D:/Graduation/Program/Data/31/2"
    shp_data = workspace + "/lakes_vec.shp"
    raster_data = workspace + "/dir.tif"
    result_path = workspace + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    result_data = result_path + "/lakes_raster.tif"
    lake_rasterize(shp_data, raster_data, result_data)
