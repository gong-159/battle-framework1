# self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, background="white")
from tkinter import *
import tkinter as tk
# from de.cal_power import *
import random
import math
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
# from de.AStar import cal_path
import de.AStar
import copy


class Window:
    def __init__(self):
        self.obs_de = []
        self.num_weapon = 0  # 需要导弹的数量
        self.cell_size = 20
        self.height = 700
        self.width = 700
        self.hz_cells = self.width // self.cell_size  # Number of horizontal cells.
        self.vt_cells = self.height // self.cell_size  # Number of vertical cells.
        # Preallocate 2D grid (list-of-lists).
        self.grid = [[None for _ in range(self.hz_cells)]
                     for _ in range(self.vt_cells)]
        self.root = Tk()
        self.root.geometry("1050x800")
        self.w = Label(self.root, text="Time:", font=("宋体", 16, "bold"), width=30, height=2)
        self.color = 1
        self.w.pack()
        self.text = Text(font=("宋体", 16, "bold"), width=15, height=1)
        self.text.place(x=560, y=10)
        self.cv = Canvas(self.root, width=self.width, height=self.height, background="white")  #
        # self.root.resizable(False,background="white")
        self.cv.pack()
        # self.canvas.bind("<1>",self.select_start_node)
        # You can still do it this way if you want.
        #  self.canvas.bind("s",self.select_start_node)
        #  self.canvas.bind("<1>",lambda event:  self.canvas.focus_set())

        # 一组单选框要绑定同一个变量
        self.r = IntVar()  # 给单选框添加variable，用于显示value值
        self.radio1 = Radiobutton(self.root, text="蓝方探测能力", font=("宋体", 14, "bold"), value=1, variable=self.r,
                                  command=self.show_color)  # 绿色
        self.radio1.place(x=10, y=100)
        # value值不能相同，才能实现单选
        self.radio2 = Radiobutton(self.root, text="蓝方攻击空中能力", font=("宋体", 14, "bold"), value=2, variable=self.r,
                                  command=self.show_color)  # 蓝色
        self.radio2.place(x=10, y=200)
        self.radio3 = Radiobutton(self.root, text="蓝方攻击地面能力", font=("宋体", 14, "bold"), value=3, variable=self.r,
                                  command=self.show_color)  # 黄
        self.radio3.place(x=10, y=300)
        self.radio4 = Radiobutton(self.root, text="红方探测能力", font=("宋体", 14, "bold"), value=4, variable=self.r,
                                  command=self.show_color)  # 绿
        self.radio4.place(x=880, y=100)
        self.radio5 = Radiobutton(self.root, text="红方攻击空中能力", font=("宋体", 14, "bold"), value=5, variable=self.r,
                                  command=self.show_color)  # 蓝
        self.radio5.place(x=880, y=200)
        self.radio6 = Radiobutton(self.root, text="红方攻击地面能力", font=("宋体", 14, "bold"), value=6, variable=self.r,
                                  command=self.show_color)  # 黄
        self.radio6.place(x=880, y=300)
        self.radio7 = Radiobutton(self.root, text="红方干扰能力", font=("宋体", 14, "bold"), value=7, variable=self.r,
                                  command=self.show_color)  # 红
        self.radio7.place(x=880, y=400)

        #
        # self.B = tk.Button(text="开始", width=15, height=2)
        # self.B.pack()

    # 单选框触发事件
    def show_color(self, ):
        self.color = self.r.get()
        self.draw_grid(self.obs_de)
        print(self.color)
        # aa = [[0, 1, 2, 3, 4, 5, 6, 7] * 5 for i in range(35)]
        # a = []
        # for i in range(7):
        #     a.append(aa)
        # self.draw_grid(a, self.r.get())

    # 将35*35列表重新赋值,0为0其余等间隔分类,对应不同颜色
    def convert_list(self, a):
        max_Value = max(max(row) for row in a)
        gap = max_Value / 6
        for i in range(35):  # 行
            for j in range(35):  # 列
                if a[i][j] != 0:  # 等于0不变
                    a[i][j] = int(a[i][j] / gap) + 1
        return a

    # 计算每个单元格的值-调用相应的函数计算各个单元的值
    def cal_cellValue(self, obs):
        cellValue_list = []  # 0-6 蓝色搜素、蓝色空中攻击、蓝色地面攻击、红色搜索、红色空中攻击、红色地面攻击、红色干扰
        for i in range(7):
            list = [[0] * 35 for i in range(35)]
            cellValue_list.append(list)
        # search_list_blue = [[0] * 35 for i in range(35)]
        # attack_air_list_blue = [[0] * 35 for i in range(35)]
        # attack_land_list_blue= [[0] * 35 for i in range(35)]
        # search_list_red= [[0] * 35 for i in range(35)]
        # attack_air_list_red= [[0] * 35 for i in range(35)]
        # attack_land_list_red= [[0] * 35 for i in range(35)]
        # interfere_list = [[0] * 35 for i in range(35)]
        for unit in obs['units']:
            cellValue_list[6] = add_interfereValue(unit, all_dict['interfere'], cellValue_list[6])  # interfere_list
        for unit in obs['qb']:
            cellValue_list[0] = add_searchValue(unit, all_dict['search'], cellValue_list[0],
                                                cellValue_list[6])  # search_list_blue
            cellValue_list[1] = add_attack_Air(unit, all_dict['attack'], cellValue_list[1])  # attack_air_list_blue
            cellValue_list[2] = add_attack_Land(unit, all_dict['attack'], cellValue_list[2])  # attack_land_list_blue
        for unit in obs['units']:
            cellValue_list[3] = add_searchValue(unit, all_dict['search'], cellValue_list[3],
                                                cellValue_list[6])  # search_list_red
            cellValue_list[4] = add_attack_Air(unit, all_dict['attack'], cellValue_list[4])  # attack_air_list_red
            cellValue_list[5] = add_attack_Land(unit, all_dict['attack'], cellValue_list[5])  # attack_land_list_red

        return cellValue_list

    # 绘制网格并填充颜色-调用相应的函数计算各个单元的值
    def draw_grid(self, obs, num_weapon = 1):
        """ Fill Canvas with a grid of white rectangles. """
        # color= (255, 255, 255)
        self.obs_de = copy.deepcopy(obs)
        self.num_weapon = num_weapon
        list_null = []
        for i in range(7):
            list = [[0] * 35 for i in range(35)]
            list_null.append(list)

        cellValue_list = self.cal_cellValue(obs)  # 计算7*35*35
        bombers_dic = cal_bombers_weapons(obs)  # 计算现有导弹情况
        # bombers_dic --- {4521: {'pos': (17, 31), 'num': 2}, 1499: {'pos': (17, 31), 'num': 2}, 4140: {'pos': (17, 31), 'num': 2},
        #  3678: {'pos': (17, 31), 'num': 2}, 'air': {'pos': (17, 32), 'num': 24}}

        if cellValue_list != list_null:
            path_list = de.AStar.cal_mul_path(cellValue_list,bombers_dic,num_weapon)
        else:
            path_list = []
        # print(path_list)
        # print(cellValue_list)
        a = []
        G_colors = {0: 'white', 1: 'PaleGreen1', 2: 'PaleGreen2', 3: 'SpringGreen1', 4: 'Green1', 5: 'Green2',
                    6: 'Green3', 7: 'Green4'}
        Y_colors = {0: 'white', 1: 'LightYellow1', 2: 'Cornsilk', 3: 'Khaki1', 4: 'Yellow1', 5: 'Yellow2',
                    6: 'Yellow3', 7: 'Goldenrod4'}
        B_colors = {0: 'white', 1: 'LightCyan1', 2: 'LightSkyBlue1', 3: 'SkyBlue1',
                    4: 'SteelBlue1', 6: 'RoyalBlue', 5: 'SteelBlue2', 7: 'Blue1'}
        R_colors = {0: 'Snow1', 1: 'LightSalmon1', 2: 'LightSalmon2', 3: 'Coral1', 4: 'OrangeRed1', 5: 'Red',
                    6: 'Firebrick3', 7: 'Red3'}
        show_color = []
        if self.color == 1:  # 蓝方探测能力 绿色
            show_color = G_colors
            a = self.convert_list(cellValue_list[0])
            # search_list =  add_searchValue(unit,search_dict,search_list,cellsize=10)
        if self.color == 2:  # 蓝方攻击空中能力 蓝色
            show_color = B_colors
            a = self.convert_list(cellValue_list[1])
        elif self.color == 3:  # 蓝方攻击地面能力 黄色
            show_color = Y_colors
            a = self.convert_list(cellValue_list[2])
        elif self.color == 4:  # 红方探测能力 绿色
            show_color = G_colors
            a = self.convert_list(cellValue_list[3])
        elif self.color == 5:  # 红方攻击空中能力 蓝色
            show_color = B_colors
            a = self.convert_list(cellValue_list[4])
        elif self.color == 6:  # 红方攻击地面能力 黄色
            show_color = Y_colors
            a = self.convert_list(cellValue_list[5])
        elif self.color == 7:  # 红方干扰能力 红色
            show_color = R_colors
            a = self.convert_list(cellValue_list[6])

        for i in range(self.hz_cells):  # 列hz_cells
            x = i * self.cell_size
            for j in range(self.vt_cells):  # 行vt_cells
                y = j * self.cell_size  #

                self.grid[i][j] = self.cv.create_rectangle(
                    x, y, x + self.cell_size, y + self.cell_size, fill=show_color[a[i][j]])
        if path_list:
            for p_list in path_list:
            # p_list =path_list[0]
                for m in range(len(p_list)):
                    i = p_list[m][0]
                    j = p_list[m][1]
                    y = i * self.cell_size
                    x = j * self.cell_size
                    self.grid[i][j] = self.cv.create_rectangle(
                        x, y, x + self.cell_size, y + self.cell_size, fill='black')

    # 选中某个网格触发事件
    def select_start_node(self, event):
        """ Change the color of the rectangle closest to x,y of event. """
        x = self.cv.canvasx(event.x)
        y = self.cv.canvasy(event.y)
        selected_rect = self.cv.find_closest(x, y)
        if selected_rect:
            self.cv.itemconfigure(selected_rect, fill='red1')  # Change color.

#计算现有导弹分布情况
def cal_bombers_weapons(obs):
    bombers_dic = {}  # 轰炸机{'轰炸机id'：{x：,y: ,导弹数： ,}}
    for unit in obs['units']:
        if unit['LX'] == 15 and unit['WP']['360']:
            i, j = calc_cell_position(unit['X'], unit['Y'])
            i = int(i)
            j = int(j)
            point = (j, i)
            bombers_dic[unit['ID']] = {'pos': point, 'num': unit['WP']['360']}  #
    if obs['airports'][0]['BOM']:
        point = (17, 32)
        bombers_dic['air'] = {'pos': point, 'num': obs['airports'][0]['BOM'] * 2}
    return bombers_dic

#计算需要的导弹数量
def cal_commandNeedWeapons(obs):
    com_dict ={}
    num = 0
    for unit in obs['qb']:
        if unit['LX'] == 41:
            i, j = calc_cell_position(unit['X'], unit['Y'])
            i = int(i)
            j = int(j)
            point = (j, i)
            if unit['DA'] == 0:
                num = 4
            elif unit['DA'] == 25:
                num = 3
            elif unit['DA'] == 50:
                num = 2
            elif unit['DA'] == 75:
                num = 1
            com_dict[point] = num
    return com_dict



all_dict = {
    'search': {
        11: 100000,  # 歼击机
        12: 250000,  # 预警机
        13: 60000,  # 干扰机
        14: 40000,  # 无人侦察机
        15: 100000,  # 轰炸机
        21: 180000,  # 护卫舰
        31: 100000,  # 地面防空
        32: 180000  # 地面雷达
    },
    'interfere': {
        13: 60000  # 干扰机
    },
    'attack': {
        11: 80000,  # 歼击机
        15: 80000,  # 轰炸机
        21: 100000,  # 护卫舰
        31: 100000  # 地面防空
    }
}

'''
unit:红方或蓝方单元
search_dict: 探测字典，key为LX，value为探测半径
search_list: 返回的结果，探测列表（二维）
cellsize: 格网大小 单位km
'''


def add_searchValue(unit, search_dict, search_list, interfere_list, cellsize=10):
    if unit['LX'] in [12, 13, 14, 21, 32]:
        '''
        12预警机探测250km，角度360°
        13干扰机探测60km，角度360°
        14无人侦察探测40km，角度360°
        21护卫舰探测180km，角度360°
        32地面雷达探测180km，角度360°
        '''
        search_list = search_Func(unit, search_dict, search_list)
    elif unit['LX'] in [11, 15, 31]:
        '''
        11歼击机探测100km，角度120° 攻击距离80km 满额导弹数6
        15轰炸机探测100km，角度120°
        31地面防空探测100km，角度120°
        '''
        search_list = search_Func(unit, search_dict, search_list, angle=120)
    for i in range(len(interfere_list)):
        for j in range(len(interfere_list[i])):
            if interfere_list[i][j]:
                search_list[i][j] = 0
    return search_list


'''
unit:红方或蓝方单元
interfere_dict: 探测字典，key为LX，value为干扰半径
interfere_list: 返回的结果，干扰列表（二维）
cellsize: 格网大小 单位km
'''


def add_interfereValue(unit, interfere_dict, interfere_list, cellsize=10):
    if unit['LX'] == 13:
        interfere_list = interfere_Func(unit, interfere_dict, interfere_list)
    return interfere_list


'''
unit:红方或蓝方单元
attack_dict: 探测字典，key为LX，value为对空攻击半径
attack_air_list: 返回的结果，对空毁伤列表（二维）
cellsize: 格网大小 单位km
'''


def add_attack_Air(unit, attack_dict, attack_air_list, cellsize=10):
    '''''
    11歼击机   攻击距离80km 满额导弹数6 攻击角度360°
    15轰炸机   攻击距离80km 满额导弹数2 攻击角度360°
    31地面防空 攻击距离100km 满额导弹数12 攻击角度120° 火力通道3
    21护卫舰   攻击距离100km 满额导弹数36 攻击角度360° 火力通道4
    '''''
    if unit['LX'] in [11, 21]:
        attack_air_list = attack_air_Func(unit, attack_dict, attack_air_list)
    elif unit['LX'] in [31]:
        attack_air_list = attack_air_Func(unit, attack_dict, attack_air_list, angle=120)
    return attack_air_list


'''
unit:红方或蓝方单元
attack_dict: 探测字典，key为LX，value为对空攻击半径
attack_land_list: 返回的结果，对地毁伤列表（二维）
cellsize: 格网大小 单位km
'''


def add_attack_Land(unit, attack_dict, attack_land_list, cellsize=10):
    if unit['LX'] in [15]:
        attack_land_list = attack_land_Func(unit, attack_dict, attack_land_list)
    return attack_land_list


'''对地攻击函数'''


def attack_land_Func(unit, attack_dict, attack_land_list, cellsize=10000):
    x = unit['X']
    y = unit['Y']
    i, j = calc_cell_position(x, y)  ##计算该单位所处的单元格位置
    px_x, px_y = calc_position_fromRowColumn(i, j)  # 根据单位格位置反求像素位置

    row_lu = int(i - attack_dict[unit['LX']] / cellsize)
    column_lu = int(j - attack_dict[unit['LX']] / cellsize)  # 左上角顶点行列号

    row_rd = int(i + attack_dict[unit['LX']] / cellsize) + 1
    column_rd = int(j + attack_dict[unit['LX']] / cellsize) + 1  # 右下角顶点行列号
    for m in range(row_lu, row_rd):
        if m < 0 or m >= 350000 / cellsize: continue
        for n in range(column_lu, column_rd):
            if n < 0 or n >= 350000 / cellsize: continue
            px_fx, px_fy = calc_position_fromRowColumn(m, n)
            distance = calc_distance(px_x, px_y, px_fx, px_fy)
            if distance < attack_dict[unit['LX']]:
                attack_land_list[m][n] += 1
    return attack_land_list


'''对空攻击函数'''


def attack_air_Func(unit, attack_dict, attack_air_list, angle=360, cellsize=10000):
    x = unit['X']
    y = unit['Y']
    i, j = calc_cell_position(x, y)  ##计算该单位所处的单元格位置
    px_x, px_y = calc_position_fromRowColumn(i, j)  # 根据单位格位置反求像素位置

    row_lu = int(i - attack_dict[unit['LX']] / cellsize)
    column_lu = int(j - attack_dict[unit['LX']] / cellsize)  # 左上角顶点行列号

    row_rd = int(i + attack_dict[unit['LX']] / cellsize) + 1
    column_rd = int(j + attack_dict[unit['LX']] / cellsize) + 1  # 右下角顶点行列号
    for m in range(row_lu, row_rd):
        if m < 0 or m >= 350000 / cellsize: continue
        for n in range(column_lu, column_rd):
            if n < 0 or n >= 350000 / cellsize: continue
            px_fx, px_fy = calc_position_fromRowColumn(m, n)
            if (angle_range(px_fx, px_fy, unit) and angle != 360) or angle == 360:
                distance = calc_distance(px_x, px_y, px_fx, px_fy)
                if distance < attack_dict[unit['LX']]:
                    attack_air_list[m][n] += 1
    return attack_air_list


'''干扰函数'''


def interfere_Func(unit, interfere_dict, interfere_list, cellsize=10000):
    x = unit['X']
    y = unit['Y']
    i, j = calc_cell_position(x, y)  ##计算该单位所处的单元格位置
    px_x, px_y = calc_position_fromRowColumn(i, j)  # 根据单位格位置反求像素位置

    row_lu = int(i - interfere_dict[unit['LX']] / cellsize)
    column_lu = int(j - interfere_dict[unit['LX']] / cellsize)  # 左上角顶点行列号

    row_rd = int(i + interfere_dict[unit['LX']] / cellsize) + 1
    column_rd = int(j + interfere_dict[unit['LX']] / cellsize) + 1  # 右下角顶点行列号
    for m in range(row_lu, row_rd):
        if m < 0 or m >= 350000 / cellsize: continue
        for n in range(column_lu, column_rd):
            if n < 0 or n >= 350000 / cellsize: continue
            px_fx, px_fy = calc_position_fromRowColumn(m, n)
            distance = calc_distance(px_x, px_y, px_fx, px_fy)
            if distance < interfere_dict[unit['LX']]:
                interfere_list[m][n] += 1
    return interfere_list


'''探测函数'''


def search_Func(unit, search_dict, search_list, angle=360, cellsize=10000):
    x = unit['X']
    y = unit['Y']
    i, j = calc_cell_position(x, y)  ##计算该单位所处的单元格位置
    px_x, px_y = calc_position_fromRowColumn(i, j)  # 根据单位格位置反求像素位置

    row_lu = int(i - search_dict[unit['LX']] / cellsize)
    column_lu = int(j - search_dict[unit['LX']] / cellsize)  # 左上角顶点行列号

    row_rd = int(i + search_dict[unit['LX']] / cellsize) + 1
    column_rd = int(j + search_dict[unit['LX']] / cellsize) + 1  # 右下角顶点行列号

    for m in range(row_lu, row_rd):
        if m < 0 or m >= 350000 / cellsize: continue
        for n in range(column_lu, column_rd):
            if n < 0 or n >= 350000 / cellsize: continue
            '''角度判断'''
            px_fx, px_fy = calc_position_fromRowColumn(m, n)
            if (angle_range(px_fx, px_fy, unit) and angle != 360) or angle == 360:
                distance = calc_distance(px_x, px_y, px_fx, px_fy)
                if distance < search_dict[unit['LX']]:
                    search_list[m][n] += 1
    return search_list


'''根据仿真坐标计算像素行列号'''


def calc_cell_position(x, y, cellsize=20):
    cordXY = coordConvert(x, y)  # 坐标转化
    i = cordXY[0] / cellsize
    j = cordXY[1] / cellsize
    return i, j


'''仿真坐标转为像素位置'''


def coordConvert(x, y, width=700, height=700, scale=500):
    convertXY = []
    convertX = x / scale + width / 2
    convertY = height / 2 - y / scale
    convertXY.append(convertX)
    convertXY.append(convertY)
    return convertXY


'''根据行列号反求像素位置'''


def calc_position_fromRowColumn(i, j, cellsize=20):
    x = i * cellsize + 1 / 2 * cellsize
    y = j * cellsize + 1 / 2 * cellsize
    return x, y


'''计算两个像素点之间的距离'''


def calc_distance(x_center, y_center, x1, y1, scale=500):
    distance = math.sqrt((x_center - x1) ** 2 + (y_center - y1) ** 2)
    return distance * scale


'''判断是否在角度范围之内'''


def angle_range(x, y, unit):
    delta_x = x - coordConvert(unit['X'], unit['Y'])[0]
    delta_y = y - coordConvert(unit['X'], unit['Y'])[1]
    HX = 0
    if delta_x > 0 and delta_y > 0:
        HX = math.atan(abs(delta_x) / abs(delta_y))
    elif delta_x > 0 and delta_y < 0:
        HX = math.pi - math.atan(abs(delta_x) / abs(delta_y))
    elif delta_x < 0 and delta_y < 0:
        HX = math.pi + math.atan(abs(delta_x) / abs(delta_y))
    elif delta_x < 0 and delta_y > 0:
        HX = math.pi * 2 - math.atan(abs(delta_x) / abs(delta_y))
    angle = HX / math.pi * 180
    min_angle = unit['HX'] - 60
    max_angle = unit['HX'] + 60
    if min_angle < 0:
        min_angle += 360.
        if angle in [0, max_angle] or angle in [min_angle, 360]:
            return True
        else:
            return False
    elif max_angle > 360:
        max_angle -= 360
        if angle in [0, max_angle] or angle in [min_angle, 360]:
            return True
        else:
            return False
    else:
        if angle in [min_angle, max_angle]:
            return True
        else:
            return False
# def main():
#     aa = [[0, 1, 2, 3, 4, 5, 6, 7] * 5 for i in range(35)]
#     a=[]
#     for i in range(7):
#         a.append(aa)
#
#     window = Window()
#     window.draw_grid()
#     window.root.mainloop()
#
#
# if __name__ == "__main__":
#     main()
