import os
import json
import rasterio
from rasterio.mask import mask
import common_utils as cu


# geojson裁剪tif: geojson路径 tif路径 结果路径
def geojson_clip_tif(geojson_path, tif_path, result_path):
    print("Crop Raster...")
    with open(geojson_path) as f:
        geoj = json.load(f)
        raster = rasterio.open(tif_path)
        geo = []
        for feature in geoj['features']:
            geo.append(feature['geometry'])
        out_image, out_transform = mask(raster, geo, all_touched=True, crop=True, nodata=raster.nodata)
        profile = raster.meta.copy()
        profile.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })
        band_mask = rasterio.open(result_path, "w", **profile)
        band_mask.write(out_image)


# shapefile裁切tif: shapefile路径 tif路径 结果路径
def shp_clip_tif(shp_path, raster_path, result_path):
    temp_path = "temp.geojson"

    cu.shp_to_geojson(shp_path, temp_path)
    geojson_clip_tif(temp_path, raster_path, result_path)

    os.remove(temp_path)


if __name__ == '__main__':
    workspace_path = "D:/Graduation/Program/Data/21"
    # shp_file = workspace_path + "/query/polygon.shp"
    geoj_file = workspace_path + "/query/polygon.geojson"

    dir_file = workspace_path + "/query/dir.tif"
    dir_mask_file = workspace_path + "/dir.tif"
    geojson_clip_tif(geoj_file, dir_file, dir_mask_file)
    acc_file = workspace_path + "/query/acc.tif"
    acc_mask_file = workspace_path + "/acc.tif"
    geojson_clip_tif(geoj_file, acc_file, acc_mask_file)
    dem_file = workspace_path + "/query/dem.tif"
    dem_mask_file = workspace_path + "/dem.tif"
    geojson_clip_tif(geoj_file, dem_file, dem_mask_file)
    lakes_file = workspace_path + "/query/lakes.tif"
    lakes_mask_file = workspace_path + "/lakes.tif"
    geojson_clip_tif(geoj_file, lakes_file, lakes_mask_file)

    # shp_clip_tif(shp_file, tif_file, result_file)

