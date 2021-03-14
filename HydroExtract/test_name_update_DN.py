import geojson_update_properties as gup
import os


if __name__ == '__main__':
    for i in range(4, 13):
        folder_path = '/home/liujz/data/Large_Scale_Watershed/Test/case5.3/nested' + '/lv' + str(i)
        basins_geojs = os.listdir(folder_path)
        for basins_geoj in basins_geojs:
            pfaf_id = basins_geoj.split('.')[0]
            properties = {
                "DN": pfaf_id,
                "pfaf_id": pfaf_id,
            }
            geoj_path = folder_path + '/' + basins_geoj
            gup.geojson_update_properties(geoj_path, properties)
