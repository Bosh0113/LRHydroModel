import os
import common_utils as cu
import vector_rasterize as vr
import split_subcatchments as ss
import shutil

REFER_RASTER = '/disk1/workspace/20220729/stream.tif'
NODATA_VALUE = 0

def basin_geoj2tif():
    base_path = '/disk1/workspace/20220729'

    for lv_name in range(7, 13):
        geoj_folder = base_path + '/slope_lake/lv' + str(lv_name) + '/sub_basin'
        tiff_folder = base_path + '/display_tif/lv' + str(lv_name) + '/sub_basin'
        if not os.path.exists(tiff_folder):
            os.makedirs(tiff_folder)
        geoj_files = os.listdir(geoj_folder)
        for geoj_idx in range(len(geoj_files)):
            geoj_file = geoj_files[geoj_idx]
            geoj_filename = os.path.join(geoj_folder, geoj_file)
            print(geoj_filename)
            temp_folder = os.path.join(base_path, 'temp')
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)
            try:
                shp_filename = os.path.join(temp_folder, 'shp.shp')
                cu.geojson_to_shp(geoj_filename, shp_filename)
                tif_value = geoj_idx + 1
                tiff_filename = os.path.join(tiff_folder, str(tif_value) + '_' + geoj_file.split('.')[0] + '.tif')
                vr.shp_rasterize(shp_filename, REFER_RASTER, tiff_filename, tif_value, NODATA_VALUE, 1)
            except:
                pass
            shutil.rmtree(temp_folder)


def lake_geoj2tif():
    base_path = '/disk1/workspace/20220729'

    for lv_name in [7, 10]:
        geoj_folder = base_path + '/slope_lake/lv' + str(lv_name) + '/lake'
        tiff_folder = base_path + '/display_tif/lv' + str(lv_name) + '/lake'
        if not os.path.exists(tiff_folder):
            os.makedirs(tiff_folder)
        geoj_files = os.listdir(geoj_folder)
        for geoj_idx in range(len(geoj_files)):
            geoj_file = geoj_files[geoj_idx]
            geoj_filename = os.path.join(geoj_folder, geoj_file)
            print(geoj_filename)
            temp_folder = os.path.join(base_path, 'temp')
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)
            try:
                shp_filename = os.path.join(temp_folder, 'shp.shp')
                cu.geojson_to_shp(geoj_filename, shp_filename)
                tif_value = 1
                tiff_filename = os.path.join(tiff_folder, str(tif_value) + '_' + geoj_file.split('.')[0] + '.tif')
                vr.shp_rasterize(shp_filename, REFER_RASTER, tiff_filename, tif_value, NODATA_VALUE, 1)
            except:
                pass
            shutil.rmtree(temp_folder)


def slope_geoj2tif():
    base_path = '/disk1/workspace/20220729'
    max_slope_count = 0
    for lv_name in range(7, 13):
        slope_count = 0
        geoj_folder = base_path + '/slope_lake/lv' + str(lv_name) + '/slope_surface'
        tiff_folder = base_path + '/display_tif/lv' + str(lv_name) + '/slope_surface'
        if not os.path.exists(tiff_folder):
            os.makedirs(tiff_folder)
        geoj_files = os.listdir(geoj_folder)
        for geoj_idx in range(len(geoj_files)):
            geoj_file = geoj_files[geoj_idx]
            geoj_filename = os.path.join(geoj_folder, geoj_file)
            print(geoj_filename)
            temp_folder = os.path.join(base_path, 'temp')
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)
            # try:
            temp_slope_folder = os.path.join(temp_folder, 'slope_temp')
            if not os.path.exists(temp_slope_folder):
                os.makedirs(temp_slope_folder)
            ss.split_geojson(temp_slope_folder, geoj_filename)
            slope_geoj_files = os.listdir(temp_slope_folder)
            count_slope = len(slope_geoj_files)
            for slope_idx in range(count_slope):
                slope_count += 1
                slope_geoj_file = slope_geoj_files[slope_idx]
                # tif_value = int(slope_geoj_file.split('.')[0])
                tif_value = slope_count
                tif_value_str = str(tif_value)
                shp_filename = os.path.join(temp_folder, tif_value_str + '_shp.shp')
                geoj_filename = os.path.join(temp_slope_folder, slope_geoj_file)
                cu.geojson_to_shp(geoj_filename, shp_filename)
                tiff_filename = os.path.join(tiff_folder, tif_value_str + '_' + geoj_file.split('.')[0] + '.tif')
                vr.shp_rasterize(shp_filename, REFER_RASTER, tiff_filename, tif_value, NODATA_VALUE, 1)
            # except:
            #     pass
            print("Total Slope Count:", slope_count)
            shutil.rmtree(temp_folder)
        if slope_count > max_slope_count:
            max_slope_count = slope_count
        print("Max Slope Count:", max_slope_count)


if __name__ == '__main__':
    basin_geoj2tif()
    lake_geoj2tif()
    slope_geoj2tif()
