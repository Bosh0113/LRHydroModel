import taudem_utils as tu
import watershed_extract as we


if __name__ == '__main__':
    workspace = '/home/liujz/data/Large_Scale_Watershed/Test/case5.3'
    dem_tif = workspace + '/dem.tif'
    dir_tif = workspace + '/dir.tif'
    acc_tif = workspace + '/acc.tif'

    result_path = workspace + '/river_watershed'
    river_tif = result_path + '/stream.tif'
    river_th = str(169000)
    tu.stream_definition_by_threshold(acc_tif, river_tif, river_th)
    we.get_watershed(result_path, dem_tif, dir_tif, acc_tif, river_tif)