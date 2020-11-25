import slope_surface_extract as sse
import os
import time


if __name__ == '__main__':
    start = time.perf_counter()
    workspace_path = "D:/Graduation/Program/Data/19/test"

    process_path = workspace_path + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)
    work_path = workspace_path + "/result"
    if not os.path.exists(work_path):
        os.makedirs(work_path)

    # 提取河网
    acc_tif_path = workspace_path + "/acc.tif"
    water_tif_path = workspace_path + "/water_revise.tif"
    dir_tif_path = workspace_path + "/dir.tif"

    # 提取坡面
    sse.get_slope_surface(work_path, water_tif_path, dir_tif_path, acc_tif_path, 20)

    end = time.perf_counter()
    print('Run', end - start, 's')
    print("改了acc转换")
