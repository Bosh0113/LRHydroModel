import geopyspark as gps
import json
from pyspark import SparkContext
from shapely.geometry import Polygon
import os


def test(work_path):
	process_path = work_path + "/process"
	if not os.path.exists(process_path):
		os.makedirs(process_path)

	conf = gps.geopyspark_conf(master="local[*]", appName="master")
	pysc = SparkContext(conf=conf)

	poly = None
	# Creates a Polygon from Geojson
	json_path = '/usr/local/large_scale_hydro/result/polygon.geojson'
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

	dem_tif_path = process_path + '/dem.tif'
	print("Get DEM")
	tiled_raster_layer = gps.query(uri="file:///usr/local/large_scale_hydro/catalog", layer_name="dem", layer_zoom=0, query_geom=poly)
	print(tiled_raster_layer.count())
	print(tiled_raster_layer.layer_metadata.extent)
	tiled_raster_layer.save_stitched(dem_tif_path)

	dir_tif_path = process_path + '/dir.tif'
	print("Get Direction")
	tiled_raster_layer = gps.query(uri="file:///usr/local/large_scale_hydro/catalog", layer_name="direction", layer_zoom=0, query_geom=poly)
	print(tiled_raster_layer.count())
	print(tiled_raster_layer.layer_metadata.extent)
	tiled_raster_layer.save_stitched(dir_tif_path)

	acc_tif_path = process_path + '/acc.tif'
	print("Get Accumulation")
	tiled_raster_layer = gps.query(uri="file:///usr/local/large_scale_hydro/catalog", layer_name="accumulation", layer_zoom=0, query_geom=poly)
	print(tiled_raster_layer.count())
	print(tiled_raster_layer.layer_metadata.extent)
	tiled_raster_layer.save_stitched(acc_tif_path)

	# lake_tif_path = '/usr/local/large_scale_hydro/result/lakes.tif'
	# print("Get Lakes")
	# tiled_raster_layer = gps.query(uri="file:///usr/local/large_scale_hydro/catalog", layer_name="lakes", layer_zoom=0, query_geom=poly)
	# print(tiled_raster_layer.count())
	# print(tiled_raster_layer.layer_metadata.extent)
	# tiled_raster_layer.save_stitched(lake_tif_path)


if __name__ == '__main__':
	workspace = "/usr/local/large_scale_hydro/Test/1"
	test(workspace)
