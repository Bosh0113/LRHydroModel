# coding=utf-8
import os
# os.environ['PROJ_LIB'] = '/home/beichen/anaconda3/envs/master_research/lib/python3.7/site-packages/pyproj/proj_dir/share/proj'
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
    seaside_record = process_path + "/seaside_record.txt"
    final_record = process_path + "/final_record.txt"
    lo.get_trace_points(dir_reclass, dir_tif, trace_starts, seaside_txt=seaside_record, final_txt=final_record)
    raf.add_final_to_river(dir_reclass, final_record, trace_starts, acc_tif)

    # 提取子流域
    print("-------------------------------------Get Watershed-----------------------------------")
    we.get_watershed(workspace, dem_tif, dir_reclass, acc_tif, trace_starts)

    # shutil.rmtree(process_path)


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "/disk1/workspace/20220726"
    result_path = workspace_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    dem_data = workspace_path + "/dem.tif"
    dir_data = workspace_path + "/dir.tif"
    acc_data = workspace_path + "/acc.tif"

    get_drainage(result_path, dem_data, dir_data, acc_data)
    end = time.perf_counter()
    print('Run', end - start, 's')
