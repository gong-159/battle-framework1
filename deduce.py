from tkinter import *
import threading
import time
import sys
import PIL.Image as Image
import os
import math
import copy
import random

sys.setrecursionlimit(1000000)


# 依据间隔t，下一步状态位置，目前状态确定t之后的状态
def calculate_movePos(blue_unit, units_state, t):
    # delta_x, delta_y = [], []
    # print(units_state[blue_unit['ID']])  [(4606.82444, 6695.80619)]
    # [(-95000.0, 50000.0), (-65000.0, 50000.0), (-65000.0, 80000.0), (-95000.0, 80000.0)]
    X = units_state[blue_unit['ID']][0][0]
    Y = units_state[blue_unit['ID']][0][1]
    pre_x = blue_unit['X']
    pre_y = blue_unit['Y']
    if blue_unit['SP'] * t >= math.sqrt((Y - pre_y) ** 2 + (X - pre_x) ** 2):  # 如果飞过了，则飞到当前巡逻点，并将此点移至最后
        delta_x = (X - pre_x)
        delta_y = (Y - pre_y)
        units_state[blue_unit['ID']].append(units_state[blue_unit['ID']][0])
        units_state[blue_unit['ID']].remove(units_state[blue_unit['ID']][0])
    else:
        delta_x = (X - pre_x) * blue_unit['SP'] * t / math.sqrt((Y - pre_y) ** 2 + (X - pre_x) ** 2)
        delta_y = (Y - pre_y) * blue_unit['SP'] * t / math.sqrt((Y - pre_y) ** 2 + (X - pre_x) ** 2)
    blue_unit['X'] += delta_x
    blue_unit['Y'] += delta_y
    HX = 1
    if delta_x > 0 and delta_y > 0:
        HX = math.atan(abs(delta_x) / abs(delta_y))
    elif delta_x > 0 and delta_y < 0:
        HX = math.pi - math.atan(abs(delta_x) / abs(delta_y))
    elif delta_x < 0 and delta_y < 0:
        HX = math.pi + math.atan(abs(delta_x) / abs(delta_y))
    elif delta_x < 0 and delta_y > 0:
        HX = math.pi * 2 - math.atan(abs(delta_x) / abs(delta_y))
    HX = HX / math.pi * 180
    blue_unit['HX'] = HX

    # print(blue_unit['ID'],blue_unit['LX'],pre_x, pre_y, X, Y,delta_x,delta_y, blue_unit['X'], blue_unit['Y'])
    delta_x = delta_x / 500
    delta_y = delta_y / 500
    return delta_x, delta_y, blue_unit, units_state


# 按照航向前进-敌方位置
def cacucalt_move_xy(unit, t):
    HX = unit['HX']
    v = unit['SP']

    delta_x1 = math.sin(HX / 180 * math.pi) * v * t
    delta_y1 = math.cos(HX / 180 * math.pi) * v * t
    unit['X'] += delta_x1
    unit['Y'] += delta_y1
    delta_x = delta_x1 / 500
    delta_y = delta_y1 / 500
    return delta_x, delta_y, unit


# 计算巡逻矩形四个顶点
def calc(x_center, y_center, x1, y1, dir):
    angle = (90 - dir) / 180 * math.pi
    x_after = math.cos(angle) * (x1 - x_center) - math.sin(angle) * (y1 - y_center) + x_center
    y_after = math.sin(angle) * (x1 - x_center) + math.cos(angle) * (y1 - y_center) + y_center
    return x_after, y_after


# 计算巡逻位置
def caculate_position(unit, task):  # 巡逻
    # print(unit, task)
    # print('#######################')
    patrol_points = []
    p = []
    p_new = []
    if task['maintype'] in ['areahunt', 'takeoffareahunt']:
        length = task['area_len']
        width = task['area_wid']
    else:
        length = task['length']
        width = task['width']
    p.append([task['point_x'] - 1 / 2 * length, task['point_y'] - 1 / 2 * width])
    p.append([task['point_x'] + 1 / 2 * length, task['point_y'] - 1 / 2 * width])
    p.append([task['point_x'] + 1 / 2 * length, task['point_y'] + 1 / 2 * width])
    p.append([task['point_x'] - 1 / 2 * length, task['point_y'] + 1 / 2 * width])
    for i in range(4):
        p_new.append(calc(task['point_x'], task['point_y'], p[i][0], p[i][1], task['direction']))

    near_point = []
    near_dist = 99999999
    for p1 in p_new:  # 找到距离最近的点
        dist = math.sqrt((p1[0] - unit['X']) ** 2 + (p1[1] - unit['Y']) ** 2)
        if dist < near_dist:
            near_dist = dist
            near_point = p1
    if near_point == p_new[0]:
        patrol_points.append(p_new[0])
        patrol_points.append(p_new[1])
        patrol_points.append(p_new[2])
        patrol_points.append(p_new[3])
    elif near_point == p_new[1]:
        patrol_points.append(p_new[1])
        patrol_points.append(p_new[2])
        patrol_points.append(p_new[3])
        patrol_points.append(p_new[0])
    elif near_point == p_new[2]:
        patrol_points.append(p_new[2])
        patrol_points.append(p_new[3])
        patrol_points.append(p_new[0])
        patrol_points.append(p_new[1])
    elif near_point == p_new[3]:
        patrol_points.append(p_new[3])
        patrol_points.append(p_new[0])
        patrol_points.append(p_new[1])
        patrol_points.append(p_new[2])
    # if unit['X'] == patrol_points[0][0] and unit['Y'] == patrol_points[0][1]:
    #     patrol_points.append(patrol_points[0])
    #     patrol_points.remove(patrol_points[0])
    # patrol_points坐标转换
    # patrol_points_new =[]
    # for i in range(4):
    #     point = coordConvert(patrol_points[i][0],patrol_points[i][1])
    #     patrol_points_new.append(point)
    # print(patrol_points_new)
    return patrol_points  # [(-95000.0, 50000.0), (-65000.0, 50000.0), (-65000.0, 80000.0), (-95000.0, 80000.0)]


# def rockets_action(unit):
#     red_im = PhotoImage(file=picConfig['red'][unit["LX"]])
#     red_image = cv.create_image(coordConvert(unit["X"], unit["Y"])[0],
#                                 coordConvert(unit["X"], unit["Y"])[1],
#                                 image=red_im)  # 再加一个字典
#     rockets_units_images[red_unit["ID"]] = [red_im, red_image]
# 计算新起飞的飞机下一步状态
def caculate_state( blue_obs_deduce, deduce_obs_time, dict_actionToUnit,
                   units_state):  # ,blue_units_images,red_units_images
    #
    # for task in dict_actionToUnit:
    # if dict_actionToUnit[task]["maintype"] in  ['takeoffareapatrol', 'takeoff_inepatrol','takeoffareahunt', 'takeofftargethunt', 'takeoffprotect'] :
    # if task not in blue_units_images and task not in blue_obs_deduce['units'] :  # 起飞的新增图像
    #     NeedCreat =True
    #     for unit in blue_obs_deduce['units']:
    #         if task == unit['ID']:
    #             NeedCreat = False
    #             break
    #     if NeedCreat :
    #         red_units_images, blue_units_images, cv, blue_obs_deduce =add_model(cv,blue_obs_deduce,red_units_images,blue_units_images,dict_actionToUnit,task)
    #         print('新增图像')
    # print(blue_obs_deduce)

    for unit in blue_obs_deduce['units']:
        if unit['ID'] in units_state:
            continue
        if unit['ID'] in dict_actionToUnit:
            unit_task = dict_actionToUnit[unit['ID']]
            # print(unit_task)
            if unit_task['maintype'] in ['targethunt', 'takeofftargethunt']:  # 目标,以目标位置为下一时刻位置
                # print(red_obs_deduce)
                red_unit=[]
                for R_unit in blue_obs_deduce['qb']:
                    if unit_task['target_id'] == R_unit['ID']:
                        red_unit = R_unit
                        break
                # red_unit = red_obs_deduce[unit_task['target_id']]#111111111111111111111111111111111111
                if red_unit:
                    point = [(red_unit['X'], red_unit['Y'])]
                    units_state[unit['ID']] = point
                # print('目标')
                # print(units_state[unit['ID']])
                # [(4499.15487, -11822.91539)]
            elif unit_task['maintype'] in ['protect', 'takeoffprotect']:  # 护航
                blue_unit=[]
                for B_unit in blue_obs_deduce['units']:
                    if unit_task['cov_id'] == B_unit['ID']:
                        blue_unit = B_unit
                        break
                # red_unit = red_obs_deduce[unit_task['target_id']]#111111111111111111111111111111111111
                if blue_unit:
                    point = [(blue_unit['X'], red_unit['Y'])]
                    units_state[unit['ID']] = point
                # point=[(blue_unit['X'], blue_unit['Y'])]
                # units_state[unit['ID']] = point
                # print('航线')

            elif unit_task['maintype'] in ['area_patrol', 'takeoffareapatrol', 'areahunt', 'takeoffareahunt',
                                           'shipareapatrol', 'awcs_areapatrol', 'disturbareapatrol', 'uavareapatrol',
                                           'Ship_areapatrol']:  # 区域
                patrol_points = caculate_position(unit, unit_task)
                # print('区域')
                # print(unit,unit_task,patrol_points)
                units_state[unit['ID']] = patrol_points
                # print(units_state[unit['ID']])
                # [(-95000.0, -80000.0), (-65000.0, -80000.0), (-65000.0, -50000.0), (-95000.0, -50000.0)]
            elif unit_task['maintype'] in ['linepatrol', 'takeofflinepatrol', 'awcslinepatrol',
                                           'disturblinepatrol', 'uavlinepatrol']:  # 航线
                list_p = []
                for point in unit_task['area']['point_list']:
                    list_p.append([point['x'], point['y']])
                units_state[unit['ID']] = list_p
                print('line')
                print(units_state[unit['ID']])

            # print('下一时刻状态')

    return blue_obs_deduce, units_state


# 移动图像
def move_model(blue_obs_deduce, deduce_obs_time, units_state, t):
    # print(blue_obs_deduce)
    deduce_obs_time += t  # 推演的当前时间
    for blue_unit in blue_obs_deduce['units'] :
        if blue_unit['LX'] in [11, 12, 13, 14, 15, 18, 21] and blue_unit['ID'] in units_state:  # and blue_unit['ID'] in blue_units_images
            delta_x, delta_y, blue_unit, units_state = calculate_movePos(blue_unit, units_state, t)

    for red_unit in blue_obs_deduce['qb']:
        if red_unit['LX'] in [11, 12, 15, 21]:  # and red_unit['ID'] in red_units_images
            delta_x, delta_y, red_unit = cacucalt_move_xy(red_unit, t)


    return blue_obs_deduce, units_state, deduce_obs_time


# 加载模型
def creat_model(cv, obs_blue):
    red_units_images = {}
    blue_units_images = {}
    for red_unit in obs_blue['qb']:
        if red_unit["ID"] not in red_units_images:
            red_im = PhotoImage(file=picConfig['red'][red_unit["LX"]])
            red_image = cv.create_image(coordConvert(red_unit["X"], red_unit["Y"])[0],
                                        coordConvert(red_unit["X"], red_unit["Y"])[1],
                                        image=red_im)  # 再加一个字典
            red_units_images[red_unit["ID"]] = [red_im, red_image]
    for blue_unit in obs_blue['units']:
        if blue_unit['ID'] not in blue_units_images:
            blue_im = PhotoImage(file=picConfig["blue"][blue_unit["LX"]])
            blue_image = cv.create_image(coordConvert(blue_unit["X"], blue_unit["Y"])[0],
                                         coordConvert(blue_unit["X"], blue_unit["Y"])[1],
                                         image=blue_im)  # 再加一个字典
            blue_units_images[blue_unit["ID"]] = [blue_im, blue_image]
    return red_units_images, blue_units_images, cv

# 新增模型
def add_model(cv, blue_obs_deduce, red_units_images, blue_units_images, dict_actionToUnit, task):
    blue_id = task  # ID
    print(blue_id)
    if dict_actionToUnit[task]['maintype'] in ['takeoffareahunt', 'takeofftargethunt']:  # 轰炸机
        blue_im = PhotoImage(file='images/轰炸机_蓝方.png')
        blue_image = cv.create_image(coordConvert(-130870.0, -86854.0)[0], coordConvert(-130870.0, -86854.0)[1],
                                     image=blue_im)  # 再加一个字典
        # blue_id = random.randint(100-999)

        blue_units_images[blue_id] = [blue_im, blue_image]  # 图像的新增
        blue_obs_deduce['units'].append({"type": "TARGET",  # 态势信息新增
                                         "ID": blue_id,  # 平台编号
                                         "X": -130870.0,  # 平台位置x轴坐标(浮点型, 单位: 米, 下同)
                                         "Y": -86854.0,  # 平台位置y轴坐标
                                         "Z": 0,  # 平台位置z轴坐标
                                         "JB": 0,  # 军别(0-蓝方, 1-红方)
                                         "HX": 90.00052,  # 航向(浮点型, 单位: 度, [0-360])
                                         "SP": copy.deepcopy(dict_actionToUnit[task]['speed']),  # 速度(单位: 米/秒)
                                         "LX": 15,  # 平台类型(21-护卫舰)
                                         "XH": "Bpk",  # 型号
                                         "TMID": 6801,  # 所属编队号
                                         "SBID": 1,  # 该平台在编队内序号
                                         "TM": 0,  # 仿真时间
                                         "Locked": 0, "WH": 1, "DA": 0, "Hang": 100000.0, "Fuel": 10000.0, "ST": 41,
                                         "WP": {"360": 2}})  # 态势信息新增
    elif dict_actionToUnit[task]['maintype'] in ['takeoffprotect']:  # 歼击机
        blue_im = PhotoImage(file='images/ 歼击机_蓝方.png')
        blue_image = cv.create_image(coordConvert(-130870.0, -86854.0)[0], coordConvert(-130870.0, -86854.0)[1],
                                     image=blue_im)  # 再加一个字典
        blue_units_images[blue_id] = [blue_im, blue_image]  # 图像的新增
        blue_obs_deduce['units'].append({"type": "TARGET",  # 态势信息新增
                                         "ID": blue_id,  # 平台编号
                                         "X": -130870.0,  # 平台位置x轴坐标(浮点型, 单位: 米, 下同)
                                         "Y": -86854.0,  # 平台位置y轴坐标
                                         "Z": 0,  # 平台位置z轴坐标
                                         "JB": 0,  # 军别(0-蓝方, 1-红方)
                                         "HX": 90.00052,  # 航向(浮点型, 单位: 度, [0-360])
                                         "SP": copy.deepcopy(dict_actionToUnit[task]['speed']),  # 速度(单位: 米/秒)
                                         "LX": 11,  # 平台类型(21-护卫舰)
                                         "XH": "Bpk",  # 型号
                                         "TMID": 6801,  # 所属编队号
                                         "SBID": 1,  # 该平台在编队内序号
                                         "TM": 0,  # 仿真时间
                                         "Locked": 0, "WH": 1, "DA": 0, "Hang": 100000.0, "Fuel": 10000.0, "ST": 41,
                                         "WP": {"170": 6}})  # 态势信息新增
    else:
        if dict_actionToUnit[task]['fly_type'] == 11:  # 歼击机
            blue_im = PhotoImage(file='images/歼击机_蓝方.png')
            blue_image = cv.create_image(coordConvert(-130870.0, -86854.0)[0], coordConvert(-130870.0, -86854.0)[1],
                                         image=blue_im)  # 再加一个字典
            # blue_id = random.randint(100 - 999)
            # while True:
            #     if blue_id in blue_units_images:
            #         blue_id = random.randint(100 - 999)
            #     else:
            #         break
            blue_units_images[blue_id] = [blue_im, blue_image]  # 图像的新增
            blue_obs_deduce['units'].append({"type": "TARGET",  # 态势信息新增
                                             "ID": blue_id,  # 平台编号
                                             "X": -130870.0,  # 平台位置x轴坐标(浮点型, 单位: 米, 下同)
                                             "Y": -86854.0,  # 平台位置y轴坐标
                                             "Z": 0,  # 平台位置z轴坐标
                                             "JB": 0,  # 军别(0-蓝方, 1-红方)
                                             "HX": 90.00052,  # 航向(浮点型, 单位: 度, [0-360])
                                             "SP": copy.deepcopy(dict_actionToUnit[task]['speed']),  # 速度(单位: 米/秒)
                                             "LX": 11,  # 平台类型(21-护卫舰)
                                             "XH": "Bpk",  # 型号
                                             "TMID": 6801,  # 所属编队号
                                             "SBID": 1,  # 该平台在编队内序号
                                             "TM": 0,  # 仿真时间
                                             "Locked": 0, "WH": 1, "DA": 0, "Hang": 100000.0, "Fuel": 10000.0, "ST": 41,
                                             "WP": {"170": 6}})  # 态势信息新增

        elif dict_actionToUnit[task]['fly_type'] == 15:  # 轰炸机
            blue_im = PhotoImage(file='images / 轰炸机_蓝方.png')
            blue_image = cv.create_image(coordConvert(-130870.0, -86854.0)[0], coordConvert(-130870.0, -86854.0)[1],
                                         image=blue_im)  # 再加一个字典

            blue_units_images[blue_id] = [blue_im, blue_image]  # 图像的新增
            blue_obs_deduce['units'].append({"type": "TARGET",  # 态势信息新增
                                             "ID": blue_id,  # 平台编号
                                             "X": -130870.0,  # 平台位置x轴坐标(浮点型, 单位: 米, 下同)
                                             "Y": -86854.0,  # 平台位置y轴坐标
                                             "Z": 0,  # 平台位置z轴坐标
                                             "JB": 0,  # 军别(0-蓝方, 1-红方)
                                             "HX": 90.00052,  # 航向(浮点型, 单位: 度, [0-360])
                                             "SP": copy.deepcopy(dict_actionToUnit[task]['speed']),  # 速度(单位: 米/秒)
                                             "LX": 15,  # 平台类型(21-护卫舰)
                                             "XH": "Bpk",  # 型号
                                             "TMID": 6801,  # 所属编队号
                                             "SBID": 1,  # 该平台在编队内序号
                                             "TM": 0,  # 仿真时间
                                             "Locked": 0, "WH": 1, "DA": 0, "Hang": 100000.0, "Fuel": 10000.0, "ST": 41,
                                             "WP": {"360": 2}})  # 态势信息新增
    return red_units_images, blue_units_images, cv, blue_obs_deduce




def angle_range(point, unit):
    delta_x = point[0] - unit['X']
    delta_y = point[1] - unit['Y']

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


# 删除模型
def delete_model(cv, blue_obs_deduce, red_units_images, blue_units_images, unit):
    del blue_units_images[unit['ID']]  # 删掉图像
    blue_obs_deduce['units'][:] = [d for d in blue_obs_deduce['units'] if d.get('ID') != unit['ID']]  # 删除unit


# 坐标转化
def coordConvert(x, y, width=700, height=700, scale=500):
    convertXY = []
    convertX = x / scale + width / 2
    convertY = height / 2 - y / scale
    convertXY.append(convertX)
    convertXY.append(convertY)
    return convertXY


# 图像字典
picConfig = {
    'red': {
        11: 'images/歼击机_红方.png',
        12: 'images/预警机_红方.png',
        13: 'images/干扰机_红方.png',
        14: 'images/无人侦察机_红方.png',
        15: 'images/轰炸机_红方.png',
        21: 'images/驱逐舰_红方.png',
        # 31: 'images/歼击机_红方.png', ##地面防空
        32: 'images/雷达_红方.png',
        # 41: 'images/歼击机_红方.png', ##指挥所
        42: 'images/机场_红方.png',
        18: 'images/歼击机_红方.png',  ##未知空中目标
        19: '',  ##民航
        28: 'images/驱逐舰_红方.png',  ##未知水面目标
        29: ''  ##民船
    },
    'blue': {
        11: 'images/歼击机_蓝方.png',
        12: 'images/预警机_蓝方.png',
        # '13': 'images/歼击机_红方.png',
        # '14': 'images/歼击机_红方.png',
        15: 'images/轰炸机_蓝方.png',
        21: 'images/驱逐舰_蓝方.png',
        31: 'images/地防_蓝方.png',
        32: 'images/雷达_蓝方.png',
        41: 'images/指挥所_蓝方.png',
        42: 'images/机场_蓝方.png',
        # '18': 'images/歼击机_红方.png',
        # '19': 'images/歼击机_红方.png',
        # '28': 'images/歼击机_红方.png',
        # '29': 'images/歼击机_红方.png'
    }
}
# if __name__ == '__main__':
#     main()
# 871 11 -99891.27575564341 -71665.9236651305 -65000.0 -50000.0 1061.923776018764 659.4072292036606 -98829.35197962464 -71006.51643592684
# 108 11 -118348.04979909392 -71291.22435775415 -65000.0 20000.0 504.7726889950592 863.786342223469 -117843.27711009886 -70427.43801553069
# 871 11 -18672.88414221325 -14039.326384189912 -65000.0 -50000.0 -987.4286390638551 -766.475493904732 -19660.312781277105 -14805.801878094644
