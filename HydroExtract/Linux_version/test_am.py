import os
import time
import drainage_trace as dt
import raster_polygonize as rp
import split_subcatchments as ss


def test(work_path):

    process_path = work_path + "/process"
    if not os.path.exists(process_path):
        os.makedirs(process_path)
    result_path = work_path + "/result"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    dem_tif = work_path + "/data/merge_dem.tif"
    dir_o_tif = work_path + "/data/merge_dir.tif"
    acc_tif = work_path + "/data/merge_acc.tif"

    print("Get Complete Watershed...")
    dt.get_drainage(work_path, dem_tif, dir_o_tif, acc_tif)

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
