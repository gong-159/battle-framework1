import argparse
import threading
import time
import json
import sys
import tkinter
from env.env_client import EnvClient
from env.env_cmd import EnvCmd
from env.env_runner import EnvRunner
from tkinter import *
import deduce
import copy
import datetime
import math
from de.tk_window import Window
# from agent.red_rule_agent import RedRuleAgent
# from agent.blue_rule_agent import BlueRuleAgent
from agent.saidui0252a.saidui0252a_red import RedRuleAgent
from agent.saidui0252a.saidui0252a_blue import BlueRuleAgent
from record.attach2docker import net_todocker_init

sys.setrecursionlimit(1000000)
blue_obs = []  # 蓝色方态势 以蓝色方视角
red_obs = []  # 红色方态势
obs_time = []  # 态势时间
actions_red = []  # 红色方态势指令
actions_blue = []  # 蓝色方态势指令
dict_actionToUnit = {}  # 指令对应的unit
need_pause = False
num_c=0
def connect_loop(rpyc_port):
    """根据映射出来的宿主机端口号rpyc_port，与容器内的仿真平台建立rpyc连接"""
    while True:
        try:
            env_client = EnvClient('127.0.0.1', rpyc_port)
            observation = env_client.get_observation()
            if len(observation['red']['units']) != 0:
                return env_client

        except Exception as e:
            print(e)
            print("rpyc connect failed")

        time.sleep(3)


def print_info(units):
    for unit in units:
        if unit['LX'] != 41:
            i = 1
            # print('id: {:3d}, tmid: {:4d}, speed: {:3.0f}, x: {:6.0f}, y: {:6.0f}, z: {:5.0f}, '
            #       'type: {:3d}, state: {:3d}, alive: {:2d}, hang: {:3.0f}'.format
            #       (unit['ID'], unit['TMID'], unit['SP'], unit['X'], unit['Y'], unit['Z'],
            #        unit['LX'], unit['ST'], unit['WH'], unit['Hang']))


class WarRunner(EnvRunner):

    def __init__(self, env_id, server_port, agents, config, replay):
        EnvRunner.__init__(self, env_id, server_port, agents, config, replay)  # 仿真环境初始化

    def _run_env(self):
        time.sleep(1)

    def run(self, num_episodes, speed):
        global blue_obs
        global red_obs
        global obs_time
        global actions_blue
        global actions_red
        global dict_actionToUnit
        global need_pause
        """对战调度程序"""
        # 启动仿真环境, 与服务端建立rpyc连接
        self._start_env()
        self.env_client = connect_loop(self.env_manager.get_server_port())

        self.env_client.take_action([EnvCmd.make_simulation("SPEED", "", speed)])

        f = open("state.json", "w")
        battle_results = [0, 0, 0]  # [红方获胜局数, 平局数量, 蓝方获胜局数]
        for i in range(num_episodes):
            num_frames = 0
            sim_time = 0  # 记录容器或者程序崩溃时的仿真时间
            self._reset()
            self._run_env()

            # 开启记录本轮数据的两个线程
            if self.save_replay:
                data_port = self.env_manager.get_data_port()
                folder = self.replay_dir
                net_todocker_init('127.0.0.1', data_port, self.agents[0].name, self.agents[1].name, i, folder)
            # red_last=[]
            # rockets_lists={}
            # f = True
            while True:
                try:
                    num_frames += 1
                    observation = self._get_observation()  # 获取态势
                    sim_time = observation['sim_time']
                    # print(i + 1, sim_time)
                    # 获取各种推测态势信息
                    obs_time = sim_time
                    # f = True
                    # if sim_time>=300 and sim_time<=310 and f:
                    #     f = False
                    #     print(sim_time)
                    #     # self.env_manager.stop()
                    #     self.env_client.take_action([EnvCmd.make_simulation('PAUSE','', 0)])
                    #     time.sleep(10)
                    #     print('10秒后')
                    #     self.env_client.take_action([EnvCmd.make_simulation('PAUSE', '', -1)])
                    if need_pause:
                        self.env_client.take_action([EnvCmd.make_simulation('PAUSE', '', 0)])
                    red_obs = observation['red']
                    blue_obs = observation['blue']
                    actions_red = self._get_actions_red()
                    actions_blue = self._get_actions_blue()
                    caculate_TaskObject(red_obs) #更新任务-对象字典
                    # rockets_lists = rockets_hitRate(red_obs, red_last, rockets_lists)
                    print_info(observation['red']['units'])

                    done = self._get_done(observation)  # 推演结束(分出胜负或达到最大时长)
                    if len(observation['red']['rockets']) > 0:
                        # 写入所得的json会在同一行里, 打开文件后按Ctrl+Alt+L可自动转换成字典格式
                        f.write(json.dumps(observation, ensure_ascii=False))
                    self._run_agents(observation)  # 发送指令

                    if done[0]:  # 对战结束后环境重置
                        # 统计胜负结果
                        if done[1] == 0 or done[2] == 0:
                            battle_results[1] += 1
                        if done[1] == 1:
                            battle_results[0] += 1
                        if done[2] == 1:
                            battle_results[2] += 1
                        # 环境重置
                        self.env_manager.reset()
                        self.env_client = connect_loop(self.env_manager.get_server_port())
                        self.env_client.take_action([EnvCmd.make_simulation("SPEED", "", speed)])
                        break
                    self._run_env()
                except Exception as e:
                    print(e)
                    print("容器运行出现异常需要重启")
                    # 记录错误信息
                    self.logger.debug("第{}局程序运行{}秒后出错, 错误信息为: {}\n".format(i + 1, sim_time, e))
                    self._start_env()
                    self.env_client = connect_loop(self.env_manager.get_server_port())
                    self.env_client.take_action([EnvCmd.make_simulation("SPEED", "", speed)])
                    break
        # 关闭文件
        f.close()
        return battle_results


config = {
    'server_port': 6100,
    'config': {
        'scene_name': '/home/Joint_Operation_scenario.ntedt',  # 容器里面想定文件绝对路径
        'prefix': './',  # 容器管理的脚本manage_client所在路径(这里给的相对路径)
        'image_name': 'combatmodserver:v1.4',  # 镜像名
        'volume_list': [],
        'max_game_len': 350  # 最大决策次数
    },
    'agents': {
        'red_name': {  # 战队名
            'class': RedRuleAgent,  # 智能体类名
            'side': 'red'  # 智能体所属军别(不可更改!)
        },
        'blue_name': {  # 战队名
            'class': BlueRuleAgent,  # 智能体类名
            'side': 'blue'  # 智能体所属军别(不可更改!)
        }
    },
    'replay': {  # 记录回放相关设置
        'save_replay': False,  # 是否记录
        'replay_dir': './replays'  # 回放保存路径
    }
}


def main(env_id, num_episodes, speed):
    """根据环境编号env_id、对战轮数num_episodes和配置config, 构建并运行仿真环境"""
    dg_runner = WarRunner(env_id, **config)

    results = dg_runner.run(num_episodes, speed)
    print('battle results: {}'.format(results))

def rockets_hitRate(red_obs,red_last,rockets_lists):#
    R_list = []
    if rockets_lists:
        for rocket in  red_obs['rockets']:#蓝方发射的导弹
            print(rocket['ID'])
            if rocket in rockets_lists: #添加导弹信息rocket['ID']
                print('2')
            else:
                for unit in red_obs['units']:
                    if unit['ID'] == rocket['N2']:
                        t_x = unit['X']
                        t_y = unit['Y']
                        x = rocket['X']
                        y = rocket['Y']
                        dist = math.sqrt((x - t_x) ** 2 + (y - t_y) ** 2)

                        rockets_lists[rocket['ID']] = [dist,0,rocket['N2']]#距离 是否命中 目标
                        break
        #判断导弹是否爆炸
        for rocker in rockets_lists:
            explode = True
            for r1 in  red_obs['rockets']:
                if rocker == r1['ID']:
                    explode=False
            if explode:
                #判断是否击中
                hit = True
                for unit in red_obs:
                    if rocker[2] == unit['ID']:#未命中
                        hit =False
                        break
                if hit:
                    for unit in red_last:
                        if rocker[2] == unit['ID']:  # 命中
                            rockets_lists[rocker][1] = 1
                            break
    else:
        if red_obs['rockets']:
            for rocket in red_obs['rockets']:  # 蓝方发射的导弹
                for unit in red_obs['units']:
                    if unit['ID'] == rocket['N2']:
                        t_x = unit['X']
                        t_y = unit['Y']
                        x = rocket['X']
                        y = rocket['Y']
                        dist = math.sqrt((x - t_x) ** 2 + (y - t_y) ** 2)
                        rockets_lists[rocket['ID']] = [dist, 0, rocket['N2']]  # 距离 是否命中 目标
                        break
    return rockets_lists

def helloCallBack(window):
    global blue_obs
    global red_obs
    global obs_time
    global actions_red
    global actions_blue
    global need_pause

    need_pause = True
    blue_obs_deduce = copy.deepcopy(red_obs)#red_obs
    # red_units_images, blue_units_images, window.cv = deduce.creat_model(window.cv, blue_obs_deduce)  # 加开始按钮
    units_state = {}
    deduce_obs_time = obs_time
    window.root.after(10,refresh(window, blue_obs_deduce, units_state,deduce_obs_time))  #red_obs['qb']
    # window.root.after(10,
    #            refresh(window, red_units_images, blue_units_images, blue_obs_deduce, blue_obs['qb'], units_state,
    #                    deduce_obs_time))


def show_deduce():
    global blue_obs
    global red_obs
    global obs_time
    global actions_red
    global actions_blue



    # print(blue_obs_deduce['units'])
    root = Tk()
    root.attributes("-alpha", 0.1)
    root.geometry('700x800')

    w = tkinter.Label(root, text="Time:",font=("宋体", 16, "bold"),width=30, height=2)
    w.pack()
    text = tkinter.Text(font=("宋体", 16, "bold"),width=15, height=1)
    text.place(x=430,y=10)
    # text.pack()
    cv = Canvas(root, background='white', width=700, height=700)
    cv.pack()
    backim = PhotoImage(file="images/背景.png")
    cv.create_image(375, 400, image=backim)
    B = tkinter.Button( text="开始", width=15, height=2,command=lambda :helloCallBack(cv,root,text))
    B.pack()
    root.mainloop()
def show_deduce_new():
    global blue_obs
    global red_obs
    global obs_time
    global actions_red
    global actions_blue

    window = Window()
    # window.draw_grid()
    # window.B = tkinter.Button(text="开始", width=15, height=2)
    window.B = tkinter.Button( text="开始", width=15, height=2,command=lambda :helloCallBack(window))#cv,root,text
    window.B.pack()
    window.root.mainloop()

    # print(blue_obs_deduce['units'])
    root = Tk()
    root.attributes("-alpha", 0.1)
    root.geometry('700x800')

    w = tkinter.Label(root, text="Time:",font=("宋体", 16, "bold"),width=30, height=2)
    w.pack()
    text = tkinter.Text(font=("宋体", 16, "bold"),width=15, height=1)
    text.place(x=430,y=10)
    # text.pack()
    cv = Canvas(root, background='white', width=700, height=700)
    cv.pack()
    backim = PhotoImage(file="images/背景.png")
    cv.create_image(375, 400, image=backim)
    B = tkinter.Button( text="开始", width=15, height=2,command=lambda :helloCallBack(cv,root,text))
    B.pack()
    root.mainloop()

def caculate_TaskObject(obs):#获取任务的对象
    for team in obs['teams']:
        if team['Task'] and team['PT']:
            for PTID in team['PT']:
                dict_actionToUnit[PTID[0]] = eval(team['Task'])



def refresh(window, blue_obs_deduce,units_state,deduce_obs_time):  # 根据预测情况进行动态显示 red_obs_deduce暂时用原有的
    global dict_actionToUnit
    global num_c
    global red_obs

    window.text.delete('1.0','end')
    now_time = datetime.datetime.now()

    obs_time=str(datetime.timedelta(seconds=int(deduce_obs_time)))

    window.text.insert('insert',obs_time)
    blue_obs_deduce,units_state = deduce.caculate_state( blue_obs_deduce, deduce_obs_time, dict_actionToUnit, units_state)#新起飞飞机的状态
    blue_obs_deduce,units_state,deduce_obs_time = deduce.move_model(blue_obs_deduce, deduce_obs_time, units_state,t=6)#移动图像
    if num_c == 9:
        window.draw_grid(blue_obs_deduce)
        num_c = 0
        blue_obs_deduce = copy.deepcopy(red_obs)
    elif num_c == 4:
        num_c += 1
        window.draw_grid(blue_obs_deduce)
    else:
        num_c += 1
    window.draw_grid(blue_obs_deduce)
    # window.draw_grid(blue_obs_deduce)
    # blue_obs_deduce, blue_units_images, cv, units_state, deduce_obs_time, red_units_images = deduce.move_model(
    #     blue_obs_deduce, deduce_obs_time, units_state, blue_units_images, cv, red_units_images)  # 移动图像

    # cv.move(red_units_images[0][2],10,10)
    # cv.move(red_units_images[2][2], 10, 10)
    # cv.move(red_units_images[3][2], 10, 10)

    window.root.after(100000, refresh, window, blue_obs_deduce,units_state,deduce_obs_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--env_id', type=int, required=False, default=1, help='id of environment')
    parser.add_argument('--speed', type=int, required=False, default=4, help='simulation speed')
    parser.add_argument('--num_episode', type=int, required=False, default=2, help='num episodes per env')

    args = vars(parser.parse_args())

    env_id = args['env_id']
    speed = args['speed']
    num_episodes = args['num_episode']

    # main(env_id, num_episodes, speed)
    thread_predict = threading.Thread(target=main, args=(env_id, num_episodes, speed))
    thread_word = threading.Thread(target=show_deduce_new)

    thread_predict.start()
    thread_word.start()

# python3 '/home/cect/code/battle-framework/run.py'
# apt-get install --reinstall libpython3.6-stdlib
