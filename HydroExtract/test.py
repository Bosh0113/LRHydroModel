import os
import time
import clip_tif as ct


def test(work_path):

    process_path = work_path + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)
    result_path = work_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    shp_data1 = work_path + "/preprocess/data1.shp"
    geojson_data1 = process_path + "/data1.geojson"
    ct.shp_to_geojson(shp_data1, geojson_data1)
    shp_data2 = work_path + "/preprocess/data2.shp"
    geojson_data2 = process_path + "/data2.geojson"
    ct.shp_to_geojson(shp_data2, geojson_data2)
    shp_data3 = work_path + "/preprocess/data3.shp"
    geojson_data3 = process_path + "/data3.geojson"
    ct.shp_to_geojson(shp_data3, geojson_data3)
    shp_query = work_path + "/preprocess/query_area.shp"
    geojson_query = process_path + "/query_area.geojson"
    ct.shp_to_geojson(shp_query, geojson_query)



    print("test")


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "D:/Graduation/Program/Data/26"
    test(workspace_path)
    end = time.perf_counter()
    print('Run', end - start, 's')
