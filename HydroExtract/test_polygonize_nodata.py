import raster_polygonize as rp


if __name__ == '__main__':
    tif_path = r'G:\Graduation\Program\Data\38\test_one_river\pfaf_1.tif'
    geoj_path = r'G:\Graduation\Program\Data\38\test_one_river\pfaf_1.geojson'
    rp.polygonize_to_geojson(tif_path, geoj_path)