import os
import geojson_area_4326 as ga4
import sub_divide_threshold as sdt
import shutil
import clip_tif_saga as cts
import pfafstetter_coding as pc
import raster_polygonize as rp
import split_subcatchments as ss
import geojson_update_properties as gup

# 基础数据
total_dem_tif = '/home/liujz/data/Large_Scale_Watershed/Test/case5.3/nested/dem.tif'
total_dir_o_tif = '/home/liujz/data/Large_Scale_Watershed/Test/case5.3/nested/dir_o.tif'
total_acc_tif = '/home/liujz/data/Large_Scale_Watershed/Test/case5.3/nested/acc.tif'
river_th = 100.0


# 将当前流域单元pfafstetter次分到下一级: 原流域单元 次级流域单元存储路径
def pafa_divide_to_next_level(current_geoj, next_level_folder):
    global total_dem_tif, total_dir_o_tif, total_acc_tif, river_th
    temp_folder = next_level_folder + '/temp'
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    # 获取范围内的数据
    dem_tif = temp_folder + '/dem.tif'
    dir_tif = temp_folder + '/dir.tif'
    acc_tif = temp_folder + '/acc.tif'
    cts.geojson_clip_tif(current_geoj, total_dem_tif, dem_tif)
    cts.geojson_clip_tif(current_geoj, total_dir_o_tif, dir_tif)
    cts.geojson_clip_tif(current_geoj, total_acc_tif, acc_tif)
    # 进行pfafstetter编码次分处理
    pfaf_1 = temp_folder + '/pfaf_1.tif'
    no_sub_basin = pc.get_pfafstetter_code(dir_tif, acc_tif, pfaf_1, river_th)
    # 若没有次级划分
    if no_sub_basin:
        # 删除临时文件夹
        shutil.rmtree(temp_folder)
        return no_sub_basin

    # 对结果进行矢量化
    pfaf_1_geojson = temp_folder + '/pfaf_1.geojson'
    rp.polygonize_to_geojson(pfaf_1, pfaf_1_geojson)
    # 各次级流域分开存储
    sub_basins_folder = temp_folder + '/sub_basins'
    if not os.path.exists(sub_basins_folder):
        os.makedirs(sub_basins_folder)
    ss.split_geojson(sub_basins_folder, pfaf_1_geojson)
    # 将次分的流域重命名存储到次级划分文件夹
    current_basin_name = os.path.basename(current_geoj)
    current_pfaf_id = current_basin_name.split('.')[0]
    sub_basins_geojs = os.listdir(sub_basins_folder)
    for sub_basins_geoj in sub_basins_geojs:
        sub_basin_id = current_pfaf_id + sub_basins_geoj.split('.')[0]
        # 将pfaf_id更新到属性
        properties = {
            "DN": sub_basin_id,
            "pfaf_id": sub_basin_id,
        }
        o_path = sub_basins_folder + '/' + sub_basins_geoj
        gup.geojson_update_properties(o_path, properties)
        # 将结果放在次级层级文件夹下
        n_path = next_level_folder + '/' + sub_basin_id + '.geojson'
        shutil.copy(o_path, n_path)
    # 删除临时文件夹
    shutil.rmtree(temp_folder)
    return 0


# 传统pfafstetter编码划分: 当前层级流域单元所在文件夹 次级层级流域单元所在文件夹
def start_pfaf_divide(current_level_folder, next_level_folder):
    basins_geojs = os.listdir(current_level_folder)
    # 存储各流域单元面积
    basins_areas = {}
    for geoj in basins_geojs:
        geoj_path = current_level_folder + "/" + geoj
        area = ga4.get_polygon_area(geoj_path)
        basins_areas[geoj_path] = area
    # 先判断需要次分的数组
    to_divide = sdt.get_basins_to_divide(basins_areas, 9)
    # 开始次分
    for geoj in basins_geojs:
        geoj_path = current_level_folder + "/" + geoj
        # 若进行次分
        if geoj_path in to_divide:
            no_sub_basin = pafa_divide_to_next_level(geoj_path, next_level_folder)
            if no_sub_basin:
                # 直接复制到下一层级
                pafa_id = geoj.split('.')[0] + '1'
                n_path = next_level_folder + '/' + pafa_id + '.geojson'
                shutil.copy(geoj_path, n_path)
        # 若不进行次分
        else:
            # 直接复制到下一层级
            pafa_id = geoj.split('.')[0] + '1'
            n_path = next_level_folder + '/' + pafa_id + '.geojson'
            shutil.copy(geoj_path, n_path)


if __name__ == '__main__':
    workspace = '/home/liujz/data/Large_Scale_Watershed/Test/case5.3/nested'
    for i in range(4, 5):
        level_folder_path = workspace + '/lv' + str(i)
        next_level_folder_path = workspace + '/lv' + str(i + 1)
        if not os.path.exists(next_level_folder_path):
            os.makedirs(next_level_folder_path)
        start_pfaf_divide(level_folder_path, next_level_folder_path)
