import os
import time
import direction_reclassify as dr
import land_ocean as lo
import watershed_extract as we


def test(work_path):

    process_path = work_path + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)
    result_path = work_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    acc_data = work_path + "/preprocess/acc.tif"
    dir_data = work_path + "/preprocess/dir.tif"
    dem_data = work_path + "/preprocess/dem.tif"

    # 流向数据重分类
    print("--------------------------------Reclassify Direction--------------------------------")
    dir_reclass = process_path + "/dir_reclass.tif"
    # dr.dir_reclassify(dir_data, dir_reclass)

    # # 提取路上入海点
    # print("-------------------------------------Get Seaside-------------------------------------")
    final = process_path + "/final.tif"
    # lo.get_seaside(dir_reclass, dir_data, seaside)
    #
    # # 提取子流域
    # print("------------------------------------Get Watershed-----------------------------------")
    we.get_watershed(result_path, dem_data, dir_reclass, acc_data, final)

    print("test")


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "D:/Graduation/Program/Data/24"
    test(workspace_path)
    end = time.perf_counter()
    print('Run', end - start, 's')
