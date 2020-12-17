import os


# 合并tif数据: 合并后的tif路径 需要合并的文件所在文件夹路径 需要合并的tif名称关键字数组
def merge_tif(merged_tif, folder, filenames):
    command = 'gdal_merge.py -o ' + merged_tif + ' -co COMPRESS=DEFLATE -of GTiff'
    for root, dirs, files in os.walk(folder):
        for file in files:
            for filename in filenames:
                if filename in file:
                    command = command + ' ' + root + '/' + file
    print(command)
    d = os.system(command)
    print(d)


if __name__ == '__main__':
    # workspace = "D:/Graduation/Program/Data/30/5"
    workspace = "/home/liujz/data/Large_Scale_Watershed/Test/4"
    merge_tif_path = workspace + "/merge_tif.tif"
    input_folder = workspace + "/o_tif"
    filename_array = ['e115']
    merge_tif(merge_tif_path, input_folder, filename_array)

