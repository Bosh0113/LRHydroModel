import common_utils as cu
import taudem_utils as tu
import water_revise as wr
import os
import time


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "D:/Graduation/Program/Data/19"

    process_path = workspace_path + "/process"
    work_path = workspace_path + "/result"
    if not os.path.exists(work_path):
        os.makedirs(work_path)

    # 测试水体范围修正
    water_path = workspace_path + "/lake_99.tif"
    water_tif_path = work_path + "/water_revise.tif"
    river_tif_path = process_path + "/stream.tif"
    river_record_path = process_path + "/river_record.txt"
    dir_tif_path = workspace_path + "/dir.tif"
    cu.copy_tif_data(water_path, water_tif_path)
    wr.water_revise(water_tif_path, river_tif_path, river_record_path, dir_tif_path)

    end = time.perf_counter()
    print('Run', end - start, 's')
