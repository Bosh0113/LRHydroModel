import os
import time
import geopyspark as gps
import json
from pyspark import SparkContext
from shapely.geometry import Polygon
import clip_tif as ct


def test(work_path, filename):

    process_path = work_path + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)
    result_path = work_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    # catalog_path = '/usr/local/large_scale_hydro/catalog'
    catalog_path = '/usr/local/large_scale_hydro/Test/4/catalog'
    json_path = work_path + '/' + filename + '.geojson'
    dem_tif_path = process_path + '/' + filename + '.tif'
    catalog_path = "file://" + catalog_path

    poly = None
    # Creates a Polygon from Geojson
    with open(json_path) as f:
        js = json.load(f)
        features = js['features']
        if features[0]['geometry']['type'] == 'Polygon':
            polygon = features[0]['geometry']['coordinates']
            points = polygon[0]
            input_array = []
            for point in points:
                input_array.append(tuple(point))
            poly = Polygon(input_array)

    print("Get DEM")
    # tiled_raster_layer = gps.query(uri=catalog_path, layer_name="dem", layer_zoom=0, query_geom=poly)
    tiled_raster_layer = gps.query(uri=catalog_path, layer_name="dem-demo", layer_zoom=0, query_geom=poly)
    print(tiled_raster_layer.count())
    print(tiled_raster_layer.layer_metadata.extent)
    tiled_raster_layer.save_stitched(dem_tif_path)

    print("Clip DEM")
    dem_clip = result_path + "/" + filename + "_clip.tif"
    ct.geojson_clip_tif(json_path, dem_tif_path, dem_clip)

    print("test")


if __name__ == '__main__':
    conf = gps.geopyspark_conf(master="local[*]", appName="master")
    pysc = SparkContext(conf=conf)

    start = time.perf_counter()
    workspace_path = "/usr/local/large_scale_hydro/Test/4"
    # files = ['data1', 'data2', 'data3']
    files = ['query_area']
    for file in files:
        test(workspace_path, file)
    end = time.perf_counter()
    print('Run', end - start, 's')
