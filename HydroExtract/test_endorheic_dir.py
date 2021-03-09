import common_utils as cu
import split_subcatchments as ss


if __name__ == '__main__':
    shp_path = r'G:\Graduation\Program\Figure\5.4\union\internal_au.shp'
    geojson_path = r'G:\Graduation\Program\Figure\5.4\union\internal_au.geojson'
    cu.shp_to_geojson(shp_path, geojson_path)
    geoj_folder = r'G:\Graduation\Program\Figure\5.4\union\geojsons'
    ss.split_geojson(geoj_folder, geojson_path)
