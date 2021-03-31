import common_utils as cu
import random


# 随机生成颜色
def random_color():
    color_arr = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
    color_str = ""
    for i in range(6):
        color_str += color_arr[random.randint(0, 14)]
    color_str = "0x" + color_str + "80"
    return color_str

if __name__ == '__main__':
    print("Color Setting")
    color_dict = {}
    for i in range(10):
        color_dict[i] = int(random_color(), 16)
    print(color_dict)