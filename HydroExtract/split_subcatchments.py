# coding=utf-8
import json
import os


# 将geojson中的子流域分别存储到geojson: 工作路径 原GeoJSON路径
def split_geojson(workspace, geojson_path):

    new_jsons = {}
    with open(geojson_path) as f:
        js = json.load(f)
        features = js['features']
        for feature in features:
            if feature['geometry']['type'] == 'Polygon':
                dn = str(feature['properties']['DN'])
                polygon_coord = feature['geometry']['coordinates']
                if dn in new_jsons:
                    polygon_coords = new_jsons[dn]
                    polygon_coords.append(polygon_coord)
                    new_jsons[dn] = polygon_coords
                else:
                    new_jsons[dn] = [polygon_coord]

    for key, value in new_jsons.items():
        if len(value) == 1:
            new_json = {'type': "FeatureCollection", 'name': key, 'crs': {
                'type': "name",
                'properties': {
                    'name': "urn:ogc:def:crs:OGC:1.3:CRS84"
                }
            }, 'features': [{
                'type': 'Feature',
                'properties': {
                    "DN": int(key)
                },
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': value[0]
                }
            }]}
        else:
            new_json = {'type': "FeatureCollection", 'name': key, 'crs': {
                'type': "name",
                'properties': {
                    'name': "urn:ogc:def:crs:OGC:1.3:CRS84"
                }
            }, 'features': [{
                'type': 'Feature',
                'properties': {
                    "DN": int(key)
                },
                'geometry': {
                    'type': 'MultiPolygon',
                    'coordinates': value
                }
            }]}

        new_json_path = workspace + "/" + key + ".geojson"
        f = open(new_json_path, 'w')
        f.write(json.dumps(new_json))
        f.close()


if __name__ == '__main__':
    base_path = "D:/Graduation/Program/Data/27"
    work_path = base_path + "/json"
    geojson_file = base_path + "/result/ws.geojson"
    split_geojson(work_path, geojson_file)
