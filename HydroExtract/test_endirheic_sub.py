import pfafstetter_coding as pc
import time


if __name__ == '__main__':
    start = time.perf_counter()

    workspace = r'G:\Graduation\Program\Data\43'
    dir_tif_path = workspace + '/data/dir_128_o.tif'
    acc_tif_path = workspace + '/data/acc.tif'
    stream_th_value = 1.0
    pfaf_level = 1
    pfaf_tif_path = workspace + '/result/pfaf_' + str(pfaf_level) + '.tif'

    pc.get_pfafstetter_code(dir_tif_path, acc_tif_path, pfaf_tif_path, stream_th_value, pfaf_level)

    end = time.perf_counter()
    print('Run', end - start, 's')
