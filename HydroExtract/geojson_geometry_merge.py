import json
import os


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
        try:
            with open(geojson_path) as f:
                print(geojson_path)
                js = json.load(f)
                featureObj = {}
                if js['type'] == 'FeatureCollection':
                    featureObj = js['features'][0]
                elif js['type'] == 'Feature':
                    featureObj = js
                if featureObj is not {}:
                    features.append(featureObj)
        except:
            pass
    merge_json["features"] = features

    with open(merge_geojson, 'w') as f:
        print(merge_geojson)
        f.write(json.dumps(merge_json))


if __name__ == '__main__':
    workspace = '/home/liujz/data/Large_Scale_Watershed/Test/case5.3/nested'
    for i in range(4, 13):
        folder_path = workspace + '/lv' + str(i)
        merge_geojson_path = workspace + '/lv' + str(i) + '.geojson'
        geojsons = []
        basins_geojs = os.listdir(folder_path)
        for basins_geoj in basins_geojs:
            geojson = folder_path + '/' + basins_geoj
            geojsons.append(geojson)
        merge_geojson(merge_geojson_path, geojsons)
