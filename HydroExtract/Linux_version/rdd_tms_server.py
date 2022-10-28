import geopyspark as gps
import time
from pyspark import SparkContext
from shapely.geometry import box
import sys
import os
import random


# 随机生成颜色
def random_color():
    color_arr = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
    color_str = ""
    for i in range(6):
        color_str += color_arr[random.randint(0, 14)]
    color_str = "0x" + color_str + "80"
    return color_str


# 将RDD目录数据发布成TMS: 数据目录路径 导入的数据名称
def rdd_tms_server(catalog_path, resource_name):
    conf = gps.geopyspark_conf(master="local[*]", appName="master")
    pysc = SparkContext(conf=conf)

    print("Tiles Catalog Path")
    catalog_path = "file:///" + catalog_path
    data_name = resource_name

    print("Color Setting")
    # 子流域和坡面
    color_dict = {}
    for i in range(1000):
        color_dict[i] = int(random_color(), 16)
    # # 河网
    # color_dict = {1: int('0xffffff', 16)}
    # # 湖泊
    # color_dict = {1: int('0x0000c690', 16), 0: int('0xffffff00', 16)}

    cm = gps.ColorMap.build(color_dict)

    print('TMS Setting')
    tms = gps.TMS.build(source=(catalog_path, data_name), display=cm)

    print('Set up TMS server')
    tms.bind(host="0.0.0.0", requested_port=8085)
    print(tms.url_pattern)

    time.sleep(365 * 24 * 60 * 60)

    print('Shutdown TMS server')
    tms.unbind()


if __name__ == '__main__':
    p1 = sys.argv[1]
    p2 = sys.argv[2]
    # p1 = '/disk1/Data/hydro_system_display/mapping_catalog'
    # p2 = 'sub_basin_lv12'
    rdd_tms_server(p1, p2)
