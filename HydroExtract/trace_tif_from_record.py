# coding=utf-8
import common_utils as cu
import gdal
import time


def get_trace_from_record(refer_tif, seaside_txt, final_txt, trace_tif):
    ref_ds = gdal.Open(refer_tif)

    print("Create Trace file...")
    file_format = "GTiff"
    driver = gdal.GetDriverByName(file_format)
    full_geotransform = ref_ds.GetGeoTransform()
    trace_ds = driver.Create(trace_tif, ref_ds.RasterXSize, ref_ds.RasterYSize, 1, gdal.GDT_Byte)
    trace_ds.SetGeoTransform(full_geotransform)
    trace_ds.SetProjection(ref_ds.GetProjection())
    trace_ds.GetRasterBand(1).SetNoDataValue(0)

    # 将内流区域终点更新到河流数据
    print("Add Final to Trace file...")
    with open(final_txt, 'r') as final_file:
        for line in final_file.readlines():
            final_info_str = line.strip('\n')
            final_info = final_info_str.split(',')
            # 将final像元的x,y索引
            f_x_coord = float(final_info[0])
            f_y_coord = float(final_info[1])
            off_xy = cu.coord_to_off([f_x_coord, f_y_coord], trace_ds)
            if cu.in_data(off_xy[0], off_xy[1], trace_ds.RasterXSize, trace_ds.RasterYSize):
                cu.set_raster_int_value(trace_ds, off_xy[0], off_xy[1], 1)

    # 将内流区域终点更新到河流数据
    print("Add Seaside to Trace file...")
    with open(seaside_txt, 'r') as final_file:
        for line in final_file.readlines():
            final_info_str = line.strip('\n')
            final_info = final_info_str.split(',')
            # 将seaside像元的x,y索引
            f_x_coord = float(final_info[0])
            f_y_coord = float(final_info[1])
            off_xy = cu.coord_to_off([f_x_coord, f_y_coord], trace_ds)
            if cu.in_data(off_xy[0], off_xy[1], trace_ds.RasterXSize, trace_ds.RasterYSize):
                cu.set_raster_int_value(trace_ds, off_xy[0], off_xy[1], 1)

    print('over.')
    ref_ds = None
    trace_ds = None


if __name__ == '__main__':
    start = time.perf_counter()
    workspace = '/share/home/liujunzhi/liujunzhi/large_basins/global_9/au'
    data1_path = workspace + '/data1'
    process_path = workspace + '/process'
    seaside_record = process_path + '/seaside_record.txt'
    final_record = process_path + '/final_record.txt'
    refer_tif_path = data1_path + '/au_dem.tif'
    trace_path = data1_path + '/trace_starts1.tif'
    get_trace_from_record(refer_tif_path, seaside_record, final_record, trace_path)
    end = time.perf_counter()
    print('Run', end - start, 's')
