# coding=utf-8
import os
import time
import raster_polygonize as rp
import split_subcatchments as ss
import watershed_extract as we
import river_add_final as raf


def test(work_path):

    process_path = work_path + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)
    result_path = work_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    dem = work_path + "/data/dem.tif"
    dir_o = work_path + "/data/dir.tif"
    dir_reclass = work_path + "/data/dir_reclass.tif"
    acc = work_path + "/data/acc.tif"

    print("Update River&Dir...")
    trace_starts = work_path + "/data/trace_starts.tif"
    final_record = work_path + "/data/final_record.txt"
    raf.add_final_to_river(dir_reclass, final_record, trace_starts, acc)


    print("Get Watershed...")
    we.get_watershed(process_path, dem, dir_reclass, acc, trace_starts)


    print("Get Watershed GeoJSON/SHP.")
    watershed_tif = process_path + "/watershed.tif"
    watershed_geoj = process_path + "/watersheds.geojson"
    watershed_shp = process_path + "/watersheds.shp"
    rp.polygonize_to_geojson(watershed_tif, watershed_geoj)
    rp.polygonize_to_shp(watershed_tif, watershed_shp)

    # print("Split Basins.")
    # ss.split_geojson(result_path, watershed_geoj)

    print("test")


if __name__ == '__main__':

    start = time.perf_counter()
    workspace_path = "/share/home/liujunzhi/liujunzhi/large_basins/1"
    test(workspace_path)
    end = time.perf_counter()
    print('Run', end - start, 's')
