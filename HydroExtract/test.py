import os
import time
import watershed_extract as we


def test(work_path):

    process_path = work_path + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)
    # result_path = work_path + "/result"
    # if not os.path.exists(result_path):
    #     os.makedirs(result_path)

    # shp_path = work_path + "/preprocess/Madagascar_test.shp"
    # geoj_path = work_path + "/preprocess/Madagascar_test.geojson"
    # cu.shp_to_geojson(shp_path, geoj_path)

    dem_tif = work_path + "/dem_e.tif"
    acc_tif = work_path + "/acc_e.tif"
    stream_tif = work_path + "/boundary.tif"
    dir_reclass = work_path + "/dir_reclass.tif"
    we.get_watershed(process_path, dem_tif, dir_reclass, acc_tif, stream_tif)

    print("test")


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "D:/Graduation/Program/Data/30/2"
    test(workspace_path)
    end = time.perf_counter()
    print('Run', end - start, 's')
