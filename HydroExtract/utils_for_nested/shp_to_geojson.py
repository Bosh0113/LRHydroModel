import common_utils as cu


if __name__ == '__main__':
    shp_path = r'G:\Graduation\Program\Figure\5.3_case\demo\slope_surface_lv12\preprocess\basins_with_lakes.shp'
    geojson_path = r'G:\Graduation\Program\Figure\5.3_case\demo\slope_surface_lv12\preprocess\basins_with_lakes.geojson'
    cu.shp_to_geojson(shp_path, geojson_path)
