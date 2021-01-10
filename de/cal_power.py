import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import math

all_dict={
    'search':{
        11: 100,#歼击机
        12: 250,#预警机
        13: 60,#干扰机
        14: 40,#无人侦察机
        15: 100,#轰炸机
        21: 180,#护卫舰
        31: 100,#地面防空
        32: 180#地面雷达
    },
    'interfere':{
        13: 60#干扰机
    },
    'attack':{
        11: 80,#歼击机
        15: 80,#轰炸机
        21: 100,#护卫舰
        31: 100#地面防空
    }
}
search = [[0]*35 for i in range(35)]
search_dict = all_dict['search'][11]
a=1

'''
unit:红方或蓝方单元
search_dict: 探测字典，key为LX，value为探测半径
search_list: 返回的结果，探测列表（二维）
cellsize: 格网大小 单位km
'''
def add_searchValue(unit,search_dict,search_list,cellsize=10):
    if unit['LX'] in [12,13,14,21,32]:
        '''
        12预警机探测250km，角度360°
        13干扰机探测60km，角度360°
        14无人侦察探测40km，角度360°
        21护卫舰探测180km，角度360°
        32地面雷达探测180km，角度360°
        '''
        search_Func(unit,search_dict,search_list)
    elif unit['LX'] in[11,15,31]:
        '''
        11歼击机探测100km，角度120° 攻击距离80km 满额导弹数6
        15轰炸机探测100km，角度120°
        31地面防空探测100km，角度120°
        '''
        search_Func(unit, search_dict, search_list,angle=120)
    return search_list
        # if i-25 < 0 and j-25 >= 0:#超界 左上
        #     for m in range(0,i):
        #         for n in range(j-25,j):
        #             px_fx,px_fy=calc_position_fromRowColumn(m,n)
        #             distance=calc_distance(px_x,px_y,px_fx,px_fy)
        #             if distance < 250000:
        #                 '''进行属性增加'''
        # elif i-25 >= 0 and j-25 <0:
        #     for m in range(i-       25,i):
        #         for n in range(0,j):
        #             px_fx,px_fy=calc_position_fromRowColumn(m,n)
        #             distance=calc_distance(px_x,px_y,px_fx,px_fy)
        #             if distance < 250000:
        #                 '''进行属性增加'''
        # elif i-25 < 0 and j-25 < 0:
        #     for m in range(0,i):
        #         for n in range(0,j):
        #             px_fx,px_fy=calc_position_fromRowColumn(m,n)
        #             distance=calc_distance(px_x,px_y,px_fx,px_fy)
        #             if distance < 250000:
        #                 '''进行属性增加'''
        # elif i-25 >= 0 and j-25 >= 0:
        #     for m in range(i-25,i):
        #         for n in range(j-25,j):
        #             px_fx,px_fy=calc_position_fromRowColumn(m,n)
        #             distance=calc_distance(px_x,px_y,px_fx,px_fy)
        #             if distance < 250000:
        #                 '''进行属性增加'''
        #
        # if i-25 <0 and j + 25 >=35:
        #     for m in range(0,i):
        #         for n in range(j,35):
        #             px_fx,px_fy=calc_position_fromRowColumn(m,n)
        #             distance=calc_distance(px_x,px_y,px_fx,px_fy)
        #             if distance < 250000:
        #                 '''进行属性增加'''

'''
unit:红方或蓝方单元
interfere_dict: 探测字典，key为LX，value为干扰半径
interfere_list: 返回的结果，干扰列表（二维）
cellsize: 格网大小 单位km
'''
def add_interfereValue(unit,interfere_dict,interfere_list,cellsize=10):
    if unit['LX'] == 13:
        interfere_Func(unit,interfere_dict,interfere_list)
    return interfere_list

'''
unit:红方或蓝方单元
attack_dict: 探测字典，key为LX，value为对空攻击半径
attack_air_list: 返回的结果，对空毁伤列表（二维）
cellsize: 格网大小 单位km
'''
def add_attack_Air(unit,attack_dict,attack_air_list,cellsize=10):
    '''''
    11歼击机   攻击距离80km 满额导弹数6 攻击角度360°
    15轰炸机   攻击距离80km 满额导弹数2 攻击角度360°
    31地面防空 攻击距离100km 满额导弹数12 攻击角度120° 火力通道3
    21护卫舰   攻击距离100km 满额导弹数36 攻击角度360° 火力通道4
    '''''
    if unit['LX'] in [11,21]:
        attack_air_Func(unit,attack_dict,attack_air_list)
    elif unit['LX'] in [31]:
        attack_air_Func(unit, attack_dict, attack_air_list,angle=120)
    return attack_air_list

'''
unit:红方或蓝方单元
attack_dict: 探测字典，key为LX，value为对空攻击半径
attack_land_list: 返回的结果，对地毁伤列表（二维）
cellsize: 格网大小 单位km
'''
def add_attack_Land(unit,attack_dict,attack_land_list,cellsize=10):
    if unit['LX'] in [15]:
        attack_land_Func(unit,attack_dict,attack_land_list)
    return attack_land_list

'''对地攻击函数'''
def attack_land_Func(unit,attack_dict,attack_land_list,cellsize=10):
    x = unit['X']
    y = unit['Y']
    i, j = calc_cell_position(x, y)  ##计算该单位所处的单元格位置
    px_x, px_y = calc_position_fromRowColumn(i, j)  # 根据单位格位置反求像素位置

    row_lu = i - attack_dict[unit['LX']] / cellsize
    column_lu = j - attack_dict[unit['LX']] / cellsize  # 左上角顶点行列号

    row_rd = i + attack_dict[unit['LX']] / cellsize
    column_rd = j + attack_dict[unit['LX']] / cellsize  # 右下角顶点行列号
    for m in range(row_lu, row_rd):
        if m < 0 or m > 350 / cellsize: continue
        for n in range(column_lu, column_rd):
            if n < 0 or m > 350 / cellsize: continue
            px_fx, px_fy = calc_position_fromRowColumn(m, n)
            distance = calc_distance(px_x, px_y, px_fx, px_fy)
            if distance < attack_dict[unit['LX']]:
                attack_land_list[m][n] += 1

'''对空攻击函数'''
def attack_air_Func(unit,attack_dict,attack_air_list,angle=360,cellsize=10):
    x = unit['X']
    y = unit['Y']
    i, j = calc_cell_position(x, y)  ##计算该单位所处的单元格位置
    px_x, px_y = calc_position_fromRowColumn(i, j)  # 根据单位格位置反求像素位置

    row_lu = i - attack_dict[unit['LX']] / cellsize
    column_lu = j - attack_dict[unit['LX']] / cellsize  # 左上角顶点行列号

    row_rd = i + attack_dict[unit['LX']] / cellsize
    column_rd = j + attack_dict[unit['LX']] / cellsize  # 右下角顶点行列号
    for m in range(row_lu, row_rd):
        if m < 0 or m > 350 / cellsize: continue
        for n in range(column_lu, column_rd):
            if n < 0 or m > 350 / cellsize: continue
            px_fx, px_fy = calc_position_fromRowColumn(m, n)
            if (angle_range(px_fx, px_fy, unit) and angle != 360) or angle == 360:
                distance = calc_distance(px_x, px_y, px_fx, px_fy)
                if distance < attack_dict[unit['LX']]:
                    attack_air_list[m][n] += 1

'''干扰函数'''
def interfere_Func(unit,interfere_dict,interfere_list,cellsize=10):
    x = unit['X']
    y = unit['Y']
    i, j = calc_cell_position(x, y)  ##计算该单位所处的单元格位置
    px_x, px_y = calc_position_fromRowColumn(i, j)  # 根据单位格位置反求像素位置

    row_lu = i - interfere_dict[unit['LX']] / cellsize
    column_lu = j - interfere_dict[unit['LX']] / cellsize  # 左上角顶点行列号

    row_rd = i + interfere_dict[unit['LX']] / cellsize
    column_rd = j + interfere_dict[unit['LX']] / cellsize  # 右下角顶点行列号
    for m in range(row_lu, row_rd):
        if m < 0 or m > 350 / cellsize: continue
        for n in range(column_lu, column_rd):
            if n < 0 or m > 350 / cellsize: continue
            px_fx, px_fy = calc_position_fromRowColumn(m, n)
            distance = calc_distance(px_x, px_y, px_fx, px_fy)
            if distance < interfere_dict[unit['LX']]:
                interfere_list[m][n] += 1

'''探测函数'''
def search_Func(unit,search_dict,search_list,angle=360,cellsize=10):
    x = unit['X']
    y = unit['Y']
    i, j = calc_cell_position(x, y)  ##计算该单位所处的单元格位置
    px_x, px_y = calc_position_fromRowColumn(i, j)  # 根据单位格位置反求像素位置

    row_lu = int(i - search_dict[unit['LX']] / cellsize)
    column_lu =int(j - search_dict[unit['LX']] / cellsize)   # 左上角顶点行列号

    row_rd =int(i + search_dict[unit['LX']] / cellsize)
    column_rd = int(j + search_dict[unit['LX']] / cellsize)  # 右下角顶点行列号

    for m in range(row_lu, row_rd):
        if m < 0 or m > 350 / cellsize: continue
        for n in range(column_lu, column_rd):
            if n < 0 or m > 350 / cellsize: continue
            '''角度判断'''
            px_fx, px_fy = calc_position_fromRowColumn(m, n)
            if (angle_range(px_fx,px_fy,unit) and angle!=360) or angle == 360:
                distance = calc_distance(px_x, px_y, px_fx, px_fy)
                if distance < search_dict[unit['LX']]:
                    search_list[m][n] += 1


'''根据仿真坐标计算像素行列号'''
def calc_cell_position(x,y,cellsize=20):
    cordXY=coordConvert(x,y)# 坐标转化
    i = cordXY[0]/cellsize
    j = cordXY[1]/cellsize
    return i,j
'''仿真坐标转为像素位置'''
def coordConvert(x, y, width=700, height=700, scale=500):
    convertXY = []
    convertX = x / scale + width / 2
    convertY = height / 2 - y / scale
    convertXY.append(convertX)
    convertXY.append(convertY)
    return convertXY
'''根据行列号反求像素位置'''
def calc_position_fromRowColumn(i,j,cellsize=20):
    x = i*cellsize +1/2*cellsize
    y = j*cellsize+ 1/2*cellsize
    return x,y
'''计算两个像素点之间的距离'''
def calc_distance(x_center,y_center,x1,y1,scale=500):
    distance=math.sqrt((x_center-x1)**2+(y_center-y1)**2)
    return distance*scale
'''判断是否在角度范围之内'''
def angle_range(x,y,unit):
    delta_x=x-coordConvert(unit['X'],unit['Y'])[0]
    delta_y=y-coordConvert(unit['X'],unit['Y'])[1]

    if delta_x > 0 and delta_y > 0:
        HX = math.atan(abs(delta_x) / abs(delta_y))
    elif delta_x > 0 and delta_y < 0:
        HX = math.pi - math.atan(abs(delta_x) / abs(delta_y))
    elif delta_x < 0 and delta_y < 0:
        HX = math.pi + math.atan(abs(delta_x) / abs(delta_y))
    elif delta_x < 0 and delta_y > 0:
        HX = math.pi * 2 - math.atan(abs(delta_x) / abs(delta_y))
    angle = HX / math.pi * 180
    min_angle = unit['HX']-60
    max_angle = unit['HX']+60
    if min_angle<0:
        min_angle+=360.
        if angle in [0,max_angle] or angle in [min_angle,360]:
            return True
        else:
            return False
    elif max_angle>360:
        max_angle-=360
        if angle in [0, max_angle] or angle in [min_angle, 360]:
            return True
        else:
            return False
    else:
        if angle in [min_angle,max_angle]:
            return  True
        else:
            return False