'''人工智能程序设计大作业之贪吃蛇'''



import time
import pygame
import random
from pygame.locals import *
import numpy as np


# 设置基本黑白颜色参数
Black=(0,0,0)
White=(255,255,255)
Red=(255,0,0)
Purple=(127,0,255)
TransparentGreen=(204,255,204)
PaleBlue=(153,153,255)
DarkRed=(51,0,102)
SkyBlue=(0,128,255)
# 设置基本窗口大小参数（这里默认窗口就用方形吧）
size_of_large_rec=512
row_column_num=64#横竖各row_column_num个方块
square_size=size_of_large_rec/row_column_num#小方格大小
max_len=(row_column_num*1/6)**2#设置最大长度如果达到则游戏胜利
#确定每一个方格左上角的位置
location_of_the_square=np.zeros(shape=(row_column_num,row_column_num),dtype=list)
for i in range(row_column_num):
    for j in range(row_column_num): #\表示换行接着写
        loc_x=size_of_large_rec/row_column_num*j
        loc_y=size_of_large_rec/row_column_num*i
        location_of_the_square[i][j]=[loc_x,loc_y]

class Snake():
    len_of_snake=5#每条蛇初始化长度均为5
    foodlocation=[0,0]#需要记录终点是否会发生变动从而返回是否要改变已经规划好的路径提高效率
    def __init__(self,location_list,direction):
        self.location_list=location_list
        self.direction=direction
    #Snake自动移动
    def move(self):
        '''每调用一次move就移动一次'''
        head_list=self.location_list[0]
        if self.direction == 0:
            new_head=[0,0]
            new_head[0]=head_list[0]
            new_head[1]=head_list[1]-square_size
            self.location_list.insert(0,new_head)
            self.location_list.pop()
        elif self.direction == 1:
            new_head=[0,0]
            new_head[0]=head_list[0]
            new_head[1]=head_list[1]+square_size
            self.location_list.insert(0,new_head)
            self.location_list.pop()
        elif self.direction == 2:
            new_head = [0, 0]
            new_head[0] = head_list[0] - square_size
            new_head[1] = head_list[1]
            self.location_list.insert(0, new_head)
            self.location_list.pop()
        else:
            new_head = [0, 0]
            new_head[0] = head_list[0] + square_size
            new_head[1] = head_list[1]
            self.location_list.insert(0, new_head)
            self.location_list.pop()
    # hunting_snake的改变方式
    def hunting_snake_change_move(self):
        num=random.uniform(0,1)#有0.05的概率会改变自己移动的方向
        head_list=self.location_list[0]
        ori_direction=self.direction
        #如果已经在边缘了就要马上回来了防止出界
        epsilon=3
        if head_list[0]<epsilon*square_size or head_list[0]>size_of_large_rec-epsilon*square_size\
                or head_list[1]<epsilon*square_size or head_list[1]>size_of_large_rec-epsilon*square_size:
            if head_list[0] < epsilon * square_size :
                # 如果是在左侧边缘
                self.direction = 3
            elif head_list[0] > size_of_large_rec - epsilon * square_size:
                #如果是在右侧边缘
                self.direction = 2
            elif head_list[1]<epsilon*square_size:
                # 如果是在上侧边缘
                self.direction = 1
            else:#如果是在下侧边缘
                self.direction = 0
            return
        if num<=0.05:#如果小于某个值则改变方向  用while循环防止
            self.direction = random.randint(0, 4)
            while self.direction == ori_direction:
                self.direction = random.randint(0, 4)
    #如果吃到了食物则变长
    def eatfood(self,foodlocation):
        #如果碰到了食物
        # if self.location_list[0]==foodlocation[0] and self.location_list[1]==foodlocation[1]:
        if foodlocation in self.location_list:
            next_location=return_food_next_location(foodlocation=foodlocation,direction=self.direction)
            self.location_list.insert(0,next_location)
            #self.location_list.insert(0, foodlocation)
            print("吃到食物之后玩家位置为：",self.location_list)
            self.len_of_snake+=1
            newfoodlocation=generate_food()
            print("新食物的位置在：",newfoodlocation)
            return newfoodlocation
        else:
            return foodlocation
    #如果进入了虫洞
    def meet_wormhole(self,wormhole):
        head_list=self.location_list[0]
        decrease_wormhole=wormhole.copy()
        if head_list in decrease_wormhole:
            decrease_wormhole.remove(head_list)
            head_list=decrease_wormhole[0]
            self.location_list[0]=head_list
    #判断是否需要改变路径
    def if_change_road(self,foodlocation):
        if self.foodlocation!=foodlocation:
            self.foodlocation = foodlocation
            return True
        else:
            return False
    #规划路径并返回接下来要走的路径上每一个节点的下一个节点的方向组成的字典（从起点开始算）
    def plan_following_road(self,wormhole):#自己已经有了foodlocation了就不用再引入了
        '''注意返回的字典键一定要是元组类型！！！！'''
        '''###这里就要写A*算法了###'''
        #从贪吃蛇蛇头开始创建openlist与closelist
        headlist=self.location_list[0]
        openlist=[tuple(headlist)]#所有可能遍历点组成的集合
        closelist=[]#已经遍历过的点则不再考虑
        distance_head=manhadun_distance(headlist,self.foodlocation)
        distance_diction={tuple(headlist):distance_head}#定义每个点到食物的曼哈顿距离的字典
        dict_point={}#每个点指向的位置字典，键为子节点，值为父节点
        dict_node_direction={}#最后最优路径上每个点的接下来的方向
        while tuple(self.foodlocation) not in openlist:
            #获取上下左右的位置并加入openlist中
            near_location=[(0,0),(0,0),(0,0),(0,0)]
            min_distance=min(distance_diction.values())
            min_point=(0,0)#寻找到距离最短的点
            for i in openlist:
                if distance_diction[i]==min_distance:
                    min_point=i
                    break
            #up_square,down_square,left_square,right_square=return_udlr_location()
            near_location[0],near_location[1],near_location[2],near_location[3]\
                =return_udlr_location(original_location=min_point)#上下左右分别为0123
            #print("附近点位置为：",near_location)
            for i in near_location:
                if i not in closelist:
                    distance_i=square_size+manhadun_distance(i,self.foodlocation)#求出周围四个点里离食物的距离f=g+h
                    if i in openlist:#如果已经在openlist当中了则比较现在距离与原来距离的大小
                        if distance_i<distance_diction[tuple(i)]:#如果当前更好则更新
                            distance_diction[tuple(i)]=distance_i
                            dict_point[tuple(i)] = min_point
                        else:
                            continue
                    else:#否则加入到开放字典openlist当中去
                        openlist.append(tuple(i))#加入开放字典当中去
                        distance_diction[tuple(i)]=distance_i#并将点及其距离添加到距离字典当中去
                        dict_point[tuple(i)]=min_point#子节点指向父节点的指针字典
                    # if list(i) in wormhole:#考虑虫洞的情况
                    #     wormhole_copy=wormhole.copy()
                    #     wormhole_copy.remove(list(i))
                    #     anotherhole=wormhole_copy[0]
                    #     print("这个洞的位置为：",list(i))
                    #     print("另一个洞的位置为：",anotherhole)
                    #     distance_another_hole=square_size+manhadun_distance(anotherhole,self.foodlocation)
                    #     if distance_another_hole in openlist:  # 如果已经在openlist当中了则比较现在距离与原来距离的大小
                    #         if distance_another_hole < distance_diction[tuple(anotherhole)]:  # 如果当前更好则更新
                    #             distance_diction[tuple(anotherhole)] = distance_another_hole
                    #             dict_point[tuple(anotherhole)] = min_point
                    #     else:  # 否则加入到开放字典openlist当中去
                    #         openlist.append(tuple(anotherhole))  # 加入开放字典当中去
                    #         distance_diction[tuple(anotherhole)] = distance_another_hole  # 并将点及其距离添加到距离字典当中去
                    #         dict_point[tuple(anotherhole)] = min_point  # 子节点指向父节点的指针字典
            closelist.append(tuple(min_point))
            openlist.remove(tuple(min_point))
        food_last_node=tuple(dict_point[tuple(self.foodlocation)])
        dict_node_direction[food_last_node]=parent_next_direction(tuple(self.foodlocation),food_last_node)
        food_last_last_node=(0,0)
        while tuple(headlist) not in dict_node_direction.keys():
            food_last_last_node=tuple(dict_point[tuple(food_last_node)])
            dict_node_direction[food_last_last_node] = parent_next_direction(tuple(food_last_node), food_last_last_node)
            food_last_node=food_last_last_node
        print(dict_node_direction)
        return dict_node_direction




#画出基本图像的函数
def draw_basic_background(screen,main_snake,hunting_snake,foodlocation,wormhole):
    # 填充窗口颜色
    screen.fill(White)
    # 绘制贪吃蛇   此处location_list是一个包含着贪吃蛇身体位置的信息的列表
    for body_location in main_snake.location_list:
        list_of_argument = [body_location[0], body_location[1], square_size, square_size]
        pygame.draw.rect(screen, Black, list_of_argument)#画出贪吃蛇身体部分
    for body_location in hunting_snake.location_list:
        list_of_argument = [body_location[0], body_location[1], square_size, square_size]
        pygame.draw.rect(screen, Red, list_of_argument)#画出贪吃蛇身体部分
    list_of_food=[foodlocation[0],foodlocation[1],square_size,square_size]
    pygame.draw.rect(screen, Purple, list_of_food)  # 画出食物的位置
    for wormhole_location in wormhole:
        list_of_hole=[wormhole_location[0],wormhole_location[1],square_size,square_size]
        pygame.draw.rect(screen,SkyBlue,list_of_hole)#画出两个虫洞的位置
#确定蛇的身体位置
def Snake_Body_Location(direction=0):
    '''传入头的列表以及方向'''
    Body_Location=[]
    x = random.randint(4, row_column_num - 4)  # 在x轴方向上第几个
    y = random.randint(4, row_column_num - 4)
    loc_x_head = x * square_size
    loc_y_head = y * square_size
    Body_Location.append([loc_x_head,loc_y_head])
    #这里为了方便起见暂时先生成5*1的身体好了
    for i in range(4):
        direc_body=random.randint(0,4)
        while direc_body==direction:
            direc_body = random.randint(0, 4)
    if direction==0:
        for i in range(1,5):
            Body_Location.append([loc_x_head,loc_y_head+i*square_size])
    elif direction==1:
        for i in range(1,5):
            Body_Location.append([loc_x_head,loc_y_head-i*square_size])
    elif direction==2:
        for i in range(1,5):
            Body_Location.append([loc_x_head+i*square_size,loc_y_head])
    else:
        for i in range(1, 5):
            Body_Location.append([loc_x_head-i * square_size, loc_y_head])
    print("蛇的位置列表为：",Body_Location)
    return Body_Location
#随机生成一个食物位置
def generate_food():
    x=random.randint(0,row_column_num-1)
    y = random.randint(0, row_column_num - 1)
    loc_x=x*square_size
    loc_y=y*square_size
    return loc_x,loc_y
#游戏初始化
def init_game():
    '''注意身体位置列表里面头在前尾在后！！！！！！'''
    #先确定两条蛇的起始方向
    main_direction=random.randint(0,4)#初始化方向：规定0上 1下 2左 3右
    hunting_direction=random.randint(0,4)
    #然后确定贪吃蛇的身体在哪里
    main_loction=Snake_Body_Location(main_direction)
    hunting_location=Snake_Body_Location(hunting_direction)
    #随机生成一个食物
    foodlocation=list(generate_food())
    return main_direction,hunting_direction,main_loction,hunting_location,foodlocation
#判断是否死亡  是返回True  否返回False
def judge_death(main_snake,hunting_snake):
    head_list=main_snake.location_list[0]
    body_location=main_snake.location_list.copy()
    for i in range(4):
        body_location.pop(0)
    if head_list in body_location:#如果碰到自己的身体
        print("玩家撞到了自己")
        return True
    elif head_list in hunting_snake.location_list:#如果碰到捕食者
        print("玩家碰到了捕食者")
        return True
    elif head_list[0]< 0 or head_list[0]>=size_of_large_rec:#如果超出左右边界
        print("玩家超出左右边界")
        return True
    elif head_list[1]< 0 or head_list[1]>=size_of_large_rec:#如果超出上下边界
        print("玩家超出上下边界")
        return True
    else:
        return False
#开场游戏介绍
def describe_game(screen):
    font = pygame.font.SysFont('KaiTi', int(size_of_large_rec / 11))  # 设置字体类型
    text = font.render('游戏规则Rules:', True, TransparentGreen)
    location = [size_of_large_rec * 2 / 13, size_of_large_rec * 2 / 7]
    screen.blit(text, location)
    font = pygame.font.SysFont('KaiTi', int(size_of_large_rec / 30))  # 设置字体类型
    text = font.render('尽量避免碰到周围墙壁、捕猎者和自己的身体', True, White)
    location = [size_of_large_rec * 1 / 8  , size_of_large_rec * 3 / 8+20]
    screen.blit(text, location)
    text = font.render('使用w s a d（上下左右）键改变你的方向', True, White)
    location = [size_of_large_rec * 1 / 8, size_of_large_rec * 3 / 8 + 20+30]
    screen.blit(text, location)
    text = font.render(f'达到最大长度{max_len:.0f}个大小就赢得胜利啦~~', True, White)
    location = [size_of_large_rec * 1 / 8, size_of_large_rec * 3 / 8 + 20+2*30]
    screen.blit(text, location)
    text = font.render('紫色的方格是食物，蓝色的方格是虫洞', True, White)
    location = [size_of_large_rec * 1 / 8, size_of_large_rec * 3 / 8 + 20 + 3 * 30]
    screen.blit(text, location)
    text = font.render('按下j键1.5倍速，按下k键二倍速，需要长按', True, White)
    location = [size_of_large_rec * 1 / 8, size_of_large_rec * 3 / 8 + 20 + 4 * 30]
    screen.blit(text, location)
    text = font.render('温馨提醒：注意键盘要切换半角输入哦~~', True, White)
    location = [size_of_large_rec * 1 / 8, size_of_large_rec * 3 / 8 + 20 + 5 * 30]
    screen.blit(text, location)
    pygame.display.update()
    time.sleep(4)  # 暂停4秒
    screen.fill(Black)
    font = pygame.font.SysFont('KaiTi', int(size_of_large_rec/11))#设置字体类型
    text = font.render('贪吃蛇 启动！', True, TransparentGreen)
    location=[size_of_large_rec*2/9,size_of_large_rec*3/7]
    screen.blit(text, location)
    pygame.display.update()
    time.sleep(1)  # 暂停一会
#结尾显示胜利或者失败
def display_win_or_fail(text_show):
    font = pygame.font.SysFont('SimHei', int(size_of_large_rec / 15))  # 设置字体类型
    text = font.render(text_show, True, DarkRed)
    location = [size_of_large_rec * 1 / 5, size_of_large_rec * 3 / 7]
    screen.blit(text, location)
    pygame.display.update()
#随机生成虫洞（用字典表示）
def generate_wormhole():
    x = random.randint(0, row_column_num - 1)
    y = random.randint(0, row_column_num - 1)
    loc_x1 = x * square_size
    loc_y1 = y * square_size
    wormhole_location1=[loc_x1,loc_y1]
    x = random.randint(0, row_column_num - 1)
    y = random.randint(0, row_column_num - 1)
    loc_x2 = x * square_size
    loc_y2 = y * square_size
    wormhole_location2=[loc_x2,loc_y2]
    wormhole_location=[wormhole_location1,wormhole_location2]
    return wormhole_location
#返回上下左右的位置坐标
def return_udlr_location(original_location):
    up=tuple([original_location[0],original_location[1]-square_size])
    down=tuple([original_location[0],original_location[1]+square_size])
    left=tuple([original_location[0]-square_size,original_location[1]])
    right=tuple([original_location[0]+square_size,original_location[1]])
    return up,down,left,right
#获取某一点与另一点的曼哈顿距离
def manhadun_distance(point,foodlocation):
    return abs(point[0]-foodlocation[0])+abs(point[1]-foodlocation[1])
#返回父节点下一时刻的方向
def parent_next_direction(kid_loction,parent_loction):
    if kid_loction[0]==parent_loction[0] and kid_loction[1]<parent_loction[1]:
        return 0
    elif kid_loction[0]==parent_loction[0] and kid_loction[1]>parent_loction[1]:
        return 1
    elif kid_loction[0]<parent_loction[0] and kid_loction[1]==parent_loction[1]:
        return 2
    elif kid_loction[0] > parent_loction[0] and kid_loction[1] == parent_loction[1]:
        return 3
#返回吃到食物后的食物下一个位置
def return_food_next_location(foodlocation,direction):
    next_location=[0,0]
    if direction==0:
        next_location[0]=foodlocation[0]
        next_location[1]=foodlocation[1]-square_size
        return  next_location
    elif direction==1:
        next_location[0]=foodlocation[0]
        next_location[1]=foodlocation[1]+square_size
        return next_location
    elif direction==2:
        next_location[0]=foodlocation[0]-square_size
        next_location[1]=foodlocation[1]
        return next_location
    elif direction==3:
        next_location[0]=foodlocation[0]+square_size
        next_location[1]=foodlocation[1]
        return next_location

#规定0上 1下 2左 3右
# 初始化Pygame
pygame.init()
# 创建时钟对象
clock = pygame.time.Clock()
# 设置窗口大小
screen = pygame.display.set_mode((size_of_large_rec,size_of_large_rec))
# 设置窗口标题
pygame.display.set_caption("贪吃蛇游戏")
#游戏和角色初始化
(main_direction,hunting_direction,
 main_loction,hunting_location,foodlocation)=init_game()
wormhole=generate_wormhole()#虫洞初始化
main_snake=Snake(main_loction,main_direction)#主玩家初始化
print("主玩家位置为：",main_snake.location_list)
hunting_snake=Snake(hunting_location,hunting_direction)
# 游戏循环
describe_game(screen=screen)
dict_node_direction={}
done = False
if_death=False
len_main_snake=5#初始蛇的长度为5
while not done:
    #hunting_snake的改变方式
    '''hunting_snake.hunting_snake_change_move()'''#这里原本是靠概率来决定hunting_snake改变方向，现在通过A*算法来规划路径
    if_change_road=hunting_snake.if_change_road(foodlocation=foodlocation)
    if if_change_road:
        dict_node_direction=hunting_snake.plan_following_road(wormhole=wormhole)
        print(dict_node_direction)
    if tuple(hunting_snake.location_list[0]) not in dict_node_direction.keys():
        dict_node_direction = hunting_snake.plan_following_road(wormhole=wormhole)
    hunting_snake.direction=dict_node_direction[tuple(hunting_snake.location_list[0])]
    # 两条蛇开始移动   （这里之后可能会按下加速键这里需要更改的）
    main_snake.move()
    foodlocation = list(main_snake.eatfood(foodlocation=foodlocation))
    hunting_snake.move()
    foodlocation = list(main_snake.eatfood(foodlocation=foodlocation))
    #两条蛇是否吃到了食物
    foodlocation=list(main_snake.eatfood(foodlocation=foodlocation))
    foodlocation=list(hunting_snake.eatfood(foodlocation=foodlocation))
    #如果进入了虫洞
    main_snake.meet_wormhole(wormhole=wormhole)
    hunting_snake.meet_wormhole(wormhole=wormhole)
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print("鼠标点击")
        elif event.type == KEYDOWN:
            # main_snake的改变方式
            if event.key== pygame.K_w:
                #如果按下了w键且不是朝下走
                if main_snake.direction != 1:
                    main_snake.direction=0
            elif event.key == pygame.K_s:
                # 如果按下了s键且不是朝上走
                if main_snake.direction != 0:
                    main_snake.direction = 1
            elif event.key == pygame.K_a:
                # 如果按下了a键且不是朝右走
                if main_snake.direction != 3:
                    main_snake.direction = 2
            elif event.key == pygame.K_d:
                # 如果按下了d键且不是朝左走
                if main_snake.direction != 2:
                    main_snake.direction = 3
        keys=pygame.key.get_pressed()
        if keys[pygame.K_j]:
            # 如果按下了h键则加速
            main_snake.move()
        elif keys[pygame.K_k]:
            # 如果按下了h键则加速
            main_snake.move()
            foodlocation = list(main_snake.eatfood(foodlocation=foodlocation))
            main_snake.move()
            foodlocation = list(main_snake.eatfood(foodlocation=foodlocation))
    # 判断是否死亡
    if_death = judge_death(main_snake=main_snake, hunting_snake=hunting_snake)
    # 画出基本的背景图
    draw_basic_background(screen=screen, main_snake=main_snake,
                          hunting_snake=hunting_snake, foodlocation=foodlocation, wormhole=wormhole)
    #更新窗口
    pygame.display.update()
    if if_death:
        break
    if main_snake.len_of_snake>=max_len:
        break
    # 控制游戏帧率
    clock.tick(16)
#如果死亡显示死亡画面
if if_death:
    display_win_or_fail("您失败了 o(╥﹏╥)o ")
    time.sleep(2)#暂停2秒
#如果胜利则显示胜利的画面
if main_snake.len_of_snake>=max_len:
    display_win_or_fail("您成功啦 (≧∀≦)~")
    time.sleep(2)
#退出Pygame
pygame.quit()


