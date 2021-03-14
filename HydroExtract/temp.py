import common_utils as cu


if __name__ == '__main__':
    geoj_path = r'G:\Graduation\Program\Figure\5.3_case\demo\slope_surface_lv7\temp\4342161.geojson'
    shp_path = r'G:\Graduation\Program\Figure\5.3_case\demo\slope_surface_lv7\temp\4342161.shp'
    cu.geojson_to_shp(geoj_path, shp_path)