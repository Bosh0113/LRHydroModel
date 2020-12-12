import os
import time
import common_utils as cu
import river_extract as re
import direction_reclassify as dr
import watershed_extract as we
import drainage_trace as dt
import river_add_final as raf


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

    dem_tif = work_path + "/dem_i.tif"
    dir_tif = work_path + "/dir_i.tif"
    acc_tif = work_path + "/acc_i.tif"
    stream_tif = process_path + "/stream.tif"
    dir_reclass = process_path + "/dir_reclass.tif"
    river_th = 0
    re.get_river(process_path, acc_tif, river_th)
    final_record = process_path + "/final.txt"
    dr.dir_reclassify(dir_tif, dir_reclass, final_record)
    raf.add_final_to_river(dir_reclass, final_record, stream_tif, acc_tif, river_th)
    we.get_watershed(process_path, dem_tif, dir_reclass, acc_tif, stream_tif)

    print("test")


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "D:/Graduation/Program/Data/29/preprocess"
    test(workspace_path)
    end = time.perf_counter()
    print('Run', end - start, 's')
