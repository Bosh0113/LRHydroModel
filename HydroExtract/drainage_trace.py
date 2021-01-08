# coding=utf-8
import os
import time
# import direction_reclassify as dr
import dir_reclassify_saga as drs
import land_ocean as lo
import watershed_extract as we
import river_add_final as raf
import shutil


# 根据yamazaki的流向数据追踪内/外流流域: 工作空间路径(结果输出路径) DEM路径 流向路径 汇流累积量路径
def get_drainage(workspace, dem_tif, dir_tif, acc_tif):

    process_path = workspace + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)

    # 流向数据重分类
    print("--------------------------------Reclassify Direction--------------------------------")
    dir_reclass = process_path + "/dir_reclass.tif"
    current_path = os.path.abspath(os.path.dirname(__file__))
    reclass_table = current_path + "/dir_reclass_table.txt"
    drs.reclassify_dir(dir_tif, dir_reclass, reclass_table)

    # 提取流域追踪起点
    print("----------------------------------Get Trace Start------------------------------------")
    trace_starts = process_path + "/trace_starts.tif"
    final_record = process_path + "/final_record.txt"
    lo.get_trace_points(dir_reclass, dir_tif, trace_starts, final_txt=final_record)
    raf.add_final_to_river(dir_reclass, final_record, trace_starts, acc_tif)

    # 提取子流域
    print("-------------------------------------Get Watershed-----------------------------------")
    we.get_watershed(workspace, dem_tif, dir_reclass, acc_tif, trace_starts)

    # shutil.rmtree(process_path)


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "D:/Graduation/Program/Data/25"
    result_path = workspace_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    # dem_data = workspace_path + "/preprocess/dem_e.tif"
    # dir_data = workspace_path + "/preprocess/dir_e.tif"
    # acc_data = workspace_path + "/preprocess/acc_e.tif"
    dem_data = workspace_path + "/preprocess/dem_i.tif"
    dir_data = workspace_path + "/preprocess/dir_i.tif"
    acc_data = workspace_path + "/preprocess/acc_i.tif"

    get_drainage(result_path, dem_data, dir_data, acc_data)
    end = time.perf_counter()
    print('Run', end - start, 's')
