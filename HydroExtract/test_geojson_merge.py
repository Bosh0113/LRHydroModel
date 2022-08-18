import geojson_geometry_merge as ggm
import os


if __name__ == '__main__':
    base_path = '/disk1/workspace/20220729/slope_lake'
    geoj_folders = ['lake', 'no_lake_basin', 'slope_surface']
    for lv in range(7, 13):
        lv_folder_path = os.path.join(base_path, 'lv' + str(lv))
        for geoj_folder in geoj_folders:
            geojsons = []
            geoj_folder_path = os.path.join(lv_folder_path, geoj_folder)
            basins_geojs = os.listdir(geoj_folder_path)
            for basins_geoj in basins_geojs:
                geojson = os.path.join(geoj_folder_path, basins_geoj)
                geojsons.append(geojson)
            merge_geoj = os.path.join(base_path, 'lv' + str(lv) + '_' + geoj_folder + '.geojson')
            ggm.merge_geojson(merge_geoj, geojsons)