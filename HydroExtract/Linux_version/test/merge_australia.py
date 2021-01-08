# coding=utf-8
import merge_tif as mt


if __name__ == '__main__':
    workspace = "/home/liujz/data/Large_Scale_Watershed/Test/5/1"
    dem_folder = "/home/liujz/data/Adjusted_Elevation/data"
    dir_folder = "/home/liujz/data/Flow_Direction/data"
    acc_folder = "/home/liujz/data/Flow_Accumulation_area/data"
    merge_dem = workspace + "/dem.tif"
    merge_dir = workspace + "/dir.tif"
    merge_acc = workspace + "/acc.tif"
    input_array = ['s40e135', 's40e140', 's40e145', 's40e150', 's35e110', 's35e115', 's35e120', 's35e125', 's35e130', 's35e135', 's35e140', 's35e145', 's35e150', 's30e110', 's30e115', 's30e120', 's30e125', 's30e130', 's30e135', 's30e140', 's30e145', 's30e150', 's25e110', 's25e115', 's25e120', 's25e125', 's25e130', 's25e135', 's25e140', 's25e145', 's25e150', 's20e115', 's20e120', 's20e125', 's20e130', 's20e135', 's20e140', 's20e145', 's15e120', 's15e125', 's15e130', 's15e135', 's15e140', 's15e145']
    mt.merge_tif(merge_dem, dem_folder, input_array)
    mt.merge_tif(merge_dir, dir_folder, input_array)
    mt.merge_tif(merge_acc, acc_folder, input_array)
