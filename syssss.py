from tkinter import *

def show_deduction():
    # 创建窗口
    root = Tk()
    root.geometry("700x700+100+50")
    cv = Canvas(root, background='white', width=700, height=700)
    cv.pack()
    bm = PhotoImage(file="images/机场_蓝方.png")
    backim = PhotoImage(file="images/背景.png")
    ##例如，有个坐标为(146700, -3000）的岛屿
    point = [146700, -3000]
    point_command_blue_1 = [-129532, 87667]
    point_command_blue_2 = [-131154, -87888]
    convertPoint3 = coordConvert(point[0], point[1])
    convertPoint1 = coordConvert(point_command_blue_1[0], point_command_blue_1[1])
    convertPoint2 = coordConvert(point_command_blue_2[0], point_command_blue_2[1])
    cv.create_image(375, 400, image=backim)
    cv.create_image(convertPoint3[0], convertPoint3[1], image=bm)
    cv.create_image(convertPoint1[0], convertPoint1[1], image=bm)
    cv.create_image(convertPoint2[0], convertPoint2[1], image=bm)

    root.mainloop()


def coordConvert(x,y,width=700,height=700,scale=500):
    convertXY = []
    convertX = x/scale + width/2
    convertY = height/2 - y/scale
    convertXY.append(convertX)
    convertXY.append(convertY)
    return convertXY
