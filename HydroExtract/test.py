import os
import time
import common_utils as cu


def test(work_path):

    # process_path = work_path + "/process"
    # if not os.path.exists(process_path):
    #     os.makedirs(process_path)
    # result_path = work_path + "/result"
    # if not os.path.exists(result_path):
    #     os.makedirs(result_path)

    geoj_path = work_path + "/json/138.geojson"
    shp_path = work_path + "/multi/138_auto.shp"
    cu.geojson_to_shp(geoj_path, shp_path)

    print("test")


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "D:/Graduation/Program/Data/27"
    test(workspace_path)
    end = time.perf_counter()
    print('Run', end - start, 's')
