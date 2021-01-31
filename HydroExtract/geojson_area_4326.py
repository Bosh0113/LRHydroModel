# coding=utf-8
import time
from osgeo import ogr
from osgeo import osr
import json


# 从GeoJSON数据中计算多边形面积(WGS84投影): GeoJSON路径
def get_polygon_area(geojson_path):

    with open(geojson_path) as f:
        js = json.load(f)
        FeatureObj = None
        if js['type'] == 'FeatureCollection':
            FeatureObj = js['features'][0]
        elif js['type'] == 'Feature':
            FeatureObj = js
        geometry = FeatureObj['geometry']

    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)

    target = osr.SpatialReference()
    target.ImportFromEPSG(5243)

    transform = osr.CoordinateTransformation(source, target)

    poly = ogr.CreateGeometryFromJson(str(geometry))
    poly.Transform(transform)
    geometry_area = poly.GetArea()

    return geometry_area


if __name__ == '__main__':
    start = time.perf_counter()
    workspace = r'G:\Graduation\Program\Data\44\1'
    geoj_path = workspace + '/demo/28153.geojson'
    polygon_area = get_polygon_area(geoj_path)
    print(polygon_area)
    end = time.perf_counter()
    print('Run', end - start, 's')
