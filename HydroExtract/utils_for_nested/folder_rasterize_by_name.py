import os
import basins_rasterize as br


if __name__ == '__main__':
    folder_path = ''
    raster_refer = ''
    raster_folder_path = ''

    basins_geojs = os.listdir(folder_path)
    for basins_geoj in basins_geojs:
        pfaf_id = basins_geoj.split('.')[0]
        geoj_path = folder_path + '/' + basins_geoj
        result_path = raster_folder_path + '/' + pfaf_id + '.tif'
        br.basin_rasterize(geoj_path, raster_refer, result_path, pfaf_id, 0, 1)
