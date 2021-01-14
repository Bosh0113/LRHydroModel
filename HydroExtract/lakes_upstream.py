# coding=utf-8
import os
import time
import vector_rasterize as vr
import slope_surface_extract as sse
import raster_polygonize as rp
import clip_tif_saga as cts
import shutil


saga_cmd = '/home/liujz/saga-7.6.3/build/bin/saga_cmd'


# 单个处理: 原始湖泊shp 完整DEM数据 完整DIR数据 完整ACC数据 临时工作空间路径 上游及水域范围DEM存储路径 存储新矢量湖泊 栅格化上游范围存放路径 栅格化湖泊范围存放路径
def get_lake_upstream(shp_lake, dem_tif, dir_tif, acc_tif, temp_folder, basin_dems_folder, lake_shp_folder, upstream_data_folder, lakes_tifs_folder):
    lake_filename = os.path.basename(shp_lake)
    lake_index = lake_filename.split('.')[0]
    print('Lake index: ', lake_index)
    lake_tif_path = lakes_tifs_folder + '/' + lake_index + '.tif'
    # 获取湖泊栅格文件（最小范围）
    vr.lake_rasterize(shp_lake, dem_tif_path, lake_tif_path, -99, -9, 1)
    # 获取上游及湖体范围
    sse.get_slope_surface(temp_folder, lake_tif_path, dir_tif_path, acc_tif_path, 500000)
    # 上游及湖体范围矢量化
    wss_tif = temp_folder + '/water_slope_surface.tif'
    wss_shp = basin_dems_folder + '/' + lake_index + '_wss.shp'
    rp.polygonize_to_shp(wss_tif, wss_shp)
    # 存储上游及湖体整体范围的dem数据
    basin_dem = basin_dems_folder + '/' + lake_index + "_total_dem.tif"
    cts.shp_clip_tif(wss_shp, dem_tif, basin_dem)
    # 得到上游区域提取的tif
    upstream_tif = temp_folder + '/upstream.tif'
    cmd = saga_cmd + " grid_tools 15 -INPUT " + wss_tif + " -RESULT " + upstream_tif + " -METHOD 0 -OLD -99 -NEW -9 -RESULT_NODATA_VALUE -9"
    print(cmd)
    d = os.system(cmd)
    print(d)
    # 得到上游区域shp
    upstream_shp = upstream_data_folder + '/' + lake_index + '_shp.shp'
    rp.polygonize_to_shp(upstream_tif, upstream_shp)
    # 保存湖泊对应shp
    n_lake_shp = lake_shp_folder + '/' + lake_index + '_n.shp'
    rp.polygonize_to_shp(lake_tif_path, n_lake_shp)
    # 得到上游最小数据
    upstream_dem = upstream_data_folder + '/' + lake_index + '_dem.tif'
    cts.shp_clip_tif(upstream_shp, dem_tif, upstream_dem)
    upstream_dir = upstream_data_folder + '/' + lake_index + '_dir.tif'
    cts.shp_clip_tif(upstream_shp, dir_tif, upstream_dir)
    upstream_acc = upstream_data_folder + '/' + lake_index + '_acc.tif'
    cts.shp_clip_tif(upstream_shp, acc_tif, upstream_acc)


if __name__ == '__main__':
    start = time.perf_counter()
    workspace = "/home/liujz/data/Large_Scale_Watershed/Test/tp_1"
    data_path = workspace + "/data_n"
    shp_lakes_path = workspace + "/lakes_n"
    dem_tif_path = data_path + "/tp_dem.tif"
    dir_tif_path = data_path + "/tp_dir_re.tif"
    acc_tif_path = data_path + "/tp_acc.tif"

    result_path = workspace + '/result'
    tif_lakes_path = result_path + "/lake_tifs"
    tif_basins_path = result_path + "/basin_dems"
    tif_up_data_path = result_path + '/upstream_data'
    lake_shp_n_path = result_path + '/lake_shps'

    lake_index = 0
    lake_shps = os.listdir(shp_lakes_path)
    for lake_shp in lake_shps:
        # 获得水体栅格数据
        if len(lake_shp.split('.')) == 2 and lake_shp.split('.')[1] == 'shp':
            lake_index += 1
            print('No.', lake_index, ' lake')
            # 开始提取数据
            temp_folder_path = workspace + '/temp_folder'
            if not os.path.exists(temp_folder_path):
                os.makedirs(temp_folder_path)
            lake_shp_path = shp_lakes_path + "/" + lake_shp
            get_lake_upstream(lake_shp_path, dem_tif_path, dir_tif_path, acc_tif_path, temp_folder_path, tif_basins_path, lake_shp_n_path, tif_up_data_path, tif_lakes_path)
            # 删除临时文件夹
            shutil.rmtree(temp_folder_path)

    end = time.perf_counter()
    print('Run', end - start, 's')
