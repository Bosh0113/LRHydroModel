import geopyspark as gps
import json
from pyspark import SparkContext
from shapely.geometry import Polygon
import os


# 查询区域内数据: 数据目录路径 范围路径(GeoJSON) dem结果路径 流向结果路径 汇流累积量结果路径 湖泊/水库结果路径
def data_search(catalog_path, json_path, dem_tif_path, dir_tif_path, acc_tif_path, lake_tif_path):
	catalog_path = "file://" + catalog_path
	conf = gps.geopyspark_conf(master="local[*]", appName="master")
	pysc = SparkContext(conf=conf)

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
	tiled_raster_layer = gps.query(uri=catalog_path, layer_name="dem", layer_zoom=0, query_geom=poly)
	print(tiled_raster_layer.count())
	print(tiled_raster_layer.layer_metadata.extent)
	tiled_raster_layer.save_stitched(dem_tif_path)

	print("Get Direction")
	tiled_raster_layer = gps.query(uri=catalog_path, layer_name="direction", layer_zoom=0, query_geom=poly)
	# tiled_raster_layer = gps.query(uri=catalog_path, layer_name="dir", layer_zoom=0, query_geom=poly)
	print(tiled_raster_layer.count())
	print(tiled_raster_layer.layer_metadata.extent)
	tiled_raster_layer.save_stitched(dir_tif_path)

	print("Get Accumulation")
	tiled_raster_layer = gps.query(uri=catalog_path, layer_name="accumulation", layer_zoom=0, query_geom=poly)
	# tiled_raster_layer = gps.query(uri=catalog_path, layer_name="acc", layer_zoom=0, query_geom=poly)
	print(tiled_raster_layer.count())
	print(tiled_raster_layer.layer_metadata.extent)
	tiled_raster_layer.save_stitched(acc_tif_path)

	print("Get Lakes")
	tiled_raster_layer = gps.query(uri=catalog_path, layer_name="lakes", layer_zoom=0, query_geom=poly)
	print(tiled_raster_layer.count())
	print(tiled_raster_layer.layer_metadata.extent)
	tiled_raster_layer.save_stitched(lake_tif_path)


if __name__ == '__main__':
	workspace = "/usr/local/large_scale_hydro/Test/1"
	catalog = '/usr/local/large_scale_hydro/catalog'
	geojson_path = '/usr/local/large_scale_hydro/result/polygon.geojson'
	dem_result = workspace + '/dem.tif'
	dir_result = workspace + '/dir.tif'
	acc_result = workspace + '/acc.tif'
	lake_result = workspace + '/lakes.tif'
	data_search(catalog, geojson_path, dem_result, dir_result, acc_result, lake_result)
