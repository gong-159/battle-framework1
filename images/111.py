import PIL.Image as Image
# 以第一个像素为准，相同色改为透明
def transparent_back(img):
    img = img.convert('RGBA')
    L, H = img.size
    color_0 = (255,255,255,255)#要替换的颜色
    for h in range(H):
        for l in range(L):
            dot = (l,h)
            color_1 = img.getpixel(dot)
            if color_1 == color_0:
                color_1 = color_1[:-1] + (0,)
                img.putpixel(dot,color_1)
    return img

if __name__ == '__main__':
    img=Image.open('机场_蓝方.png')
    img=transparent_back(img)
    img.save('机场_蓝方_new.png')
    print("success")
picConfig = {
    'red':{
         11: 'images/歼击机_红方.png',
         12: 'images/预警机_红方.png',
         13: 'images/干扰机_红方.png',
         14: 'images/无人侦察机_红方.png',
         15: 'images/轰炸机_红方.png',
         21: 'images/驱逐舰_红方.png',
         31: 'images/歼击机_红方.png', ##地面防空
         32: 'images/雷达_红方.png',
         41: 'images/歼击机_红方.png', ##指挥所
         42: 'images/机场_红方.png',
         18: 'images/民航.png', ##未知空中目标
         19: 'images/民航.png', ##民航
         28: 'images/货轮.png', ##未知水面目标
         29: 'images/货轮.png'  ##民船
    },
    'blue':{
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