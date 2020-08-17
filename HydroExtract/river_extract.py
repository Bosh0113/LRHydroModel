import os
import time


# 根据阈值提取河道：工作空间 汇流累积量 提取阈值
def get_river(base_path, acc_tif, river_threshold):
    # 创建结果文件夹
    result_path = base_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    # 数据路径
    acc_tif_path = base_path + "/" + acc_tif
    river_tif_path = result_path + "/river.tif"
    # 当前路径
    current_path = os.getcwd().replace("\\", "/")
    # cmd语句调用TauDEM的Threshold程序
    cmd = 'mpiexec -n ' + str(5) + ' ' + current_path +'/TauDEM/Threshold -ssa ' + acc_tif_path + ' -src ' + river_tif_path + ' -thresh ' + str(river_threshold)
    print(cmd)
    # 执行cmd
    d = os.system(cmd)
    print(d)


# 此程序可用cmd调用python执行
# 提取河网为tif
if __name__ == '__main__':
    start = time.perf_counter()
    get_river("D:/Graduation/Program/Data/1", "acc.tif", 300)
    end = time.perf_counter()
    print('Run', end - start, 's')
