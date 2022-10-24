import numpy
import random
from PIL import Image

# 随机生成颜色
def random_color():
    color_arr = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
    color_str = ""
    for i in range(6):
        color_str += color_arr[random.randint(0, 14)]
    color_str = "#" + color_str + "80"
    return color_str


# Return (red, green, blue) for the color given as #rrggbb.
def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgba_functions(color_map):
   m = {}
   for key in color_map:
      m[key] = hex_to_rgb(color_map[key])
   print(m)


   def r(v):
      if v in m:
         return m[v][0]
      else:
         return 0

   def g(v):
      if v in m:
         return m[v][1]
      else:
         return 0

   def b(v):
      if v in m:
         return m[v][2]
      else:
         return 0

   def a(v):
      if v in m:
         return m[v][3]
      else:
         return 0x00

   return (numpy.vectorize(r), numpy.vectorize(g), numpy.vectorize(b), numpy.vectorize(a))


basin_tile = numpy.array([[1, 0, 0], [0, 0, 2]])
slope_tile = numpy.array([[0, 0, 1], [2, 0, 0]])
lake_tile = numpy.array([[0, 0, 0], [0, 1, 0]])
river_tile = numpy.array([[0, 1, 0], [0, 0, 0]])
basin_max = basin_tile.max()
slope_copy = numpy.copy(slope_tile)
slope_copy[slope_copy>0] = 1
slope_plus = slope_copy*basin_max
slope_new = slope_tile + slope_plus
map_display_tile = basin_tile + slope_new
b_s_max = map_display_tile.max()
lake_display_value = b_s_max + 1
map_display_tile[lake_tile == 1] = lake_display_value
river_display_value = b_s_max + 2
map_display_tile[river_tile == 1] = river_display_value
map_display_tile = map_display_tile.tolist()

color_map = {}
for i in range(b_s_max + 1):
    color_map[i] = random_color()
color_map[lake_display_value] = '#0000C690'
color_map[river_display_value] = '#FFFFFFFF'

(r, g, b, a) = rgba_functions(color_map)
rgba = numpy.dstack([r(map_display_tile), g(map_display_tile), b(map_display_tile), a(map_display_tile)]).astype('uint8')
img = Image.fromarray(rgba, mode='RGBA')
img.show()

print(map_display_tile)
print(rgba)