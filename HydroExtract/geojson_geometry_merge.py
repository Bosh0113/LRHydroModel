import json


# 合并多边形GeoJson数据: 合并后的GeoJson存放路径 要合并的GeoJson路径集合
def merge_geojson(merge_geojson, geojson_paths):
    merge_json = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": []
    }

    features = []
    for geojson_path in geojson_paths:
        with open(geojson_path) as f:
            js = json.load(f)
            featureObj = {}
            if js['type'] == 'FeatureCollection':
                featureObj = js['features'][0]
            elif js['type'] == 'Feature':
                featureObj = js
            if featureObj is not {}:
                features.append(featureObj)
    merge_json["features"] = features

    with open(merge_geojson, 'w') as f:
        f.write(json.dumps(merge_json))


if __name__ == '__main__':
    workspace = r'G:\Graduation\Program\Data\46\0\test'
    merge_geojson_path = workspace + '\\merge.geojson'
    geojsons = []
    for i in range(1543, 1546, 1):
        geojson = workspace + '\\pfaf' + str(i) + '.geojson'
        geojsons.append(geojson)
    merge_geojson(merge_geojson_path, geojsons)
