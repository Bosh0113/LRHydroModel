import common_utils as cu


if __name__ == '__main__':
    shp_path = r'G:\Graduation\Program\Figure\5.3_case\compare_extent\compare_extent.shp'
    geojson_path = r'G:\Graduation\Program\Figure\5.3_case\compare_extent\compare_extent.geojson'
    cu.shp_to_geojson(shp_path, geojson_path)
