import geojson_geometry_merge as ggm
import os


if __name__ == '__main__':
    workspace = r'G:\Graduation\Program\Figure\5.3_case\demo\slope_surface_lv7'
    geoj_folder = workspace + '/slope_surface'
    geojsons = []
    basins_geojs = os.listdir(geoj_folder)
    for basins_geoj in basins_geojs:
        geojson = geoj_folder + '/' + basins_geoj
        geojsons.append(geojson)
    merge_geoj = workspace + '/slope_surface_lv7.geojson'
    ggm.merge_geojson(merge_geoj, geojsons)