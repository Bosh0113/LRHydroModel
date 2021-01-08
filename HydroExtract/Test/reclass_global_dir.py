import os
import dir_reclassify_saga as drs

class_table = "/home/liujz/data/Large_Scale_Watershed/Test/reclassify_dir/dir_reclass_table.txt"


def reclass_all_dir(o_tif_path, re_tif_path):
    global class_table
    drs.reclassify_dir(o_tif_path, re_tif_path, class_table)


if __name__ == '__main__':
    o_folder = "/home/liujz/data/Flow_Direction/data"
    n_folder = "/home/liujz/data/Flow_Direction/reclass_data"

    o_files = os.listdir(o_folder)
    for o_file in o_files:
        o_file_path = o_folder + "/" + o_file
        n_file_path = n_folder + "/re_" + o_file
        reclass_all_dir(o_file_path, n_file_path)
    print('Over!')
