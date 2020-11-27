import geopyspark as gps
import json
from pyspark import SparkContext
from shapely.geometry import Polygon


def test():
	conf = gps.geopyspark_conf(master="local[*]", appName="master")
	pysc = SparkContext(conf=conf)

	layer_metadata = gps.read_layer_metadata(uri="file:///usr/local/large_scale_hydro/catalog", layer_name="demo-dem", layer_zoom=0)
	layer_extent = layer_metadata.extent
	print(layer_extent)

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

	tiled_raster_layer = gps.query(uri="file:///usr/local/large_scale_hydro/catalog", layer_name="demo-dem", layer_zoom=0, query_geom=poly)
	print(tiled_raster_layer.count())
	print(tiled_raster_layer.layer_metadata.extent)
	tiled_raster_layer.save_stitched('/usr/local/large_scale_hydro/result/result_geojson.tif')


if __name__ == '__main__':
	test()
