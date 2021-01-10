# 计算G/H值，G（从起点到方块的移动量）,H（从方块到中点的估算移动量):
import copy

# 开放列表（也就是有待探查的地点）
open_list = {}
# 关闭列表  (已经探查过的地点和不可行走的地点)
close_list = {}
end = None
cellValue_list_1 = []
risk_grid = []#//123

class Node(object):
    def __init__(self, father, x, y):
        self.map_border = (35, 35)  # 地图边界(二维数组的大小，用于判断一个节点的相邻节点是否超出范围)
        # assert x > 0 and x < self.map_border[0] and y > 0 and y < self.map_border[1]
        if x < 0 or x >= self.map_border[0] or y < 0 or y >= self.map_border[1]:
            raise Exception('坐标错误')

        self.father = father
        self.x = x
        self.y = y
        self.endpoint = (8, 4)  # 4,26
        self.endpoint2 = (26, 4)
        if father != None:  # 计算G、H值
            self.G = self.calculate_G()
            self.H = distance(self, self.endpoint2)
            self.F = self.G + self.H

        else:  # 如果为起点则均为0
            self.G = 0
            self.H = 0
            self.F = 0

    def calculate_G(self):
        global cellValue_list_1, risk_grid
        dis = 0
        if (abs(self.father.x - self.x) + abs(self.father.y - self.y)) == 2:
            dis = 1.41
        else:
            dis = 1

        risk_grid = [[row[i] for row in cellValue_list_1[1]] for i in range(len(cellValue_list_1[1][0]))]
        explore_grid = [[row[i] for row in cellValue_list_1[0]] for i in range(len(cellValue_list_1[0][0]))]
        # risk_factor = cellValue_list_1[1][self.y][self.x]  # 蓝方攻击能力
        # explore_factor = cellValue_list_1[0][self.y][self.x]
        risk_grid = max_min(risk_grid)
        explore_grid = max_min(explore_grid)
        risk_factor = risk_grid[self.x][self.y]  # 蓝方攻击能力
        explore_factor = explore_grid[self.x][self.y]

        g = dis + risk_factor * 100 + explore_factor * 200 + self.father.G

        return g

    def reset_father(self, father, new_G):
        if father != None:
            self.G = new_G
            self.F = self.G + self.H
        self.father = father
    # 计算距离


def distance(cur, endpoint):
    return abs(cur.x - endpoint[0]) + abs(cur.y - endpoint[1])


def max_min(list):
    max_value = max(max(row) for row in list)
    min_value = min(min(row) for row in list)
    if max_value != 0:
        for i in range(len(list)):
            for j in range(len(list[i])):
                list[i][j] = (list[i][j] - min_value) / (max_value - min_value)
    return list


# 在open_list中找到最小F值的节点
def min_F_node(start):
    global open_list, close_list
    if len(open_list) == 0:
        # print(start.x, start.y)
        raise Exception('路径不存在')
    _min = 9999999999999999
    _k = (start.x, start.y)
    # 以列表的形式遍历open_list字典
    for k, v in open_list.items():
        if _min > v.F:
            _min = v.F
            _k = k

    return open_list[_k]


# 把相邻的节点加入到open_list之中，如果发现终点说明找到终点
def addAdjacentIntoOpen(node):
    global open_list, close_list, end

    # 首先将该节点从开放列表移动到关闭列表之中
    open_list.pop((node.x, node.y))
    close_list[(node.x, node.y)] = node
    adjacent = []

    # 添加相邻节点的时候要注意边界
    # 上
    try:
        if node.x > 0 and node.x < 35 and (node.y - 1) > 0 and (node.y - 1) < 35:
            adjacent.append(Node(node, node.x, node.y - 1))
    except Exception as err:
        print(err)
        pass
    # 左上
    try:
        if (node.x - 1) > 0 and (node.x - 1) < 35 and (node.y - 1) > 0 and (node.y - 1) < 35:
            adjacent.append(Node(node, node.x - 1, node.y - 1))
    except Exception as err:
        print(err)
        pass
    # 右上
    try:
        if (node.x + 1) > 0 and (node.x + 1) < 35 and (node.y - 1) > 0 and (node.y - 1) < 35:
            adjacent.append(Node(node, node.x + 1, node.y - 1))
    except Exception as err:
        print(err)
        pass
    # 下
    try:
        if node.x > 0 and node.x < 35 and (node.y + 1) > 0 and (node.y + 1) < 35:
            adjacent.append(Node(node, node.x, node.y + 1))
    except Exception as err:
        print(err)
        pass
    # 左下
    try:
        if (node.x - 1) > 0 and (node.x - 1) < 35 and (node.y + 1) > 0 and (node.y + 1) < 35:
            adjacent.append(Node(node, node.x - 1, node.y + 1))
    except Exception as err:
        print(err)
        pass
    # 右下
    try:
        if (node.x + 1) > 0 and (node.x + 1) < 35 and (node.y + 1) > 0 and (node.y + 1) < 35:
            adjacent.append(Node(node, node.x + 1, node.y + 1))
    except Exception as err:
        print(err)
        pass
    # 左
    try:
        if (node.x - 1) > 0 and (node.x - 1) < 35 and node.y > 0 and node.y < 35:
            adjacent.append(Node(node, node.x - 1, node.y))
    except Exception as err:
        print(err)
        pass
    # 右
    try:
        if (node.x + 1) > 0 and (node.x + 1) < 35 and node.y > 0 and node.y < 35:
            adjacent.append(Node(node, node.x + 1, node.y))
    except Exception as err:
        print(err)
        pass

    # 检查每一个相邻的点
    for a in adjacent:
        # 如果是终点，结束
        if (a.x, a.y) == (end.x, end.y):
            new_G = node.G + 1  # G值
            end.reset_father(node, new_G)
            return True
        # 如果在close_list中,不去理他
        if (a.x, a.y) in close_list:
            continue
        # 如果不在open_list中，则添加进去
        if (a.x, a.y) not in open_list:
            open_list[(a.x, a.y)] = a
        # 如果存在在open_list中，通过G值判断这个点是否更近
        else:
            exist_node = open_list[(a.x, a.y)]
            new_G = calculate_G_2(node, exist_node)  # node.G + 1
            if new_G < exist_node.G:
                exist_node.reset_father(node, new_G)

    return False


def calculate_G_2(node, new_node):
    global cellValue_list_1, risk_grid
    dis = 0
    if (abs(node.x - new_node.x) + abs(node.y - new_node.y)) == 2:
        dis = 1.41
    else:
        dis = 1
    risk_grid = [[row[i] for row in cellValue_list_1[1]] for i in range(len(cellValue_list_1[1][0]))]
    explore_grid = [[row[i] for row in cellValue_list_1[0]] for i in range(len(cellValue_list_1[0][0]))]
    risk_grid = max_min(risk_grid)
    explore_grid = max_min(explore_grid)
    risk_factor = risk_grid[new_node.x][new_node.y]  # 蓝方攻击能力
    explore_factor = explore_grid[new_node.x][new_node.y]

    g = dis + risk_factor * 20000 + explore_factor * 1000 + node.G
    return g


# 查找路线
def find_the_path(start):
    global open_list, end
    open_list[(start.x, start.y)] = start

    the_node = start
    try:
        while not addAdjacentIntoOpen(the_node):
            the_node = min_F_node(start)

    except Exception as err:
        # 路径找不到
        print(err)
        return False
    return True


# 返回最短路径上的网格点
def closest_path(start):
    global end, risk_grid
    c_path = []
    node = end
    while node.father != None:
        # while (node.x != start.x and node.y !=start.y):
        point = (node.x, node.y)
        c_path.append(point)
        node = node.father
    point2 = (start.x, start.y)
    c_path.append(point2)
    return c_path


def cal_mul_path(cellValue_list_new, bombers_dic, num_weapon):#计算所需导弹数的所有最优路径
    Path_dict = {}
    bestPath_list = []
    k_list = []
    sum = 0
    for k, v in bombers_dic.items():
        point = v['pos']
        num = v['num']
        start = Node(None, point[0], point[1])
        # print(start.x,start.y,'*****************************************')
        path_list, G = cal_path(cellValue_list_new, start)
        print(path_list)
        Path_dict[G] = {'path': path_list, 'num': num}
        k_list.append(G)
    k_list.sort()
    for i in range(len(k_list)):
        if sum <= num_weapon:
            sum += Path_dict[k_list[i]]['num']
            bestPath_list.append(Path_dict[k_list[i]]['path'])
        else:
            break
    return  bestPath_list


def cal_path(cellValue_list_new, start):  # 计算、返回某条最优路径所有点
    global cellValue_list_1, end, open_list, close_list

    cellValue_list_1 = copy.deepcopy(cellValue_list_new)

    open_list = {}
    close_list = {}
    path_list = []
    #   start = Node(None, 17, 32)
    end = Node(None, 26, 4)
    if find_the_path(start):
        path_list = closest_path(start)

    return path_list, end.G

#
# def main():
#     path_list =cal_path()
#
# if __name__ == '__main__':
#     main()
