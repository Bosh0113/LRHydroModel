import json


# 为geojson添加属性描述: geojson文件路径 需要添加的属性键值对
def geojson_add_properties(geojson_path, add_property_json):

    # 新json
    n_json = {}
    with open(geojson_path) as f:
        js = json.load(f)
        if js['type'] == 'FeatureCollection':
            FeatureObj = js['features'][0]
            current_pro = FeatureObj['properties']
            current_pro.update(add_property_json)
            js['features'][0]['properties'] = current_pro
        elif js['type'] == 'Feature':
            FeatureObj = js
            current_pro = FeatureObj['properties']
            current_pro.update(add_property_json)
            js['properties'] = current_pro
        n_json = js
    with open(geojson_path, 'w') as f:
        f.write(json.dumps(n_json))


if __name__ == '__main__':
    workspace = r'G:\Graduation\Program\Data\46\0\test'
    geojson = workspace + '\\pfaf1545.geojson'
    properties = {
        "pfaf_id": 1545,
        "slope": 0,
        "s_order": 0,
        "down_lake": 0
    }
    geojson_add_properties(geojson, properties)
