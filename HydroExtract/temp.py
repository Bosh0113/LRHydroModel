import common_utils as cu


if __name__ == '__main__':
    shp = r'G:\Graduation\Program\Data\41\endorheic_area0\data\demo_boundary.shp'
    geoj = r'G:\Graduation\Program\Data\41\endorheic_area0\data\demo_boundary.geojson'
    cu.shp_to_geojson(shp, geoj)
