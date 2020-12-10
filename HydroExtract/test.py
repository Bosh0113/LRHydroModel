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

    shp_path = work_path + "/preprocess/Australia_test.shp"
    geoj_path = work_path + "/preprocess/Australia_test.geojson"
    cu.shp_to_geojson(shp_path, geoj_path)

    print("test")


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "D:/Graduation/Program/Data/28"
    test(workspace_path)
    end = time.perf_counter()
    print('Run', end - start, 's')
