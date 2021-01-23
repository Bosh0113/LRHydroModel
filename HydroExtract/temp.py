import common_utils as cu
import sub_basins_endorheic as sbe
import gdal

if __name__ == '__main__':
    workspace = r'G:\Graduation\Program\Data\41\endorheic_area0\multi_basins'
    for i in range(0, 8, 1):
        shp = workspace + '/' + str(i) + '/basin' + str(i) + '.shp'
        geoj = workspace + '/' + str(i) + '/basin' + str(i) + '.geojson'
        cu.shp_to_geojson(shp, geoj)

        dem_tif_path = workspace + '/' + str(i) + '/dem' + str(i) + '.tif'
        s_pt, s_dir, reception_coord = sbe.basin_spill(geoj, dem_tif_path)
        if len(s_pt) > 0:
            temp_path = workspace + '/' + str(i) + '/outlet' + str(i) + '.tif'
            dem_ds = gdal.Open(dem_tif_path)
            file_format = "GTiff"
            driver = gdal.GetDriverByName(file_format)
            temp_ds = driver.Create(temp_path, dem_ds.RasterXSize, dem_ds.RasterYSize, 1, gdal.GDT_Int16, options=['COMPRESS=DEFLATE'])
            temp_ds.SetGeoTransform(dem_ds.GetGeoTransform())
            temp_ds.SetProjection(dem_ds.GetProjection())
            temp_ds.GetRasterBand(1).SetNoDataValue(-1)
            cu.set_raster_int_value(temp_ds, s_pt[0], s_pt[1], s_dir)
            temp_ds = None
            dem_ds = None
            print('raster index: ', s_pt, ' direction: ', s_dir, 'next point location: ', reception_coord)
