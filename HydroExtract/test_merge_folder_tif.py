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
    base_path = '/disk1/workspace/20220729'
    lv_names = [7, 10]
    for lv_name in lv_names:
        merge_tif_path = base_path + "/RDD_tif/lake_lv" + str(lv_name) + ".tif"
        input_folder = base_path + "/display_tif/lv" + str(lv_name) + "/lake"
        merge_tif(merge_tif_path, input_folder)

    for lv_name in range(7, 13):
        for type in ['sub_basin', 'slope_surface']:
            merge_tif_path = base_path + "/RDD_tif/" + type + "_lv" + str(lv_name) + ".tif"
            input_folder = base_path + "/display_tif/lv" + str(lv_name) + "/" + type
            merge_tif(merge_tif_path, input_folder)

