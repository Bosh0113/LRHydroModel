import time
import os
import gdal


# 可执行文件所在路径
saga_cmd = r"D:\SoftWare\SAGA\saga_cmd"
# saga_cmd = "/usr/local/bin/saga_cmd"
# saga_cmd = "/share/home/liujunzhi/liujunzhi/saga/build/bin/saga_cmd"


# 调用SAGA GIS的重分类工具: 原始数据路径 分类后数据路径 分类参照表路径
def reclassify_dir(input_file, output_file, table_path):
    print("Dir Reclassify...")
    cmd = saga_cmd + " grid_tools 15 -INPUT " + input_file + " -RESULT " + output_file + " -METHOD 2 -RETAB " + table_path + " -TOPERATOR 1"
    print(cmd)
    d = os.system(cmd)
    print(d)
    r_ds = gdal.Open(output_file, 1)
    r_ds.GetRasterBand(1).SetNoDataValue(0)
    r_ds = None


if __name__ == '__main__':
    start = time.perf_counter()

    workspace = r"G:\Graduation\Program\Data\36"
    input_tif = workspace + "\\s35e135_dir.tif"
    output_tif = workspace + "\\dir_reclass.tif"
    table = workspace + "\\dir_reclass_table.txt"
    reclassify_dir(input_tif, output_tif, table)

    end = time.perf_counter()
    print('Run', end - start, 's')
