import common_utils as cu
import os


if __name__ == '__main__':
    shp_folder = r'G:\Graduation\Program\Figure\5.3_case\demo\slope_surface_lv12\basins_shp'
    geojson_folder = r'G:\Graduation\Program\Figure\5.3_case\demo\slope_surface_lv12\basins_geojson'

    shps = os.listdir(shp_folder)
    for shp in shps:
        if len(shp.split('.')) == 2 and shp.split('.')[1] == 'shp':
            shp_path = shp_folder + '/' + shp
            pfaf_id = shp.split('.')[0]
            geojson_path = geojson_folder + '/' + pfaf_id + '.geojson'
            cu.shp_to_geojson(shp_path, geojson_path)
