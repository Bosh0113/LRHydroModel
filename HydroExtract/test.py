import slope_surface_extract as sse


if __name__ == '__main__':
    workspace_path = "D:/Graduation/Program/Data/14"
    process_path = workspace_path + "/process"
    river_threshold = 300000
    sse.get_slope_surface(process_path, process_path + "/water_revised.tif", process_path + "/dir.tif",
                          process_path + "/acc.tif", river_threshold)
