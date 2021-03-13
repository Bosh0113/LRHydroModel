import common_utils as cu
import os


if __name__ == '__main__':
    geojson_folder = r'G:\Graduation\Program\Figure\5.3_case\demo\nested\geojson'
    shp_folder = r'G:\Graduation\Program\Figure\5.3_case\demo\nested\shapefile'
    basins_geojs = os.listdir(geojson_folder)
    for basins_geoj in basins_geojs:
        geoj_path = geojson_folder + '/' + basins_geoj
        shp_path = shp_folder + '/' + basins_geoj.split('.')[0] + '.shp'
        cu.geojson_to_shp(geoj_path, shp_path)