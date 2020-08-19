import os
import time
import taudem_utils as tu


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
    # 调用TauDEM的Threshold程序
    tu.stream_definition_by_threshold(acc_tif_path, river_tif_path, str(river_threshold))


# 此程序可用cmd调用python执行
# 提取河网为tif
if __name__ == '__main__':
    start = time.perf_counter()
    get_river("D:/Graduation/Program/Data/3", "acc.tif", 300000)
    end = time.perf_counter()
    print('Run', end - start, 's')
