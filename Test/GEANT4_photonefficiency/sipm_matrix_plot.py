#translate G4 output file into list

import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib

size=15
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : size}

matplotlib.rc('font', **font)

#read PmtInformation file and plot positions photon hits sipms
#raw count is the event number which hit sipm volume
# count is the event number which hits the SiPM_Silicon part
def read_Information(address):
    file = open(address,'r')
    sipm_matrix={}
    raw_counts=0
    count=0
    x=[]
    y=[]
    z=[]
    lines=file.readlines()
    for line in lines:
        line_list=line.split()
        try:
            print(int(line_list[0]))
            raw_counts = raw_counts+1
            if line_list[-1] in sipm_matrix.keys():
                sipm_matrix[line_list[-1]] = sipm_matrix[line_list[-1]]+1
            else:
                sipm_matrix[line_list[-1]] = 1

            if line_list[-1] in['SIPM1_Si_phys','SIPM2_Si_phys','SIPM3_Si_phys','SIPM4_Si_phys','SIPM5_Si_phys']:
                count=count+1
                if line_list[7]=='um':
                    x.append(float(line_list[6])/1000)
                elif line_list[7]=='mm':
                    x.append(float(line_list[6]))
                elif line_list[7]=='cm':
                    x.append(float(line_list[6])*10)
                else:
                    print('x unit',line_list[7])

                if line_list[9]=='um':
                    y.append(float(line_list[8])/1000)
                elif line_list[9] == 'mm':
                    y.append(float(line_list[8]))
                elif line_list[9]=='cm':
                    y.append(float(line_list[8])*10)
                else:
                    pass

                if line_list[11]=='um':
                    z.append(float(line_list[10])/1000)
                elif line_list[11]=='mm':
                    z.append(float(line_list[10]))
                elif line_list[11]=='cm':
                    z.append(float(line_list[10])*10)
                else:
                    pass
        except:
            pass
    print(sipm_matrix)
    print("raw_counts",raw_counts)
    print("count",count)

    # print(x,y,z)
    # plot_xyz(x[:500],y[:500],z[:500])
    return 0

#plot x, y, z scatter graph based on 3 coordinate list
def plot_xyz(x_list,y_list,z_list):
    fig=plt.figure()
    ax = fig.add_subplot(projection='3d')
    lenx=len(x_list)
    leny=len(y_list)
    lenz=len(z_list)
    print(lenx,leny,lenz)
    for i in range(lenx):
        ax.scatter(x_list[i],y_list[i],z_list[i],marker='.')
    ax.set_xlabel('X axis/mm')
    ax.set_ylabel('Y axis/mm')
    ax.set_zlabel('Z axis/mm')
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.show()
    return 0

# similar to plot_xyz, but 2d plot
def plot_xy(x_list,y_list):
    fig=plt.figure()
    ax = fig.add_subplot()
    lenx=len(x_list)
    leny=len(y_list)

    print(lenx,leny)
    for i in range(lenx):
        ax.scatter(x_list[i],y_list[i],marker='.')
    ax.set_xlabel('X axis/mm')
    ax.set_ylabel('Y axis/mm')
    # ax.set_xlabel('Energy /ev')
    # ax.set_ylabel('ABSL /cm')
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.show()
    return 0

#read macro output file, find the last step in one event and plot the last step's position based on the key word KEY1
# Search all physcis volumes specified by KEY2 where particle passes through, and count the times.

######################################################################################
#                 ##                     ##             #             #              #
#                 ##                     ##             #             #              #
#        1        ##           2         ##      3      #       4     #       5      #
#                 ##                     ##             #             #              #
#                 ##                     ##             #             #              #
######################################################################################
# particle ----------------------------------------------------------------------------------->
# KEY1 = 5, KEY2 = 1,2,3,4,5

def read_key_txt(address, KEY1='reflector_PTFE_phys Transportation',KEY2='reflector_PTFE_phys'):
    file=open(address)
    lines=file.readlines()
    line_len=len(lines)
    sipm_matrix={}
    x1=[]
    y1=[]
    z1=[]
    x2 = []
    y2 = []
    z2 = []


    count=0
    teflon_count=0
    teflon_abs_count=0
    for i in range(line_len):
        line_list=lines[i].split()
        # print(line_list)
        try:
            if line_list[0] =='LXe':
                count=count+1
                # print(line_list)
                last_step_track=lines[i-1].split()

                key=last_step_track[-2]+' '+last_step_track[-1]
                if key in sipm_matrix.keys():
                    sipm_matrix[key] = sipm_matrix[key] + 1
                else:
                    sipm_matrix[key] = 1

                if key==KEY1:
                    # print(float(last_step_track[2])<-100)
                    x1.append(float(last_step_track[1]))
                    y1.append(float(last_step_track[2]))
                    z1.append(float(last_step_track[3]))
                    teflon_abs_count=teflon_abs_count+1

        except:
            pass
        if KEY2 in line_list:
            teflon_count = teflon_count + 1
            x2.append(float(line_list[1]))
            y2.append(float(line_list[2]))
            z2.append(float(line_list[3]))



    print(sipm_matrix)
    # print(x1,'\n',y1,'\n',z1)
    print('raw teflon=',teflon_count, 'teflon_end',teflon_abs_count,'ratio',teflon_abs_count/teflon_count )
    # plot_xyz(x2[:1000],y2[:1000],z2[:1000])
    # plot_xyz(x2, y2, z2)
    # plot_xy(x2[:500], y2[:500])
    # plot_xy(x2,y2)
    return(0)

#read macro output file, locate the all last steps, count them and clasify them into different types and plot pie chart.
def sipm_pie(address):
    file=open(address)
    # file=open("runtest1.txt")
    lines=file.readlines()
    line_len=len(lines)
    sipm_matrix={}
    new_dic={'Inner_Jar':0,'Outer_Jar':0,'Other':0,'SiPM':0,'SiPM_Holder':0,"Pressure Vessel":0,"Teflon":0}
    new_label=[]
    new_count=[]
    other_list = []
    count=0
    for i in range(line_len):
        line_list=lines[i].split()
        # print(line_list)
        try:
            if line_list[0] =='LXe':
                count=count+1
                # print(line_list)
                last_step_track=lines[i-1].split()

                key=last_step_track[-2]+' '+last_step_track[-1]
                if key in sipm_matrix.keys():
                    sipm_matrix[key] = sipm_matrix[key] + 1
                else:
                    sipm_matrix[key] = 1



        except:
            pass
    print(sipm_matrix)
    for key in sipm_matrix:
        if "Holder" in key:
            new_dic["SiPM_Holder"]=new_dic["SiPM_Holder"]+sipm_matrix[key]
        elif "Si_phys" in key:
            new_dic["SiPM"] = new_dic["SiPM"] + sipm_matrix[key]
        elif "outer_jar" in key:
            new_dic["Outer_Jar"] = new_dic["Outer_Jar"] + sipm_matrix[key]
        elif "inner_jar" in key:
            new_dic["Inner_Jar"] = new_dic["Inner_Jar"] + sipm_matrix[key]
        elif "PTFE" in key:
            new_dic["Teflon"] = new_dic["Teflon"] + sipm_matrix[key]
        elif "pressure_vessel" in key:
            new_dic["Pressure Vessel"] = new_dic["Pressure Vessel"] + sipm_matrix[key]
        else:
            new_dic["Other"] = new_dic["Other"] + sipm_matrix[key]
            other_list.append(key)

    for key in new_dic:
        new_label.append(key)
        new_count.append(float(new_dic[key]))




    # plot_xyz(x,y,z)
    pie_chart(new_label,new_count)
    print(new_dic)
    print('otherlist',other_list)
    return(0)



def pie_chart(labels,sizes):
    # x=np.char.array(labels)
    # y=np.array(sizes)
    # percent=100.*y/y.sum()
    # print(x,y)
    # patches, texts = plt.pie(y,shadow=True, startangle=90, labels= labels,textprops={'fontsize': 8})
    # labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(x, percent)]
    # sort_legend = True
    # if sort_legend:
    #     patches, labels, dummy = zip(*sorted(zip(patches, labels, y),
    #                                          key=lambda x: x[2],
    #                                          reverse=True))
    #
    # plt.legend(patches, labels, loc='center left', bbox_to_anchor=(-0.35, .5),
    #            fontsize=8)

    fig1, ax1 = plt.subplots()
    sizes_f=[]
    total_size=0
    for i in range(len(sizes)):
        sizes_f.append(float(sizes[i]))
        total_size=total_size+sizes_f[i]

    for i in range(len(labels)):
        labels[i]=labels[i]+' '+str(round(sizes_f[i]*100./total_size,2))+'%'
    ax1.pie(sizes,  labels=labels,
            shadow=True, startangle=90,textprops={'fontsize': size})
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.


    plt.show()
# find the positions of inital steps
def initial_Step(address):
    file = open(address)
    lines = file.readlines()
    line_len = len(lines)

    x1 = []
    y1 = []
    z1 = []
    x2 = []
    y2 = []
    z2 = []

    count = 0
    teflon_count = 0
    teflon_abs_count = 0
    for i in range(line_len):
        line_list = lines[i].split()
        # print(line_list)
        try:
            if line_list[0] == 'Step#':
                count = count + 1
                # print(line_list)
                last_step_track = lines[i + 1].split()


                x1.append(float(last_step_track[1]))
                y1.append(float(last_step_track[2]))
                z1.append(float(last_step_track[3]))

        except:
            pass

    # print(x1,'\n',y1,'\n',z1)

    plot_xyz(x1[:1000], y1[:1000], z1[:1000])
    # plot_xyz(x1, y1, z1)
    # plot_xy(x1[:1000], y1[:1000])
    # plot_xy(x1,y1)
    return (0)

def bar_plot(label_list, count_list):
    fig1, ax1 = plt.subplots()
    print(label_list, count_list)
    ax1.bar(label_list,count_list)
    ax1.set_xlabel('SiPM Row')
    ax1.set_ylabel('Counts')

    for i, v in enumerate(count_list):
        ax1.text(i-.15, v+3, str(v))
    plt.show()

def hbar_plot(label_list, count_list):
    fig1, ax1 = plt.subplots()
    print(label_list, count_list)
    ax1.barh(label_list,count_list)
    ax1.set_xlabel('Counts')
    ax1.set_ylabel('Volumes')
    ax1.invert_yaxis()
    plt.show()


#read macro output file, locate the all last steps, count them and clasify them into different types and plot pie chart.
def other_list(address):
    file=open(address)
    # file=open("runtest1.txt")
    lines=file.readlines()
    line_len=len(lines)
    sipm_matrix={}
    new_dic={"Flange":0,"Hyspan_bellow":0,"PV_spool":0,"Inside_vacuum_vessel":0,"LAr_phys":0,"reflector_Cu":0,"OJ_Spacer":0,"hydraulic_fluid":0,"Piezo_Cu":0,"SiPM":0,"Top_sf":0,"Top_sf":0,"Guide_rod_flange":0,"SiPM_PCB":0,
         "reflector_Ny":0,"Base_SF":0,"Side_support":0,"Guide_Rod":0,"Bottom_Spacer":0,"Quartz":0,"Main":0}
    new_label=[]
    new_count=[]
    other_list = []
    count=0
    for i in range(line_len):
        line_list=lines[i].split()
        # print(line_list)
        try:
            if line_list[0] =='LXe':
                count=count+1
                # print(line_list)
                last_step_track=lines[i-1].split()

                key=last_step_track[-2]+' '+last_step_track[-1]
                if key in sipm_matrix.keys():
                    sipm_matrix[key] = sipm_matrix[key] + 1
                else:
                    sipm_matrix[key] = 1



        except:
            pass
    print(sipm_matrix)
    for key in sipm_matrix:

        if "Flange" in key or "top_flange" in key:
            new_dic["Flange"]=new_dic["Flange"]+sipm_matrix[key]

        elif "Hyspan_bellow" in key:
            new_dic["Hyspan_bellow"] = new_dic["Hyspan_bellow"] + sipm_matrix[key]
        elif "PV_spool" in key:
            new_dic["PV_spool"] = new_dic["PV_spool"] + sipm_matrix[key]
        elif "Inside_vacuum_vessel" in key:
            new_dic["Inside_vacuum_vessel"] = new_dic["Inside_vacuum_vessel"] + sipm_matrix[key]
        elif "LAr_phys" in key:
            new_dic["LAr_phys"] = new_dic["LAr_phys"] + sipm_matrix[key]
        elif "reflector_Cu" in key or 'reflector_top_Cu' in key:
            new_dic["reflector_Cu"] = new_dic["reflector_Cu"] + sipm_matrix[key]
        elif "OJ_Spacer" in key:
            new_dic["OJ_Spacer"] = new_dic["OJ_Spacer"] + sipm_matrix[key]
        elif "hydraulic_fluid" in key:
            new_dic["hydraulic_fluid"] = new_dic["hydraulic_fluid"] + sipm_matrix[key]
        elif "Piezo_Cu" in key:
            new_dic["Piezo_Cu"] = new_dic["Piezo_Cu"] + sipm_matrix[key]
        # first sipm_pcb then sipm
        elif "SiPM_PCB" in key:
            new_dic["SiPM_PCB"] = new_dic["SiPM_PCB"] + sipm_matrix[key]
        elif "SiPM1_phys" in key or "SiPM2_phys" in key or "SiPM3_phys" in key or "SiPM4_phys" in key or "SiPM5_phys" in key:
            new_dic["SiPM"] = new_dic["SiPM"] + sipm_matrix[key]
        elif "SiPM1_Inside_phys" in key or "SiPM2_Inside_phys" in key or "SiPM3_Inside_phys" in key or "SiPM4_Inside_phys" in key or "SiPM5_Inside_phys" in key:
            new_dic["SiPM"] = new_dic["SiPM"] + sipm_matrix[key]
        elif "Top_sf" in key:
            new_dic["Top_sf"] = new_dic["Top_sf"] + sipm_matrix[key]
        elif "Guide_rod_flange" in key:
            new_dic["Guide_rod_flange"] = new_dic["Guide_rod_flange"] + sipm_matrix[key]
        elif "reflector_Ny" in key or "reflector_top_Ny" in key:
            new_dic["reflector_Ny"] = new_dic["reflector_Ny"] + sipm_matrix[key]
        elif "Base_SF" in key:
            new_dic["Base_SF"] = new_dic["Base_SF"] + sipm_matrix[key]
        elif "Side_support" in key:
            new_dic["Side_support"] = new_dic["Side_support"] + sipm_matrix[key]
        elif "Guide_Rod" in key:
            new_dic["Guide_Rod"] = new_dic["Guide_Rod"] + sipm_matrix[key]
        elif "Bottom_Spacer" in key:
            new_dic["Bottom_Spacer"] = new_dic["Bottom_Spacer"] + sipm_matrix[key]
        elif "Quartz" in key:
            new_dic["Quartz"] = new_dic["Quartz"] + sipm_matrix[key]
        else:
            new_dic["Main"] = new_dic["Main"] + sipm_matrix[key]
            other_list.append(key)

    for key in new_dic:
        new_label.append(key)
        new_count.append(float(new_dic[key]))




    # plot_xyz(x,y,z)
    # pie_chart(new_label,new_count)
    del new_dic['Main']
    decending_dic= sorted_dic(new_dic, reverse= True)
    print('decending list',decending_dic)

    print('otherlist',other_list)
    x, y = sorted_dic_to_2dlist(decending_dic)
    hbar_plot(x, y)
    return(0)


def sorted_dic(dic, reverse =  False):
    return dict(sorted(dic.items(),key = lambda x: x[1], reverse =  reverse))

def sorted_dic_to_2dlist(dic):
    label=[]
    list=[]
    for key in dic:
        label.append(key)
        list.append(dic[key])

    return label, list

def plot_delta():
    x = np. arange(0,1,0.1)
    plt.plot(x,x*(1+x)/(1-x))
    plt.xlabel("light attenuation between two reflections delta")
    plt.ylabel("delata contribution to PCE d*(1+d)/(1-d)")
    plt.axvline(x=1/2.7, label="1/e, travels with a absorption length",color="red")
    plt.axvline(x=1 /(2.7)**(1/2), label="1/sqrt(e), travels with half absorption length",color="orange")
    plt.legend()
    plt.show()




if __name__=="__main__":
    # get hits number and plot positions
    # print(os.getcwd())
    # base = os.getcwd()
    # Infoaddress = 'fixed_sim\\95r100abs_v2\\PmtInformation.txt'
    # fullInfoaddress=os.path.join(base, Infoaddress)
    # read_Information(fullInfoaddress)

    # read_Information('PmtInformation100.txt')

    #pie chart

    # print(os.getcwd())
    # base = os.getcwd()
    # OUTaddress = 'D:\\GIthub\\runze\\sbcGEANT4\\SBC\\SBCbuild\\output\\CF4_noreflection.txt'
    # # OUTaddress = 'fixed_sim\\95r100abs_v2\\95r100abs.txt'
    # # OUTaddress = 'fixed_sim\\99r100abs\\99r100abs.txt'
    # fullOUTaddress = os.path.join(base, OUTaddress)
    # sipm_pie(fullOUTaddress)


    # read_key_txt(KEY2='pressure_vessel_phys')
    # initial_Step()

    # x=['SIPM1_Si', 'SIPM2_Si','SIPM3_Si','SIPM4_Si','SIPM5_Si']
    # y=[865,810,766,641,498]
    # bar_plot(x,y)

    # print(os.getcwd())
    # base = os.getcwd()
    # OUTaddress = 'fixed_sim\\95r100abs\\95r100abs.txt'
    # fullOUTaddress = os.path.join(base, OUTaddress)
    # other_list(fullOUTaddress)

    # plot_xy([6.53,6.89,7.29],[83.258,41.474,5.056])

    plot_delta()









