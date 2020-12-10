import os
import time
import geopyspark as gps
from pyspark import SparkContext
import data_search as ds
import clip_tif as ct
import drainage_trace as dt
import raster_polygonize as rp
import split_subcatchments as ss


def test(work_path, filename):

    process_path = work_path + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)
    result_path = work_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    catalog_path = '/usr/local/large_scale_hydro/catalog'
    json_path = work_path + '/' + filename + '.geojson'
    dem_tif_path = process_path + '/dem.tif'
    dir_tif_path = process_path + '/dir.tif'
    acc_tif_path = process_path + '/acc.tif'
    lake_tif_path = process_path + '/lake.tif'

    ds.data_search(catalog_path, json_path, dem_tif_path, dir_tif_path, acc_tif_path, lake_tif_path)

    print("Clip DEM/Dir/Acc")
    dem_clip = result_path + "/dem_clip.tif"
    dir_clip = process_path + "/dir_clip.tif"
    acc_clip = process_path + "/acc_clip.tif"
    ct.geojson_clip_tif(json_path, dem_tif_path, dem_clip)
    ct.geojson_clip_tif(json_path, dir_tif_path, dir_clip)
    ct.geojson_clip_tif(json_path, acc_tif_path, acc_clip)

    print("Get Watershed...")
    dt.get_drainage(process_path, dem_clip, dir_clip, acc_clip)

    print("Get Watershed GeoJSON/SHP.")
    watershed_tif = process_path + "/watershed.tif"
    watershed_geoj = process_path + "/watersheds.geojson"
    watershed_shp = process_path + "/watersheds.shp"
    rp.polygonize_to_geojson(watershed_tif, watershed_geoj)
    rp.polygonize_to_shp(watershed_tif, watershed_shp)

    print("Split Basins.")
    ss.split_geojson(result_path, watershed_geoj)

    print("test")


if __name__ == '__main__':
    # conf = gps.geopyspark_conf(master="local[*]", appName="master")
    # pysc = SparkContext(conf=conf)

    start = time.perf_counter()
    workspace_path = "/usr/local/large_scale_hydro/Test/7"
    files = ['Australia_test']
    for file in files:
        test(workspace_path, file)
    end = time.perf_counter()
    print('Run', end - start, 's')
