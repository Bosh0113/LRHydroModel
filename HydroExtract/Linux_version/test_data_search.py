# coding=utf-8
import geopyspark as gps
import json
from pyspark import SparkContext
from shapely.geometry import MultiPolygon
from shapely.geometry import Polygon

conf = gps.geopyspark_conf(master="local[*]", appName="master")
pysc = SparkContext(conf=conf)


def data_search(json_path, catalog_path, data_name, storage_path):
	catalog_path = "file://" + catalog_path

	polys = None
	# Creates a MultiPolygon from Geojson
	with open(json_path) as f:
		js = json.load(f)
		FeatureObj = None
		if js['type'] == 'FeatureCollection':
			FeatureObj = js['features'][0]
		elif js['type'] == 'Feature':
			FeatureObj = js
		if FeatureObj['geometry']['type'] == 'MultiPolygon':
			polygons = FeatureObj['geometry']['coordinates']
			polygons_array = []
			for polygon in polygons:
				input_array = []
				for point in polygon[0]:
					input_array.append(tuple(point))
				polygons_array.append(Polygon(input_array))
			polys = MultiPolygon(polygons_array)
		elif FeatureObj['geometry']['type'] == 'Polygon':
			polygon = FeatureObj['geometry']['coordinates']
			points = polygon[0]
			input_array = []
			for point in points:
				input_array.append(tuple(point))
			polys = Polygon(input_array)

	print("Get Data")
	tiled_raster_layer = gps.query(uri=catalog_path, layer_name=data_name, layer_zoom=0, query_geom=polys)
	print(tiled_raster_layer.count())
	print(tiled_raster_layer.layer_metadata.extent)
	tiled_raster_layer.save_stitched(storage_path)


if __name__ == '__main__':
	workspace = "/disk1/workspace/20221027"
	catalog_path = '/disk1/Data/hydro_system_display/case_demo'
	json_path = '/disk1/workspace/20221027/demo_query.geojson'
	data_name = 'sub_basin_lv12'
	storage_path = workspace + '/demo_query.tif'
	data_search(json_path, catalog_path, data_name, storage_path)
