import time
import gdal
import common_utils as cu

water_value = -99


# 由河系元素开始追踪重编码上游子流域区域：新区域标识 河系像元x索引 河系像元y索引 子流域数据路径 流向数据路径 湖泊/水库数据路径 河系xy索引集合
def recode_from_river(watershed_id, river_x, river_y, watershed_tif_path, dir_tif_path, water_tif_path, rivers_index):
    global water_value
    # 创建数据集
    watershed_ds = gdal.OpenEx(watershed_tif_path, 1)
    dir_ds = gdal.Open(dir_tif_path)
    water_ds = gdal.Open(water_tif_path)
    # 初始化需要赋值的像元集合
    update_cells = [[river_x, river_y]]
    # 更新区域内像元值
    while len(update_cells) > 0:
        # 取出要更新的像元索引
        update_cell = update_cells.pop()
        print(">>> update cell:", update_cell)
        # 更新像元值
        cu.set_raster_int_value(watershed_ds, update_cell[0], update_cell[1], watershed_id)
        # print('update: ', update_cell, '->', watershed_id)
        # 得到邻近像元集合
        neighbor_cells = cu.get_8_dir(update_cell[0], update_cell[1])
        # 搜索上游像元
        for neighbor_cell in neighbor_cells:
            n_x = neighbor_cell[0]
            n_y = neighbor_cell[1]
            # 判断邻近点是否在数据内
            if cu.in_data(n_x, n_y, watershed_ds.RasterXSize, watershed_ds.RasterYSize):
                # 若不为河段并不为湖泊/水库（即若为子流域）
                water_off = cu.off_transform(n_x, n_y, watershed_ds, water_ds)
                in_water = cu.is_water_cell(water_ds, water_off[0], water_off[1], water_value)
                if neighbor_cell not in rivers_index and not in_water:
                    dir_value = cu.get_raster_int_value(dir_ds, n_x, n_y)
                    to_point = cu.get_to_point(n_x, n_y, dir_value)
                    # 若为上游点
                    if to_point == update_cell:
                        # 加入更新数组
                        update_cells.append(neighbor_cell)

    watershed_ds = None
    dir_ds = None


def watershed_recode(river_record_path, watershed_tif_path, dir_tif_path, water_tif_path):

    # 创建数据集
    watershed_ds = gdal.Open(watershed_tif_path)
    dir_ds = gdal.Open(dir_tif_path)

    # 读取河系信息到内存
    print("Reading rivers info...")
    # 初始化河系像元索引
    rivers_index = []
    with open(river_record_path, 'r') as river_file:
        rivers_info = {}
        for line in river_file.readlines():
            river_info_str = line.strip('\n')
            river_info = river_info_str.split(',')
            # 将river像元的x,y索引作为字典的key
            river_point_str = river_info[0] + ',' + river_info[1]
            # 将river像元的流向和汇流累积量作为字典的value
            river_info_detail = float(river_info[2])
            rivers_info[river_point_str] = river_info_detail
            rivers_index.append([int(river_info[0]), int(river_info[1])])

    # 创建河段集合
    print("Building rivers group...")
    river_reaches = {}
    # 继续创建标识
    flag = 1
    # 开始创建
    while flag:
        flag = 0
        # 取汇流累积量最小的像元索引
        min_acc_river = min(rivers_info, key=rivers_info.get)
        # 获取子流域标识值
        current_cell = min_acc_river.split(',')
        watershed_value = cu.get_raster_int_value(watershed_ds, int(current_cell[0]), int(current_cell[1]))
        # 若不在子流域则继续寻找
        if watershed_value < 0:
            del rivers_info[min_acc_river]
            flag = 1
        # 若在子流域则作为起点
        else:
            # 初始化要遍历的河流起点数组
            river_starts = [min_acc_river]
            # 若河流起点数组不为空则遍历河段
            while len(river_starts) > 0:
                # 开始追踪河段
                start = river_starts.pop()
                # 创建河段索引记录数组
                river_reach = []
                # 获得此像元索引
                start_xy = start.split(',')
                # 获取此河段对应子流域Id标识
                watershed_id = cu.get_raster_int_value(watershed_ds, int(start_xy[0]), int(start_xy[1]))
                # 初始化追踪数组
                tracking = [start]
                # 开始追踪河段的像元
                while len(tracking) > 0:
                    # 取出像元并记录
                    cell_str = tracking.pop()
                    del rivers_info[cell_str]
                    river_reach.append(cell_str)
                    # 获得像元xy索引
                    cell_xy = cell_str.split(',')
                    n_x = cell_xy[0]
                    n_y = cell_xy[1]
                    # 获得流向的像元
                    dir = cu.get_raster_int_value(dir_ds, int(n_x), int(n_y))
                    to_point = cu.get_to_point(int(n_x), int(n_y), dir)
                    to_point_str = ','.join(str(k) for k in to_point)
                    # 若下游像元在原河流数组
                    if to_point_str in rivers_info.keys():
                        # 获取此点在子流域数据的值
                        watershed_value = cu.get_raster_int_value(watershed_ds, to_point[0], to_point[1])
                        # 若在子流域内
                        if watershed_value >= 0:
                            # 若在同子流域内则记录为河段
                            if watershed_value == watershed_id:
                                tracking.append(to_point_str)
                            # 若不在同一子流域则记录为下一河段起点
                            else:
                                river_starts.append(to_point_str)
                        # 若不在子流域内则搜索下游河段的起点
                        else:
                            # 初始化搜索数组
                            find_next_start = [to_point]
                            # 开始搜索
                            while len(find_next_start) > 0:
                                # 取出像元
                                river_cell = find_next_start.pop()
                                # 在原河流数组中清除记录
                                river_cell_str = ','.join(str(k) for k in river_cell)
                                del rivers_info[river_cell_str]
                                # 获得下游像元
                                dir = cu.get_raster_int_value(dir_ds, river_cell[0], river_cell[1])
                                next_point = cu.get_to_point(dir, river_cell[0], river_cell[1])
                                # 若下游像元在原河流数组
                                next_point_str = ','.join(str(k) for k in next_point)
                                if next_point_str in rivers_info.keys():
                                    # 获取此点在子流域数据的值
                                    watershed_value = cu.get_raster_int_value(watershed_ds, next_point[0],
                                                                              next_point[1])
                                    # 若在子流域内
                                    if watershed_value >= 0:
                                        # 则记录为下一河段起点
                                        river_starts.append(next_point_str)
                                    # 若不在子流域内则继续搜索下游河段的起点
                                    else:
                                        find_next_start.append(next_point)
                # 将河段存入集合
                if watershed_id in river_reaches.keys():
                    update_array = river_reaches[watershed_id]
                    update_array.append(river_reach)
                    river_reaches[watershed_id] = update_array
                else:
                    river_reaches[watershed_id] = [river_reach]
            # 若河流像元未全部遍历则继续
            if len(rivers_info) > 0:
                flag = 1

    print("Searching rivers in watersheds need recode...")
    # 记录当前子流域标识最大值
    max_ws_id = 0
    # 初始化在需要重新编码子流域中的河段集合
    recode_ws_rivers = []
    # 筛选出涉及处理的子流域
    for watershed, watershed_rivers in river_reaches.items():
        watershed_id = int(watershed)
        if watershed_id > max_ws_id:
            max_ws_id = watershed_id
        # 若存在多个河段则需要进行重新唯一编码
        if len(watershed_rivers) > 1:
            # print("%s, %d" % (watershed, len(watershed_rivers)))
            # print(watershed_rivers)
            # 找出每组中除最长河段的其他河段
            max_len = 0
            max_river_start = ''
            for river in watershed_rivers:
                if len(river) > max_len:
                    max_len = len(river)
                    max_river_start = river[0]
            for river in watershed_rivers:
                if len(river) <= max_len and max_river_start not in river:
                    recode_ws_rivers.append(river)

    print("Recoding watersheds by rivers...")
    # 在需要重新编码的子流域中的河段
    watershed_count = 0
    for river in recode_ws_rivers:
        max_ws_id += 1
        watershed_count += 1
        total_count = len(recode_ws_rivers)
        print("> updating one watershed.....................", watershed_count, "/", total_count)
        river_count = 0
        for river_cell in river:
            river_count += 1
            total_r_count = len(river)
            print(">> update by river cell:", river_count, "/", total_r_count)
            cell_xy = river_cell.split(',')
            recode_from_river(max_ws_id, int(cell_xy[0]), int(cell_xy[1]), watershed_tif_path, dir_tif_path, water_tif_path, rivers_index)

    watershed_ds = None
    dir_ds = None


if __name__ == '__main__':
    start = time.perf_counter()
    # base_path = "D:/Graduation/Program/Data/10"
    base_path = "D:/Graduation/Program/Data/14/test_recode_ws"
    # base_path = "D:/Graduation/Program/Data/14/test_recode_ws_mpi"
    watershed_recode(base_path + "/river_record.txt", base_path + "/watershed.tif", base_path + "/dir.tif", base_path + "/water_revised.tif")
    end = time.perf_counter()
    print('Run', end - start, 's')
