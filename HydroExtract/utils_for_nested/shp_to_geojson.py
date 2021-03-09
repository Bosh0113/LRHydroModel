import common_utils as cu


if __name__ == '__main__':
    shp_path = r'G:\Graduation\Program\Data\51\nested\5\56\566\preprocess\extent.shp'
    geojson_path = r'G:\Graduation\Program\Data\51\nested\5\56\566\preprocess\extent.geojson'
    cu.shp_to_geojson(shp_path, geojson_path)
