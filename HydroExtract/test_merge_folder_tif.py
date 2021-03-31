# coding=utf-8
import os


# 合并tif数据: 合并后的tif路径 需要合并的文件所在文件夹路径
def merge_tif(merged_tif, folder):
    command = 'gdal_merge.py -o ' + merged_tif + ' -co COMPRESS=DEFLATE -co BIGTIFF=YES -of GTiff'
    for root, dirs, files in os.walk(folder):
        for file in files:
            command = command + ' ' + root + '/' + file
    print(command)
    d = os.system(command)
    print(d)


if __name__ == '__main__':
    workspace = "/home/liujz/data/Large_Scale_Watershed/Test/case5.3/nested/slope_surface/lv7"
    merge_tif_path = workspace + "/lake_tif.tif"
    input_folder = workspace + "/lake"
    merge_tif(merge_tif_path, input_folder)

