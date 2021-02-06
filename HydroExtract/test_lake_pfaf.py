# coding=utf-8
import time
import os
import dir_reclassify_saga as drs
import vector_rasterize as vr
import record_rivers as rr
import water_revise as wr
import slope_surface_extract as sse
import pfafstetter_coding as pc


if __name__ == '__main__':
    start = time.perf_counter()

    workspace = r'G:\Graduation\Program\Data\45\3\lv1\lv2\lv3'
    # workspace = '/usr/local/large_scale_hydro/Test/13'

    dir_tif_path = workspace + '/data/dir.tif'
    acc_tif_path = workspace + '/data/acc.tif'
    stream_th_value = 4.0

    pfaf_level = 1
    pfaf_tif_path = workspace + '/refer/pfaf14_' + str(pfaf_level) + '.tif'
    pc.get_pfafstetter_code(dir_tif_path, acc_tif_path, pfaf_tif_path, stream_th_value, pfaf_level)

    # # 数据处理路径
    # process_path = workspace + "/process"
    # if not os.path.exists(process_path):
    #     os.makedirs(process_path)
    #
    # print('重分类流向数据')
    # dir_8_tif = process_path + '/dir_8.tif'
    # current_path = os.path.abspath(os.path.dirname(__file__))
    # reclass_table = current_path + "/dir_reclass_table.txt"
    # drs.reclassify_dir(dir_tif_path, dir_8_tif, reclass_table)
    #
    # print('栅格化湖泊数据')
    # lake_shp_path = workspace + '/data/lakes.shp'
    # lake_tif_path = process_path + '/lakes.tif'
    # vr.lake_rasterize(lake_shp_path, dir_tif_path, lake_tif_path, -99, -9, 1)
    #
    # print('记录河道信息')
    # stream_tif_path = workspace + '/data/stream.tif'
    # rr.record_rivers(process_path, stream_tif_path, acc_tif_path)
    #
    # print('湖泊数据修正')
    # river_record = process_path + "/river_record.txt"
    # wr.water_revise(lake_tif_path, stream_tif_path, river_record, dir_8_tif)
    #
    # print('提取湖泊上游坡面')
    # sse.get_slope_surface(process_path, lake_tif_path, dir_8_tif, acc_tif_path, stream_th_value, -9)

    end = time.perf_counter()
    print('Run', end - start, 's')
