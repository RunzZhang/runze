# Introduction########
# 1.pycharm 的一些技巧
# comment：
# python comment 行以 "#" 开始
# 但是你可以用鼠标多选多行，然后ctrl+/ 键一次commeent多行

# ctrl + F 查找，这个一般程序都有的，但是查找可以锁定大小写
# ctrl + G 跳段落。当报错告诉你某一行出错的时候，用这个快捷键可以快速跳到某一行
# insert 键。这个可能会被误触。知道再按insert键就可以恢复了

"""另外一种办法是英文的双引号，只需要在段落前后加上即可"""
#2 结构
# 一般是：
# import 部分
#       导入包
# function 部分
#       自定义函数
# class 部分
#       自定义 类
# main 部分
#       主函数
# 这个和c和java应该是类似的，但是c会把函数和类与主函数分开到不同的代码里

""""更多的科学画图的教程：
https://towardsdatascience.com/an-introduction-to-making-scientific-publication-plots-with-python-ea19dfa7f51e
matplot: https://towardsdatascience.com/an-introduction-to-making-scientific-publication-plots-with-python-ea19dfa7f51e
pandas: https://pandas.pydata.org/
有些英文过长也可以去b站找教程，但是元数据都在上面这里。此外这个教程并没有教授一维频率直方图和饼状图，考虑到其潜在使用频率较少的情况。如有
需要，也可以上述matplot的链接查找"""




# 那么现在开始
# 1.import部分
import matplotlib.pyplot as plt # 导入matplotlib中的pyplot包，并且将它在此代码中重命名为plt
import matplotlib as mpl # 导入matplotlib，并且将它在此代码中重命名为mpl
# 主要的python绘画包
from matplotlib import colors, cm   # 从matplottlib中导入颜色包
import matplotlib.font_manager as fm
# 从 matplot 中导入字体

import numpy as np
# 导入numpy，主要的处理数据（加减乘除，log，exp函数，还有array（类似于数列，但是可操作性更强））
import pandas as pd
# 导入pandas，主要用于导入数据（csv，excel等），和数据表的批量处理（选出符合标准的行，列，各行列加减的运算）
import os
# 导入系统操作（读入系统路径）


# 2.暂时没有需要定义的全局函数，跳过函数定义部分

# 定义类
class custom_plot():
    def __init__(self): # 类的初始化
        # def 是因为这是这个类的函数，只能作用于custom_plot类上，在其他类或者主函数中是不能被调用的
        # init 表示这个函数里的内容会在类被调用的时候就运行（所以叫初始化），类似于开机就会跑windows系统（初始化）
        # 但是其他软件需要手动点击（除初始化函数以外的函数）
        # self 表示这个函数作用在custom——plot 类本身上，类定义里的函数变量里第一个都是self（因为这些函数只能作用在本类上）
        # ，一开始迷惑不用不用太过纠结
        self.currentdir= os.getcwd()  # 得到当前文件夹路径
        self.base = "D:\\path\\to\\your\\file"
        self.base = "C:\\Users\\ZRZ\\Desktop\\python_scientific_plot"
        # 类内的变量定义，一开始学习可以粗暴得认为类里得函数都是self+变量名
        # 这里是数据得基础路径
        # 也可以把当前路径当作基础路径,我这里这么做了
        self.address = 'test.xlsx'
        # 数据得名称
        self.fulladdress = os.path.join(self.base, self.address)
        self.waddresss = self.base
        # 设置写入路径，它和基础路径一致，当然你也可以自定义
        # 数据全路径等于基础路径加数据的文件名
        # 回忆os是跟系统路经有关得包

    def read_Information(self):
        # self.df = pd.read_csv(self.fulladdress)
        self.df = pd.read_excel(self.fulladdress)
        # 根据你的文件类型，选择读取csv或者excel文件，读取路径是fulladress，并将这个文件保存在df里
        # 这里我们用了pandas得包，之后df（dataframe）就可以直接批量操作了

    def pandas_practice(self):
        # 这里介绍一下pandas的一些操作，可跳过，如果后续不理解可以回溯
        # 这里可以当作预处理一个df（data frame）
        # 先设置一个空的dictionary
        self.blank_dic={}

        """ uncomment above to see what is index"""
        for idx in range(len(self.df.index)):  # for loop
            # range取的for loop的循环上下限
            # len取得一个列表的长度
            # self.df.index 是你的excel表左侧第0行形成的数列，可以看上面绿色的comment
            # idx 指的就是行数

            if idx % 2 == 0:  # idx（行）是偶数
                self.blank_dic[idx]=self.df[idx]["column_name"]
                """那么在blank dic里添加一个项目，它的key是idx的数字，他的值是第idx行，名称为《column_name》的列的交叉项"""

        """pandas的一些教程
        总体上来说，pandas实现的包含了excel的选取和函数功能
        一切都是以self.df 为基础的
        其结构：
        如果excel表结构是
                  | A     |B      |
        0         |column1|column2|...
        1         | value1| value2|
        
        那么 df的结构是
        
        idx         |column1|column2|...
        0           | value1| value2|
        ... 
        选中行列 self.df[行数][列的名字]
        比如 self.df[0][column1]就是value1
        
        当然也可以选择多行，多列，并新建一个新的df
        self.df1 = self.df[r1:r2] 选中以r1开始（包含r1）到r2（不包含r2）的所有行
        
        self.df1 = self.df[column_number] 选中名字为colunm_name的列
        
        比如 self.df1 = self.df[column2] 那么 print(self.df1) 就是这样：
        
        idx         |column2|
        0           | value2|
        ...
         第三种常用的是条件选择
         self.df2 = self.df[self.df[column1]=='somevalue']['column3']
                            《选中列1里值为somevalue的行》     《在这些行里选择列名为column3的那一列》
         idx          |Sex    |  ID  |city|
         0            | Male  | 101  |shanghai    
         1            | Female| 3736 |beijing
         2            | Female| 377  | hangzhou  
         3            | Male  | 937  | hefei
         self.df2 = self.df[self.df[Sex]=='Female']['city']
         那么print(self.df2)就是
         idx          |city|   
         1            | beijing
         2            | hangzhou  
         当然不等式条件也是可以的
         self.df2 = self.df[self.df[ID]>'400']['city']
         idx          |city|   
         1            |beijing  
         3            | hefei
         
         4.当然平均值mean，方差std都是有的
         print(self.df[columnname].mean())
         print(self.df[columnname].std()) 
         输出这一列的均值、标准差
         如果print(self.df.mean())则会输出所有列的可用均值"""

        wdf = pd.DataFrame.from_dict(self.blank_dic, orient = 'index', columns=["column_name"])
        # 把上面的self.blank_dic从dict转化为data frame的格式，orient 指的把key设为idx列，把key的value设为column__name的值
        wdf.to_csv(self.waddresss+"output.csv", sep=',')
        # 把上面的df文档写为output。csv文档，分隔符设为逗号
        """这两部如果不懂可以跳过，除非你需要用到重新写数据"""
    def pandas_select(self):
        # 从excel表格里选取特定的数据为后续处理
        # 以下假设你的表格是m*n 的矩阵，有的有缺省项（NA） ,m 行， n 列
        # 这一步的目的是选出作为后续数据处理的横坐标和纵坐标
        self.value1 = ""
        self.condition1 = ''
        self.column11 = ''
        self.column12 = ''

        self.x1=self.df[self.df[self.condition1]==self.value1][self.column11].to_list()
        self.y1=self.df[self.df[self.condition1]==self.value1][self.column12].to_list()

        """不要觉得这很复杂，只是带入很多。这里说的是选取在condition1名称列下其值等于value1的所有数据行
        比如，选取性别（condition1）列为男性(value1)的所有行
        然后再取这些子表格里的两列（column11, column12）为x和y
        比如月份(column11)为x，收入(column12)为y
        总体就是选取性别为男性的收入随月份变化
        这里需要你自己填写上述变量的值
        to_list()函数是把dataframe 的种类变成list [1,2,4]这样的数列"""

        self.value2 = ""
        self.condition2 = ''
        self.column21 = ''
        self.column22 = ''

        self.x2 = self.df[self.df[self.condition2] == self.value2][self.column21].to_list()
        self.y2 = self.df[self.df[self.condition2] == self.value2][self.column22].to_list()

        """一样，选出另一组数据。这里如果需要在同一幅图里画多组数据，那么需要多组数据"""

    def plot_line_example(self):
        # 给出了x1,y1,x2,y2 在plot_line(没有example后缀) 函数里，你需要利用panda_select得到输入表里的两组数据
        # 折线图,输入是两个list，长度需要相等

        fig, axs = plt.subplots(1,1,figsize = (3,3))   # 建立画的底板，一共有1行，一列，也就是1*1幅画，x轴y轴长宽比3:3
        #当然这里也可以一次性画多张图，不过那个稍微复杂一些，现阶段跳过
        self.label1= "Correct"
        self.label2 ="Session"
        self.title= "Sample of Plot Line"   # 图的标题
        self.xlabel=r"$\mathregular{\lambda}$ (nm)"  # x轴的名字
        # r重申后面是字符串(string), \mathregular使用latex，
        # $\mathregular{'Command goes here'}$ 来使用latex
        self.ylabel='y value'       # y轴的名字
        self.xlow=0          # x轴下限
        self.xhigh=10       # x轴上限
        self.ylow = 0        # y轴下限
        self.yhigh = 10     # y轴上限
        axs.plot(self.x1,self.y1,color="red",label=self.label1)
        axs.plot(self.x2, self.y2, color='green',label= self.label2)
        # 画出不同颜色的折线，颜色分别为红和绿（可以选择其他的），曲线分别标记label1 和2

        axs.legend()  # 显示
        axs.set_title(self.title)
        axs.set_xlabel(self.xlabel, labelpad=10)  # labelpad： 调整x轴名称和x轴的距离
        axs.set_ylabel(self.ylabel, labelpad=10)
        # axs.set_xlim(self.xlow,self.xhigh)
        # axs.set_ylim(self.ylow,self.yhigh)
        # 如果不想设置一个，直接comment掉那一行


        """此处以下部分为额外要求，有需求可以从中查找，不需要全部设置"""
        """###################   ||  ####################"""
        """####################\ || /#####################"""
        """####################  __  ###################"""

        font_names = [f.name for f in fm.fontManager.ttflist]  # 列出全部的可选字体
        print('font list：', font_names)  # 输出上述的list

        mpl.rcParams['font.family'] = 'DejaVu Sans Mono'  # 选出字体
        plt.rcParams['font.size'] = 18  # 选出字号
        plt.rcParams['axes.linewidth'] = 2  # 选出坐标轴线宽

        axs.spines['right'].set_visible(True)
        axs.spines['top'].set_visible(True)
        # 选择要不要把图画上和右侧的框去掉，False指去掉

        axs.xaxis.set_tick_params(which='major', size=10, width=2, direction='in', top='on')
        #设置x轴主要坐标点的大小宽度方向，以及是否在画面上方x轴出现
        axs.xaxis.set_tick_params(which='minor', size=5, width=2, direction='in', top='on')
        # 设置x轴“次”要坐标点的大小宽度方向，以及是否在画面上方x轴出现
        axs.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
        # 设置y轴主要坐标点的大小宽度方向，以及是否在画面上方x轴出现
        axs.yaxis.set_tick_params(which='minor', size=5, width=2, direction='in', right='on')
        # 设置y轴次要坐标点的大小宽度方向，以及是否在画面上方x轴出现

        # axs.xaxis.set_major_locator(mpl.ticker.MultipleLocator(50))
        # #把x轴主要坐标点的间距设为100
        # axs.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(25))
        # # 把x轴次要坐标点的间距设为25
        # axs.yaxis.set_major_locator(mpl.ticker.MultipleLocator(50))
        # # 把y轴主要坐标点的间距设为100
        # axs.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(20))
        # # 把y轴主要坐标点的间距设为20


        # 更全面的设置在这个代码一开始的绿色comment里的链接里寻找
        # 把文章中的ax换成axs就好了
        """###################  --  ##################"""
        """###################/ || \######################"""
        """###################  ||  #####################"""
        """此处以上部分为可选"""
        plt.show() #显示图
        #显示之后可以直接点击保存来保存

    def plot_line(self):
        #折线图,输入是两个list，长度需要相等，需要先用pandas_select保存x1,x2,y1,y2

        fig, axs = plt.subplots(1,1,figsize = (3,3),sharex= True)   #建立画的底板，一共有1行，一列，也就是1*1幅画，x轴y轴长宽比3:3,两个折线图共享x轴
        self.label1= ""

        self.label2 =" "
        self.title="" #图的标题
        self.xlabel=r"$\mathregular{\lambda}$ (nm)"       #x轴的名字
        # r重申后面是字符串(string), \mathregular使用latex，
        # $\mathregular{'Command goes here'}$ 来使用latex
        self.ylabel=''       #y轴的名字
        self.xlow=0          #x轴下限
        self.xhigh=100       #x轴上限
        self.ylow = 0        #y轴下限
        self.yhigh = 100     #y轴上限
        axs.plot(self.x1,self.y1,color="red",label=self.label1)
        axs.plot(self.x2, self.y2, color='green',label= self.label2)
        #画出不同颜色的折线，颜色分别为红和绿（可以选择其他的），曲线分别标记label1 和2

        axs.legend()# 显示
        axs.set_title(self.title)
        axs.set_xlabel(self.xlabel, labelpad=10) #labelpad： 调整x轴名称和x轴的距离
        axs.set_ylabel(self.ylabel, labelpad=10)
        axs.set_xlim(self.xlow,self.xhigh)
        axs.set_ylim(self.ylow,self.yhigh)
        #如果不想设置一个，直接comment掉那一行


        """此处以下部分为额外要求，有需求可以从中查找，不需要全部设置"""
        """###################   ||  ####################"""
        """####################\ || /#####################"""
        """####################  __  ###################"""

        font_names = [f.name for f in fm.fontManager.ttflist]#列出全部的可选字体
        print('font list：',font_names) #输出上述的list

        mpl.rcParams['font.family'] = 'Avenir' #选出字体
        plt.rcParams['font.size'] = 18 #选出字号
        plt.rcParams['axes.linewidth'] = 2 #选出坐标轴线宽


        axs.spines['right'].set_visible(True)
        axs.spines['top'].set_visible(True)
        # 选择要不要把图画上和右侧的框去掉，False指去掉

        axs.xaxis.set_tick_params(which='major', size=15, width=2, direction='in', top='on')
        #设置x轴主要坐标点的大小宽度方向，以及是否在画面上方x轴出现
        axs.xaxis.set_tick_params(which='minor', size=7, width=2, direction='in', top='on')
        # 设置x轴“次”要坐标点的大小宽度方向，以及是否在画面上方x轴出现
        axs.yaxis.set_tick_params(which='major', size=15, width=2, direction='in', right='on')
        # 设置y轴主要坐标点的大小宽度方向，以及是否在画面上方x轴出现
        axs.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')
        # 设置y轴次要坐标点的大小宽度方向，以及是否在画面上方x轴出现

        axs.xaxis.set_major_locator(mpl.ticker.MultipleLocator(50))
        #把x轴主要坐标点的间距设为100
        axs.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(25))
        # 把x轴次要坐标点的间距设为25
        axs.yaxis.set_major_locator(mpl.ticker.MultipleLocator(50))
        # 把y轴主要坐标点的间距设为100
        axs.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(20))
        # 把y轴主要坐标点的间距设为20

        # 更全面的设置在这个代码一开始的绿色comment里的链接里寻找
        # 把文章中的ax换成axs就好了
        """###################  --  ##################"""
        """###################/ || \######################"""
        """###################  ||  #####################"""
        """此处以上部分为可选"""
        plt.show() # 显示图
        # 显示之后可以直接点击保存来保存
    def bar_1d(self):
        # 柱状图，可以区分下bar（柱状图）和hist（直方图）的区别。他们很类似，但是也有区别
        # hist偏向统计，记录的是频次。但是bar不用，当记录的值是频次的时候他等于直方图，当不是的时候就不等于
        # 举个例子。柱状图的输入是[1月到12月]，[1月到12月的下雨天数]。直方图记录的是[1-365天][有没有下雨]，然后再把365天按照12月分下来
        # 但是如果柱状图表示的是1-12月平均气温，就没有直接等同的直方图了。
        # 总体来说，直方图更偏向统计意义

        # 预输入和line_plot类似，但是分享横坐标，所以只有一个x
        # self.x1, self.y1, self.y2
        distance = 0.2 # 两相邻需要比较的bar之间的距离
        x_position = np.arange(len(self.x1)) #需要给各bar安排位置，
        label1 = 'Correct'
        label2= ' Session'
        fig, axs = plt.subplots(1, 1, figsize=(3, 3))
        axs.bar(x_position - distance, self.y1, 0.4, label=label1)
        # 画出数组1的bar，x位置在标准位置向左偏distance，高度为self.y1,宽度为0.4,记录为label1
        axs.bar(x_position + distance, self.y2, 0.4, label=label2)
        # 画出数组2的bar，x位置在标准位置向右偏distance，高度为self.y2,宽度为0.4,记录为label2
        axs.legend()
        # 有label就需要legend显示label
        axs.set_xticks(x_position)
        axs.set_xticklabels(self.x1)
        # 其他选项和line类似
        plt.show()


    def color_hist_2d(self):
        # 2d 平面颜色渲染的直方图
        # 数据需要预处理
        # 假设一组数据，出现的坐标分别为(v0,w0),(v1,w1)....那么需要x1,y1满足
        # self.x1=[v0,v1,v2...]
        # self.y1=[w0,w1,w2...]

        # 画出这组数据的折方图
        bins= 40   # 因为是直方统计，所以需要bin数
        fig, axs = plt.subplots(1, 1, figsize=(3, 3))  # 建立画的底板，一共有1行，一列，也就是1*1幅画，x轴y轴长宽比3:3
        (h, xedge, yedge, image)=axs.hist2d(self.x1, self.y1, bins=bins, norm=colors.Normalize(), cmap='plasma')
        # 等式的含义这里是指先运算（绘画）等式右边的内容，再把计算得到的其他参数赋值到左边
        # 左边的比较复杂，可以查询资料，这里不多阐述
        # bin是每边的统计格数，如果20就是20个格子。
        # norm是说值要不要归一化，一般选择是
        # plasma是颜色的渐变条件，plasma是从蓝到红
        fig.colorbar(image, ax=axs)
        # fig 和image 是上一步得到的输出，这里我们在这幅图旁画上归一化的颜色参考比例尺

        #####################################################
        ####### 其他参数设置和line_plot一致，都是对axs设置 ##########
        #####################################################

        plt.show()

    def color_2d(self):
        # 数据依旧需要预处理
        # 需要一个2d的矩阵
        # [[v00,v01,v02,v03,...],
        #  [v10,v11,...........],
        #  [v20,v21,...........],
        #  .......................]
        # color_2d 和color_hist_2d的区别是，hist输入的是每次数据的坐标，而前者是该坐标下的函数值(但是不含坐标，坐标有额外的输入)
        # 举个例子，如果把一把沙撒到地上，那么每粒沙落到地面的坐标组成的一组坐标列，就是hist
        # 而如果把地面各地点沙子高度的值记录下来，就是非hist
        # 可以把color_2d理解为2d的bar（柱状图），而hist是频数直方图
        self.array = [[5,2],[7,3]]
        self.xlow= 0
        self.xhigh = 10
        self.ylow = 0
        self.yhigh = 10
        # xy轴（坐标系）的范围
        fig, axs = plt.subplots(1, 1, figsize=(3, 3))
        image = axs.imshow(self.array, extent=(self.xlow,self.xhigh,self.ylow,self.yhigh), cmap='plasma')
        # 类似得，在(self.xlow,self.xhigh,self.ylow,self.yhigh)的范围里画出图像
        fig.colorbar(image, ax=axs)
        plt.show()

    def pandas_select_sample(self):
        # 这是一个案例，真实如何选择需要去pandas_select里编辑
        # 用不等式替代了等式条件
        self.x1=self.df[self.df['Correct']>=6]['Name'].to_list()
        self.y1=self.df[self.df['Correct']>=6]["Correct"].to_list()

        self.x2 = self.df[self.df['Correct']>=6]['Name'].to_list()
        self.y2 = self.df[self.df['Correct']>=6]["Session"].to_list()



# 这里是主函数，在这里调用我们编写的类和函数
if __name__=="__main__":
    """ 这部分是一个案例，如果不能运行，应该是环境或者IDE设置的问题。"""
    practice =custom_plot()  # 调用类，放到一个新的变量里，这里类的__init__函数会自动运行
    practice.read_Information()  # 读入示例的数据
    practice.pandas_select_sample()  # 使用pandas在读入的表里，选入某个条件下的x1,y1,x2,y2的值
    practice.plot_line_example()  # 利用数据画出折线图
    practice.bar_1d()  # 利用数据画出柱状图
    practice.x1=practice.y2  # color_hist_2d的预处理，为了画频率图，因为函数默认处理x1，y1，但是示例里x1是字符串，所以把y2赋值给x1，让x1，y1都是数
    # 这一步也可以看出，可以在主函数中给self.x1和self.y1直接赋值。如果这一步发生在类的函数里那就是self.x1=self.y2(因为self就是custom_plot类本身)
    practice.color_hist_2d()  # 利用数据画2d频率直方图
    practice.color_2d()  # 利用数据画出2d柱状图

    """在上面的可以运行后，想要运行你自己的数据，你需要执行以下几步
    1.调整class custom_plot里的self.base和self.address的值，使得最后的路径读取你需要的excel表格
    2.在read_information()里， 调整读取的是excel还是csv类型。comment 掉你不需要的部分
    3.在pandas_select函数里，选择你自己挑选的条件
    4.在plot_line/bar_1d/color_hist_2d/color_2d里，设置你需要的参数
    5.然后运行以下代码，别忘了comment掉这个段落前的案例"""
    # practice = custom_plot()
    # practice.read_Information()
    # practice.pandas_select()
    # practice.plot_line()
    # practice.bar_1d()
    # # practice.color_hist_2d()
    # # practice.color_2d()
    # 选择你需要的函数uncomment,如果有多个没有被comment, 那么会同时画出多个图片


