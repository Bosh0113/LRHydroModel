import os
import time
import direction_reclassify as dr
import land_ocean as lo
import watershed_extract as we
import shutil


# 根据yamazaki的流向数据追踪外流流域: 工作空间路径(结果输出路径) DEM路径 流向路径 汇流累积量路径
def get_exorheic_drainage(workspace, dem_tif, dir_tif, acc_tif):

    process_path = workspace_path + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)

    # 流向数据重分类
    print("--------------------------------Reclassify Direction--------------------------------")
    dir_reclass = process_path + "/dir_reclass.tif"
    dr.dir_reclassify(dir_tif, dir_reclass)

    # 提取路上入海点
    print("-------------------------------------Get Seaside-------------------------------------")
    seaside = process_path + "/seaside.tif"
    lo.get_seaside(dir_reclass, dir_tif, seaside)

    # 提取子流域
    print("------------------------------------Get Watershed-----------------------------------")
    we.get_watershed(workspace, dem_tif, dir_reclass, acc_tif, seaside)
    shutil.rmtree(process_path)


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "D:/Graduation/Program/Data/23"
    result_path = workspace_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    dem_data = workspace_path + "/preprocess/dem.tif"
    dir_data = workspace_path + "/preprocess/dir.tif"
    acc_data = workspace_path + "/preprocess/acc.tif"

    get_exorheic_drainage(result_path, dem_data, dir_data, acc_data)
    end = time.perf_counter()
    print('Run', end - start, 's')
