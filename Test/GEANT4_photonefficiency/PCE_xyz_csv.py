#translate G4 output file into list

import matplotlib.pyplot as plt
from matplotlib import colors, cm
import numpy as np
import os, pickle
import pandas as pd

class photon_efficiency_measurement():
    def __init__(self, parent=None, join='Q_sigma_Info.txt'):
        # super().__init__(parent)
        print(os.getcwd())
        self.base = "D:\\GIthub\\runze\\Test\\GEANT4_photonefficiency\\PCE"

        self.iniaddress = 'PCE_ini_0405.csv'
        self.fulliniaddress = os.path.join(self.base, self.iniaddress)
        self.finaddress = 'PCE_fin_0405.csv'
        self.fullfinaddress = os.path.join(self.base, self.finaddress)
        self.outputfile = 'result_ini_0406.csv'
        # ONe entry like this event number : (incident energy(float, ev), outgoing(bool), Q Value (float) in MeV)
        self.INFOmatrix = {}




    def read_Information(self):
        df_ini = pd.read_csv(self.fulliniaddress)
        df_fin = pd.read_csv(self.fullfinaddress)
        print(df_ini.head(5))




        event_pointer = -1
        track_pointer = 1

        for idx in range(len(df_ini.index)):
        # for idx in range(100):

            try:
                
                
                
                
                if event_pointer == df_ini.iloc[idx]['Event']:
                    pass
        #
                else:
                    print(idx)
                    event_pointer = df_ini.iloc[idx]['Event']
                    pass

                self.INFOmatrix[event_pointer] = [df_ini.iloc[idx]['x'], df_ini.iloc[idx]['y'],df_ini.iloc[idx]['z'],False]



            except Exception as e:
                print(e)

        event_pointer = -1
        for idx in range(len(df_fin.index)):
        # for idx in range(3):

            try:

                if event_pointer == df_fin.iloc[idx]['m']:
                    pass
                #
                else:
                    print(idx)
                    event_pointer = df_fin.iloc[idx]['m']
                    pass

                self.INFOmatrix[event_pointer][3] = True



            except Exception as e:
                print(e)
        # print(self.INFOmatrix)
        wdf = pd.DataFrame.from_dict(self.INFOmatrix, orient = 'index', columns=['x','y','z','Hit'])
        wdf.to_csv(self.outputfile, sep=',')


    def plot_Q(self, read =False):
        # print(self.INFOmatrix)

        if read:
            df_ini=pd.read_csv(self.outputfile)

        self.Q_list= df_ini['Q'].to_list()
        print(self.Q_list)


        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title('Q Value in G4 Calibration')
        ax.set_xlabel('Q Value/MeV')
        ax.set_ylabel('entries/bin')
        plt.hist(self.Q_list,bins=70, range=(5.8*10**6,6.5*10**6) ,log= True)
        plt.show()



        return 0
    def plot_hist(self, read = False):
        bins=20
        print(self.outputfile)
        if read:
            df=pd.read_csv(self.outputfile)
            # df = pd.read_csv(self.outputfile, nrows = 20)
        else:
            print("You have to first run read_information() function before plot_cross if read = False. Otherwise might cause error!")


        Ini_x = df['x'].to_list()
        Ini_y = df['y'].to_list()
        Ini_z = df['z'].to_list()

        # Ini_z = df[(df['y']<25) & (df['y']>-25)]['z'].to_list()
        Fin_x = df[df['Hit']==True]['x'].to_list()
        Fin_y = df[df['Hit']==True]['y'].to_list()
        Fin_z = df[df['Hit']==True]['z'].to_list()
        # Fin_z = df[(df['Hit'] == True) &(df['y']<25) & (df['y']>-25)]['z'].to_list()


        print('x',Ini_x, '\n', Fin_x)

        fig, axs = plt.subplots(2, 3, figsize=(9, 3))
        (h0, xedge0, yedge0, image0) = axs[0, 0].hist2d(Ini_x, Ini_y, bins=bins, norm = colors.Normalize(),cmap='plasma')

        axs[0, 0].set_title('Ini_Distribution_xy')
        axs[0, 0].grid(which='both')
        axs[0, 0].set_xlabel('x/mm')
        axs[0, 0].set_ylabel('y/mm')

        (h1, xedge1, zedge1, image1) = axs[1, 0].hist2d(Ini_x, Ini_z, bins=bins, norm = colors.Normalize(),cmap='plasma')
        axs[1, 0].set_title('Ini_Distribution_xz')
        axs[1, 0].grid(which='both')
        axs[1, 0].set_xlabel('x/mm')
        axs[1, 0].set_ylabel('z/mm')

        (h2, xedge2, yedge2, image2) = axs[0, 1].hist2d(Fin_x, Fin_y, bins=bins, norm = colors.Normalize(),cmap='plasma')
        axs[0, 1].set_title('Fin_Distribution_xy')
        axs[0, 1].grid(which='both')
        axs[0, 1].set_xlabel('x/mm')
        axs[0, 1].set_ylabel('y/mm')

        (h3, xedge3, zedge3, image3) = axs[1, 1].hist2d(Fin_x, Fin_z, bins=bins, norm = colors.Normalize(),cmap='plasma')
        axs[1, 1].set_title('Fin_Distribution_xz')
        axs[1, 1].grid(which='both')
        axs[1, 1].set_xlabel('x/mm')
        axs[1, 1].set_ylabel('z/mm')


        xy_2d_effi_array=np.zeros((bins,bins))
        print('h1', xedge1, zedge1,len(h1), h1)
        Ini_xy_x_low=xedge0[0]
        Ini_xy_x_up=xedge0[-1]
        Ini_xy_y_low = yedge0[0]
        Ini_xy_y_up = yedge0[-1]
        for i in range(bins):
            for j in range(bins):
                if h0[i][j] != 0:
                    element_xy = h2[i][j]/h0[i][j]
                else:
                    element_xy = 0
                xy_2d_effi_array[i][j]=element_xy

        image4 = axs[0, 2].imshow(xy_2d_effi_array,extent=(Ini_xy_x_low, Ini_xy_x_up, Ini_xy_y_low, Ini_xy_y_up))
        axs[0, 2].set_title('Efficiency Distribution')
        axs[0, 2].set_xlabel('x/mm')
        axs[0, 2].set_ylabel('y/mm')

        xz_2d_effi_array = np.zeros((bins, bins))
        Ini_xz_x_low = xedge1[0]
        Ini_xz_x_up = xedge1[-1]
        Ini_xz_z_low = zedge1[0]
        Ini_xz_z_up = zedge1[-1]

        for i in range(bins):
            for j in range(bins):
                if h1[i][j]!= 0:
                    element_xz = h3[i][j]/h1[i][j]
                else:
                    element_xz = 0
                xz_2d_effi_array[i][j]=element_xz
        image5 = axs[1, 2].imshow(xz_2d_effi_array, extent=(Ini_xz_x_low, Ini_xz_x_up, Ini_xz_z_low, Ini_xz_z_up))
        axs[1, 2].set_title('Efficiency Distribution')
        axs[1, 2].set_xlabel('x/mm')
        axs[1, 2].set_ylabel('z/mm')

        fig.colorbar(image0, ax = axs[0,0])
        fig.colorbar(image1, ax=axs[0, 1])
        fig.colorbar(image2, ax=axs[0, 2])
        fig.colorbar(image3, ax=axs[1, 0])
        fig.colorbar(image4, ax=axs[1, 1])
        fig.colorbar(image5, ax=axs[1, 2])


        plt.show()

    def PCE_count(self, read=False):
        if read:
            df = pd.read_csv(self.outputfile)
        Ini_list_len=len(df['x'].to_list())
        Fin_list_len=len(df[df['Hit'] == True]['x'].to_list())
        print("Ini",Ini_list_len,"Fin", Fin_list_len,"PCE",Fin_list_len/Ini_list_len)

    def plot_hist_y0plane(self, read=False):
        bins = 40
        print(self.outputfile)
        if read:
            df = pd.read_csv(self.outputfile)
            # df = pd.read_csv(self.outputfile, nrows=20)
        else:
            print("You have to first run read_information() function before plot_cross if read = False. Otherwise might cause error!")

        Ini_x = df['x'].to_list()
        Ini_y = df['y'].to_list()
        # Ini_z = df['z'].to_list()
        Ini_x1 = df[(df['y'] < 25) & (df['y'] > -25)]['x'].to_list()
        Ini_z1 = df[(df['y']<25) & (df['y']>-25)]['z'].to_list()
        Fin_x = df[df['Hit'] == True]['x'].to_list()
        Fin_y = df[df['Hit'] == True]['y'].to_list()
        # Fin_z = df[df['Hit'] == True]['z'].to_list()
        Fin_x1 = df[(df['Hit'] == True) & (df['y'] < 25) & (df['y'] > -25)]['x'].to_list()
        Fin_z1 = df[(df['Hit'] == True) &(df['y']<25) & (df['y']>-25)]['z'].to_list()

        print('x', Ini_x, '\n', Fin_x)

        fig, axs = plt.subplots(2, 3, figsize=(9, 3))
        (h0, xedge0, yedge0, image0) = axs[0, 0].hist2d(Ini_x, Ini_y, bins=bins, norm=colors.Normalize(), cmap='plasma')

        axs[0, 0].set_title('(a) Ini_Distribution_xy')
        axs[0, 0].grid(which='both')
        axs[0, 0].set_xlabel('x/mm')
        axs[0, 0].set_ylabel('y/mm')

        (h1, xedge1, zedge1, image1) = axs[1, 0].hist2d(Ini_x1, Ini_z1, bins=bins, norm=colors.Normalize(), cmap='plasma')
        axs[1, 0].set_title('(d) Ini_Distribution_xz')
        axs[1, 0].grid(which='both')
        axs[1, 0].set_xlabel('x/mm')
        axs[1, 0].set_ylabel('z/mm')

        (h2, xedge2, yedge2, image2) = axs[0, 1].hist2d(Fin_x, Fin_y, bins=bins, norm=colors.Normalize(), cmap='plasma')
        axs[0, 1].set_title('(b) Fin_Distribution_xy')
        axs[0, 1].grid(which='both')
        axs[0, 1].set_xlabel('x/mm')
        axs[0, 1].set_ylabel('y/mm')

        (h3, xedge3, zedge3, image3) = axs[1, 1].hist2d(Fin_x1, Fin_z1, bins=bins, norm=colors.Normalize(), cmap='plasma')
        axs[1, 1].set_title('(e) Fin_Distribution_xz')
        axs[1, 1].grid(which='both')
        axs[1, 1].set_xlabel('x/mm')
        axs[1, 1].set_ylabel('z/mm')

        xy_2d_effi_array = np.zeros((bins, bins))
        print('h1', xedge1, '\n',zedge1,'\n', len(h1),'\n', h1)
        Ini_xy_x_low = xedge0[0]
        Ini_xy_x_up = xedge0[-1]
        Ini_xy_y_low = yedge0[0]
        Ini_xy_y_up = yedge0[-1]
        for i in range(bins):
            for j in range(bins):
                if h0[i][j] != 0:
                    element_xy = h2[i][j] / h0[i][j]
                else:
                    element_xy = 0
                xy_2d_effi_array[i][j] = element_xy

        image4 = axs[0, 2].imshow(np.rot90(xy_2d_effi_array,1), extent=(Ini_xy_x_low, Ini_xy_x_up, Ini_xy_y_low, Ini_xy_y_up), cmap='plasma')
        axs[0, 2].set_title('(c) Efficiency Distribution')
        axs[0, 2].set_xlabel('x/mm')
        axs[0, 2].set_ylabel('y/mm')

        xz_2d_effi_array = np.zeros((bins, bins))
        Ini_xz_x_low = xedge1[0]
        Ini_xz_x_up = xedge1[-1]
        Ini_xz_z_low = zedge1[0]
        Ini_xz_z_up = zedge1[-1]

        for j in range(bins):
            for i in range(bins):
                if h1[i][j] != 0:
                    element_xz = h3[i][j] / h1[i][j]
                else:
                    element_xz = 0
                xz_2d_effi_array[i][j] = element_xz
        # image5 = axs[1, 2].imshow(xz_2d_effi_array, extent=(Ini_xz_x_low, Ini_xz_x_up, Ini_xz_z_low, Ini_xz_z_up),cmap='plasma')
        image5 = axs[1, 2].imshow(np.rot90(xz_2d_effi_array), extent=(Ini_xz_x_low, Ini_xz_x_up, Ini_xz_z_low, Ini_xz_z_up), cmap='plasma')
        axs[1, 2].set_title('(f) Efficiency Distribution')
        axs[1, 2].set_xlabel('x/mm')
        axs[1, 2].set_ylabel('z/mm')

        fig.colorbar(image0, ax=axs[0, 0])
        fig.colorbar(image1, ax=axs[1, 0])
        fig.colorbar(image2, ax=axs[0, 1])
        fig.colorbar(image3, ax=axs[1, 1])
        fig.colorbar(image4, ax=axs[0, 2])
        fig.colorbar(image5, ax=axs[1, 2])


        plt.show()

    def plot_hist_rzplane(self, read=False):
        bins = 40
        print(self.outputfile)
        if read:
            df = pd.read_csv(self.outputfile)
            # df = pd.read_csv(self.outputfile, nrows=10000)
            # df = pd.read_csv(self.outputfile, nrows=2000)
        else:
            print("You have to first run read_information() function before plot_cross if read = False. Otherwise might cause error!")


        Ini_x = df['x'].to_list()
        Ini_y = df['y'].to_list()
        Ini_z = df['z'].to_list()
        Ini_r = []
        for i in range(len(Ini_x)):
            Ini_r.append(np.sqrt((Ini_x[i])**2+(Ini_y[i])**2))
        Fin_x = df[df['Hit'] == True]['x'].to_list()
        Fin_y = df[df['Hit'] == True]['y'].to_list()
        Fin_z = df[df['Hit'] == True]['z'].to_list()
        Fin_r = []
        for i in range(len(Fin_x)):
            Fin_r.append(np.sqrt((Fin_x[i]) ** 2 + (Fin_y[i]) ** 2))

        print('x', Ini_x, '\n', Fin_x)

        # fig, axs = plt.subplots(2, 3, figsize=(9, 3))

        fig = plt.figure()
        ax0 = fig.add_subplot(2,3,1,projection ='3d')
        (h0, xedge0, yedge0) = np.histogram2d(Ini_x, Ini_y, bins=bins)
        xpos0, ypos0 = np.meshgrid(xedge0[:-1],yedge0[:-1], indexing = "ij")
        xpos0 = xpos0.ravel()
        ypos0 = ypos0.ravel()
        vpos0 = 0
        dx0 = xedge0[1]-xedge0[0]
        dy0 = yedge0[1]-yedge0[0]
        dv0 = h0.ravel()

        cmap0 = cm.get_cmap('plasma')
        norm0 = colors.Normalize(vmin=min(dv0), vmax= max(dv0))
        colors0=cmap0(norm0(dv0))

        ax0.bar3d(xpos0, ypos0, vpos0, dx0, dy0, dv0, zsort='average', color=colors0)
        sc0 = cm.ScalarMappable(cmap=cmap0, norm=norm0)
        sc0.set_array([])
        plt.colorbar(sc0)

        # ax0.azim = 300
        # ax0.elev = 30

        # ax0.bar3d(xpos0, vpos0, ypos0, dx0, dw0, dy0, zsort='average')

        ax0.set_title('(a) Ini_Distribution_xy')
        ax0.set_xlabel('x/mm')
        ax0.set_ylabel('y/mm')

        ax1 = fig.add_subplot(2, 3, 4, projection='3d')
        RWeight1= []
        for ele in Ini_r:
            if ele != 0:
                RWeight1.append(2*3.1415/(ele))
            else:
                RWeight1.append(0)
        (h1, redge1, zedge1) = np.histogram2d(Ini_r, Ini_z, bins=bins, normed = False, weights = RWeight1)
        rpos1, zpos1 = np.meshgrid(redge1[:-1], zedge1[:-1], indexing="ij")
        rpos1 = rpos1.ravel()
        zpos1 = zpos1.ravel()
        vpos1 = 0
        dr1 = redge1[1] - redge1[0]
        dz1 = zedge1[1] - zedge1[0]
        dv1 = h1.ravel()

        # cut the abnormal value to make figure displayed in a reasonable range
        for ele in dv1:
            if ele  >= 0.005:
                ele = 0.005

        cmap1 = cm.get_cmap('plasma')
        norm1 = colors.Normalize(vmin=min(dv1), vmax=max(dv1))
        colors1 = cmap1(norm1(dv1))

        ax1.bar3d(rpos1, zpos1, vpos1, dr1, dz1, dv1, zsort='average',color=colors1)
        ax1.set_title('(d) Ini_Distribution_rz')
        ax1.set_xlabel('r/mm')
        ax1.set_ylabel('z/mm')

        sc1 = cm.ScalarMappable(cmap=cmap1, norm=norm1)
        sc1.set_array([])
        plt.colorbar(sc1)

        #xdege2 != xedge0 when sample number is not large enough!
        ax2 = fig.add_subplot(2, 3, 2, projection='3d')
        (h2, xedge2, yedge2) = np.histogram2d(Fin_x, Fin_y, bins=bins)
        xpos2, ypos2 = np.meshgrid(xedge2[:-1], yedge2[:-1], indexing="ij")
        xpos2 = xpos2.ravel()
        ypos2 = ypos2.ravel()
        vpos2 = 0
        dx2 = xedge2[1] - xedge2[0]
        dy2 = yedge2[1] - yedge2[0]
        dv2 = h2.ravel()

        cmap2 = cm.get_cmap('plasma')
        norm2 = colors.Normalize(vmin=min(dv2), vmax=max(dv2))
        colors2 = cmap2(norm2(dv2))

        ax2.bar3d(xpos2, ypos2, vpos2, dx2, dy2, dv2, zsort='average', color=colors2)
        ax2.set_title('(b) Fin_Distribution_xy')
        ax2.set_xlabel('x/mm')
        ax2.set_ylabel('y/mm')

        sc2 = cm.ScalarMappable(cmap=cmap2, norm=norm2)
        sc2.set_array([])
        plt.colorbar(sc2)

        ax3 = fig.add_subplot(2, 3, 5, projection='3d')

        RWeight3 = []
        for ele in Fin_r:
            if ele != 0:
                RWeight3.append(1 / (ele))
            else:
                RWeight3.append(0)
        (h3, redge3, zedge3) = np.histogram2d(Fin_r, Fin_z, bins=bins, normed=False, weights=RWeight3)

        rpos3, zpos3 = np.meshgrid(redge3[:-1], zedge3[:-1], indexing="ij")
        rpos3 = rpos3.ravel()
        zpos3 = zpos3.ravel()
        vpos3 = 0
        dr3 = redge3[1] - redge3[0]
        dz3 = zedge3[1] - zedge3[0]
        dv3 = h3.ravel()

        for ele in dv3:
            if ele  >= 0.005:
                ele = 0.005

        cmap3 = cm.get_cmap('plasma')
        norm3 = colors.Normalize(vmin=min(dv3), vmax=max(dv3))
        colors3 = cmap3(norm3(dv3))

        RWeight3 = []
        for ele in Fin_r:
            if ele != 0:
                RWeight3.append(2*3.1415 / (ele) ** 2)
            else:
                RWeight3.append(0)

        ax3.bar3d(rpos3, zpos3, vpos3, dr3, dz3, dv3, zsort='average', color=colors3)
        ax3.set_title('(e) Fin_Distribution_rz')
        ax3.set_xlabel('r/mm')
        ax3.set_ylabel('z/mm')

        sc3 = cm.ScalarMappable(cmap=cmap3, norm=norm3)
        sc3.set_array([])
        plt.colorbar(sc3)


        xy_2d_effi_array = np.zeros((bins, bins))
        # print('h1', xedge0, '\n',zedge0,'\n', len(h1),'\n', h1)
        Ini_xy_x_low = xedge0[0]
        Ini_xy_x_up = xedge0[-1]
        Ini_xy_y_low = yedge0[0]
        Ini_xy_y_up = yedge0[-1]
        for i in range(bins):
            for j in range(bins):
                if h0[i][j] != 0:
                    element_xy = h2[i][j] / h0[i][j]
                else:
                    element_xy = 0
                xy_2d_effi_array[i][j] = element_xy
                # if  element_xy >1:
                #     print("efficiency value error",element_xy,"h2",h2[i][j],"h0",h0[i][j],"ij",i,j)

        # xy_2d_effi_array=np.rot90(xy_2d_effi_array)


        ax4 = fig.add_subplot(2, 3, 3, projection='3d')
        (h4, xedge4, yedge4) = np.histogram2d(Fin_x, Fin_y, bins=bins)
        xpos4, ypos4 = np.meshgrid(xedge4[:-1], yedge4[:-1], indexing="ij")
        xpos4 = xpos4.ravel()
        ypos4 = ypos4.ravel()
        vpos4 = 0
        dx4 = xedge4[1] - xedge4[0]
        dy4 = yedge4[1] - yedge4[0]
        dv4 = xy_2d_effi_array.ravel()

        cmap4 = cm.get_cmap('plasma')
        norm4 = colors.Normalize(vmin=min(dv4), vmax=max(dv4))
        colors4 = cmap4(norm4(dv4))

        ax4.bar3d(xpos4, ypos4, vpos4, dx4, dy4, dv4, zsort='average', color=colors4)

        ax4.set_title('(c) Efficiency')
        ax4.set_xlabel('x/mm')
        ax4.set_ylabel('y/mm')

        sc4 = cm.ScalarMappable(cmap=cmap4, norm=norm4)
        sc4.set_array([])
        plt.colorbar(sc4)

        rz_2d_effi_array = np.zeros((bins, bins))
        # print('h1', xedge0, '\n',zedge0,'\n', len(h1),'\n', h1)
        for i in range(bins):
            for j in range(bins):
                if h1[i][j] != 0:
                    element_rz = h3[i][j] / h1[i][j]
                else:
                    element_rz = 0
                if element_rz >0.02:
                    element_rz =0.02
                rz_2d_effi_array[i][j] = element_rz

        # rz_2d_effi_array = np.rot90(rz_2d_effi_array)

        ax5 = fig.add_subplot(2, 3, 6, projection='3d')
        (h5, redge5, zedge5) = np.histogram2d(Fin_r, Fin_z, bins=bins)
        rpos5, zpos5 = np.meshgrid(redge5[:-1], zedge5[:-1], indexing="ij")
        rpos5 = rpos5.ravel()
        zpos5 = zpos5.ravel()
        vpos5 = 0
        dr5 = redge5[1] - redge5[0]
        dz5 = zedge5[1] - zedge5[0]
        dv5 = rz_2d_effi_array.ravel()

        cmap5 = cm.get_cmap('plasma')
        norm5 = colors.Normalize(vmin=min(dv5), vmax=max(dv5))
        colors5 = cmap5(norm5(dv5))

        ax5.bar3d(rpos5, zpos5, vpos5, dr5, dz5, dv5, zsort='average', color=colors5)
        ax5.set_title('(e) Efficiency')
        ax5.set_xlabel('r/mm')
        ax5.set_ylabel('z/mm')

        sc5 = cm.ScalarMappable(cmap=cmap5, norm=norm5)
        sc5.set_array([])
        plt.colorbar(sc5)
        #

        plt.show()

    def plot_hist_nonrzplane(self, read=False):
        bins = 40
        print(self.outputfile)
        if read:
            df = pd.read_csv(self.outputfile)
            # df = pd.read_csv(self.outputfile, nrows=10000)
            # df = pd.read_csv(self.outputfile, nrows=2000)
        else:
            print("You have to first run read_information() function before plot_cross if read = False. Otherwise might cause error!")


        Ini_x = df['x'].to_list()
        Ini_y = df['y'].to_list()
        Ini_z = df['z'].to_list()
        Ini_r = []
        for i in range(len(Ini_x)):
            Ini_r.append(np.sqrt((Ini_x[i])**2+(Ini_y[i])**2))
        Fin_x = df[df['Hit'] == True]['x'].to_list()
        Fin_y = df[df['Hit'] == True]['y'].to_list()
        Fin_z = df[df['Hit'] == True]['z'].to_list()
        Fin_r = []
        for i in range(len(Fin_x)):
            Fin_r.append(np.sqrt((Fin_x[i]) ** 2 + (Fin_y[i]) ** 2))

        print('x', Ini_x, '\n', Fin_x)

        # fig, axs = plt.subplots(2, 3, figsize=(9, 3))

        fig = plt.figure()
        ax0 = fig.add_subplot(2,3,1,projection ='3d')
        (h0, xedge0, yedge0) = np.histogram2d(Ini_x, Ini_y, bins=bins)
        xpos0, ypos0 = np.meshgrid(xedge0[:-1],yedge0[:-1], indexing = "ij")
        xpos0 = xpos0.ravel()
        ypos0 = ypos0.ravel()
        vpos0 = 0
        dx0 = xedge0[1]-xedge0[0]
        dy0 = yedge0[1]-yedge0[0]
        dv0 = h0.ravel()

        cmap0 = cm.get_cmap('plasma')
        norm0 = colors.Normalize(vmin=min(dv0), vmax= max(dv0))
        colors0=cmap0(norm0(dv0))

        ax0.bar3d(xpos0, ypos0, vpos0, dx0, dy0, dv0, zsort='average', color=colors0)
        sc0 = cm.ScalarMappable(cmap=cmap0, norm=norm0)
        sc0.set_array([])
        plt.colorbar(sc0)

        # ax0.azim = 300
        # ax0.elev = 30

        # ax0.bar3d(xpos0, vpos0, ypos0, dx0, dw0, dy0, zsort='average')

        ax0.set_title('(a) Ini_Distribution_xy')
        ax0.set_xlabel('x/mm')
        ax0.set_ylabel('y/mm')

        ax1 = fig.add_subplot(2, 3, 4, projection='3d')
        RWeight1= []
        for ele in Ini_r:
            if ele != 0:
                RWeight1.append(1)
            else:
                RWeight1.append(0)
        (h1, redge1, zedge1) = np.histogram2d(Ini_r, Ini_z, bins=bins, normed = False, weights = RWeight1)
        rpos1, zpos1 = np.meshgrid(redge1[:-1], zedge1[:-1], indexing="ij")
        rpos1 = rpos1.ravel()
        zpos1 = zpos1.ravel()
        vpos1 = 0
        dr1 = redge1[1] - redge1[0]
        dz1 = zedge1[1] - zedge1[0]
        dv1 = h1.ravel()

        # cut the abnormal value to make figure displayed in a reasonable range
        for ele in dv1:
            if ele  >= 0.005:
                ele = 0.005

        cmap1 = cm.get_cmap('plasma')
        norm1 = colors.Normalize(vmin=min(dv1), vmax=max(dv1))
        colors1 = cmap1(norm1(dv1))

        ax1.bar3d(rpos1, zpos1, vpos1, dr1, dz1, dv1, zsort='average',color=colors1)
        ax1.set_title('(d) Ini_Distribution_rz')
        ax1.set_xlabel('r/mm')
        ax1.set_ylabel('z/mm')

        sc1 = cm.ScalarMappable(cmap=cmap1, norm=norm1)
        sc1.set_array([])
        plt.colorbar(sc1)

        #xdege2 != xedge0 when sample number is not large enough!
        ax2 = fig.add_subplot(2, 3, 2, projection='3d')
        (h2, xedge2, yedge2) = np.histogram2d(Fin_x, Fin_y, bins=bins)
        xpos2, ypos2 = np.meshgrid(xedge2[:-1], yedge2[:-1], indexing="ij")
        xpos2 = xpos2.ravel()
        ypos2 = ypos2.ravel()
        vpos2 = 0
        dx2 = xedge2[1] - xedge2[0]
        dy2 = yedge2[1] - yedge2[0]
        dv2 = h2.ravel()

        cmap2 = cm.get_cmap('plasma')
        norm2 = colors.Normalize(vmin=min(dv2), vmax=max(dv2))
        colors2 = cmap2(norm2(dv2))

        ax2.bar3d(xpos2, ypos2, vpos2, dx2, dy2, dv2, zsort='average', color=colors2)
        ax2.set_title('(b) Fin_Distribution_xy')
        ax2.set_xlabel('x/mm')
        ax2.set_ylabel('y/mm')

        sc2 = cm.ScalarMappable(cmap=cmap2, norm=norm2)
        sc2.set_array([])
        plt.colorbar(sc2)

        ax3 = fig.add_subplot(2, 3, 5, projection='3d')

        RWeight3 = []
        for ele in Fin_r:
            if ele != 0:
                RWeight3.append(1)
            else:
                RWeight3.append(0)
        (h3, redge3, zedge3) = np.histogram2d(Fin_r, Fin_z, bins=bins, normed=False, weights=RWeight3)

        rpos3, zpos3 = np.meshgrid(redge3[:-1], zedge3[:-1], indexing="ij")
        rpos3 = rpos3.ravel()
        zpos3 = zpos3.ravel()
        vpos3 = 0
        dr3 = redge3[1] - redge3[0]
        dz3 = zedge3[1] - zedge3[0]
        dv3 = h3.ravel()

        for ele in dv3:
            if ele  >= 0.005:
                ele = 0.005

        cmap3 = cm.get_cmap('plasma')
        norm3 = colors.Normalize(vmin=min(dv3), vmax=max(dv3))
        colors3 = cmap3(norm3(dv3))

        RWeight3 = []
        for ele in Fin_r:
            if ele != 0:
                RWeight3.append(1)
            else:
                RWeight3.append(0)

        ax3.bar3d(rpos3, zpos3, vpos3, dr3, dz3, dv3, zsort='average', color=colors3)
        ax3.set_title('(e) Fin_Distribution_rz')
        ax3.set_xlabel('r/mm')
        ax3.set_ylabel('z/mm')

        sc3 = cm.ScalarMappable(cmap=cmap3, norm=norm3)
        sc3.set_array([])
        plt.colorbar(sc3)


        xy_2d_effi_array = np.zeros((bins, bins))
        # print('h1', xedge0, '\n',zedge0,'\n', len(h1),'\n', h1)
        Ini_xy_x_low = xedge0[0]
        Ini_xy_x_up = xedge0[-1]
        Ini_xy_y_low = yedge0[0]
        Ini_xy_y_up = yedge0[-1]
        for i in range(bins):
            for j in range(bins):
                if h0[i][j] != 0:
                    element_xy = h2[i][j] / h0[i][j]
                else:
                    element_xy = 0
                xy_2d_effi_array[i][j] = element_xy
                # if  element_xy >1:
                #     print("efficiency value error",element_xy,"h2",h2[i][j],"h0",h0[i][j],"ij",i,j)

        # xy_2d_effi_array=np.rot90(xy_2d_effi_array)


        ax4 = fig.add_subplot(2, 3, 3, projection='3d')
        (h4, xedge4, yedge4) = np.histogram2d(Fin_x, Fin_y, bins=bins)
        xpos4, ypos4 = np.meshgrid(xedge4[:-1], yedge4[:-1], indexing="ij")
        xpos4 = xpos4.ravel()
        ypos4 = ypos4.ravel()
        vpos4 = 0
        dx4 = xedge4[1] - xedge4[0]
        dy4 = yedge4[1] - yedge4[0]
        dv4 = xy_2d_effi_array.ravel()

        cmap4 = cm.get_cmap('plasma')
        norm4 = colors.Normalize(vmin=min(dv4), vmax=max(dv4))
        colors4 = cmap4(norm4(dv4))

        ax4.bar3d(xpos4, ypos4, vpos4, dx4, dy4, dv4, zsort='average', color=colors4)

        ax4.set_title('(c) Efficiency')
        ax4.set_xlabel('x/mm')
        ax4.set_ylabel('y/mm')

        sc4 = cm.ScalarMappable(cmap=cmap4, norm=norm4)
        sc4.set_array([])
        plt.colorbar(sc4)

        rz_2d_effi_array = np.zeros((bins, bins))
        # print('h1', xedge0, '\n',zedge0,'\n', len(h1),'\n', h1)
        for i in range(bins):
            for j in range(bins):
                if h1[i][j] != 0:
                    element_rz = h3[i][j] / h1[i][j]
                else:
                    element_rz = 0
                if element_rz >0.1:
                    element_rz =0.1
                rz_2d_effi_array[i][j] = element_rz

        # rz_2d_effi_array = np.rot90(rz_2d_effi_array)

        ax5 = fig.add_subplot(2, 3, 6, projection='3d')
        (h5, redge5, zedge5) = np.histogram2d(Fin_r, Fin_z, bins=bins)
        rpos5, zpos5 = np.meshgrid(redge5[:-1], zedge5[:-1], indexing="ij")
        rpos5 = rpos5.ravel()
        zpos5 = zpos5.ravel()
        vpos5 = 0
        dr5 = redge5[1] - redge5[0]
        dz5 = zedge5[1] - zedge5[0]
        dv5 = rz_2d_effi_array.ravel()

        cmap5 = cm.get_cmap('plasma')
        norm5 = colors.Normalize(vmin=min(dv5), vmax=max(dv5))
        colors5 = cmap5(norm5(dv5))

        ax5.bar3d(rpos5, zpos5, vpos5, dr5, dz5, dv5, zsort='average', color=colors5)
        ax5.set_title('(f) Efficiency')
        ax5.set_xlabel('r/mm')
        ax5.set_ylabel('z/mm')

        sc5 = cm.ScalarMappable(cmap=cmap5, norm=norm5)
        sc5.set_array([])
        plt.colorbar(sc5)
        #

        plt.show()

    def plot_hist_zplane(self, read=False):
        bins = 20
        colorbar_pos = .10
        abnormal_cut= 0.1
        z_lim_ini =3000
        z_lim_fin = 200
        half_bin = bins/2
        print(self.outputfile)
        if read:
            df = pd.read_csv(self.outputfile)
            # df = pd.read_csv(self.outputfile, nrows=10000)
            # df = pd.read_csv(self.outputfile, nrows=2000)
        else:
            print("You have to first run read_information() function before plot_cross if read = False. Otherwise might cause error!")
        # df['y'] < 25) & (df['y'] > -25)
        Ini_x1 = df[(df['z'] < 500) & (df['z'] > 480)]['x'].to_list()
        Ini_y1 = df[(df['z'] < 500) & (df['z'] > 480)]['y'].to_list()
        Ini_x2 = df[(df['z'] < 400) & (df['z'] > 380)]['x'].to_list()
        Ini_y2 = df[(df['z'] < 400) & (df['z'] > 380)]['y'].to_list()
        Ini_x3 = df[(df['z'] < 620) & (df['z'] > 600)]['x'].to_list()
        Ini_y3 = df[(df['z'] < 620) & (df['z'] > 600)]['y'].to_list()


        Fin_x1 = df[(df['z'] < 500) & (df['z'] > 480) & (df['Hit'] == True)]['x'].to_list()
        Fin_y1 = df[(df['z'] < 500) & (df['z'] > 480) & (df['Hit'] == True)]['y'].to_list()
        Fin_x2 = df[(df['z'] < 400) & (df['z'] > 380) & (df['Hit'] == True)]['x'].to_list()
        Fin_y2 = df[(df['z'] < 400) & (df['z'] > 380) & (df['Hit'] == True)]['y'].to_list()
        Fin_x3 = df[(df['z'] < 620) & (df['z'] > 600) & (df['Hit'] == True)]['x'].to_list()
        Fin_y3 = df[(df['z'] < 620) & (df['z'] > 600) & (df['Hit'] == True)]['y'].to_list()


        # fig, axs = plt.subplots(2, 3, figsize=(9, 3))

        fig = plt.figure()
        ax0 = fig.add_subplot(3,3,4,projection ='3d')
        (h0, xedge0, yedge0) = np.histogram2d(Ini_x1, Ini_y1, bins=bins, range=[[-100,100],[-100,100]])
        # print(h0)
        xpos0, ypos0 = np.meshgrid(xedge0[:-1],yedge0[:-1], indexing = "ij")
        xpos0 = xpos0.ravel()
        ypos0 = ypos0.ravel()
        vpos0 = 0
        dx0 = xedge0[1]-xedge0[0]
        dy0 = yedge0[1]-yedge0[0]
        dv0 = h0.ravel()

        cmap0 = cm.get_cmap('plasma')
        norm0 = colors.Normalize(vmin=min(dv0), vmax= max(dv0))
        colors0=cmap0(norm0(dv0))

        ax0.bar3d(xpos0, ypos0, vpos0, dx0, dy0, dv0, zsort='average', color=colors0)
        sc0 = cm.ScalarMappable(cmap=cmap0, norm=norm0)
        sc0.set_array([])
        plt.colorbar(sc0, pad =colorbar_pos)

        # ax0.azim = 300
        # ax0.elev = 30

        # ax0.bar3d(xpos0, vpos0, ypos0, dx0, dw0, dy0, zsort='average')

        ax0.set_title('(d) Ini_Distribution_xy_middle')
        ax0.set_xlabel('x/mm')
        ax0.set_ylabel('y/mm')
        ax0.set_zlim(0,z_lim_ini)

        ax1 = fig.add_subplot(3, 3, 7, projection='3d')

        (h1, xedge1, yedge1) = np.histogram2d(Ini_x2, Ini_y2, bins=bins, range=[[-100,100],[-100,100]])
        xpos1, ypos1 = np.meshgrid(xedge1[:-1], yedge1[:-1], indexing="ij")
        xpos1 = xpos1.ravel()
        ypos1 = ypos1.ravel()
        vpos1 = 0
        dx1 = xedge1[1] - xedge1[0]
        dy1 = yedge1[1] - yedge1[0]
        dv1 = h1.ravel()

        cmap1 = cm.get_cmap('plasma')
        norm1 = colors.Normalize(vmin=min(dv0), vmax=max(dv0))
        colors1 = cmap1(norm1(dv1))

        ax1.bar3d(xpos1, ypos1, vpos1, dx1, dy1, dv1, zsort='average',color=colors1)
        ax1.set_title('(g) Ini_Distribution_xy_bottom')
        ax1.set_xlabel('x/mm')
        ax1.set_ylabel('y/mm')
        ax1.set_zlim(0,z_lim_ini)

        sc1 = cm.ScalarMappable(cmap=cmap1, norm=norm1)
        sc1.set_array([])
        plt.colorbar(sc1, pad =colorbar_pos)

        #xdege2 != xedge0 when sample number is not large enough!
        ax2 = fig.add_subplot(3, 3, 1, projection='3d')
        (h2, xedge2, yedge2) = np.histogram2d(Ini_x3, Ini_y3, bins=bins,range=[[-100,100],[-100,100]])
        xpos2, ypos2 = np.meshgrid(xedge2[:-1], yedge2[:-1], indexing="ij")
        xpos2 = xpos2.ravel()
        ypos2 = ypos2.ravel()
        vpos2 = 0
        dx2 = xedge2[1] - xedge2[0]
        dy2 = yedge2[1] - yedge2[0]
        dv2 = h2.ravel()

        cmap2 = cm.get_cmap('plasma')
        norm2 = colors.Normalize(vmin=min(dv0), vmax=max(dv0))
        colors2 = cmap2(norm2(dv2))

        ax2.bar3d(xpos2, ypos2, vpos2, dx2, dy2, dv2, zsort='average', color=colors2)
        ax2.set_title('(a) Ini_Distribution_xy_top')
        ax2.set_xlabel('x/mm')
        ax2.set_ylabel('y/mm')
        ax2.set_zlim(0,z_lim_ini)

        sc2 = cm.ScalarMappable(cmap=cmap2, norm=norm2)
        sc2.set_array([])
        plt.colorbar(sc2, pad =colorbar_pos)

        ax3 = fig.add_subplot(3, 3, 5, projection='3d')

        (h3, xedge3, yedge3) = np.histogram2d(Fin_x1, Fin_y1, bins=bins, range=[[-100, 100], [-100, 100]])
        xpos3, ypos3 = np.meshgrid(xedge3[:-1], yedge3[:-1], indexing="ij")
        xpos3 = xpos3.ravel()
        ypos3 = ypos3.ravel()
        vpos3 = 0
        dx3 = xedge3[1] - xedge3[0]
        dy3 = yedge3[1] - yedge3[0]
        dv3 = h3.ravel()

        cmap3 = cm.get_cmap('plasma')
        norm3 = colors.Normalize(vmin=min(dv3), vmax=max(dv3))
        colors3 = cmap3(norm3(dv3))

        ax3.bar3d(xpos3, ypos3, vpos3, dx3, dy3, dv3, zsort='average', color=colors3)
        sc3 = cm.ScalarMappable(cmap=cmap3, norm=norm3)
        sc3.set_array([])
        ax3.set_zlim(0,z_lim_fin)
        plt.colorbar(sc3, pad =colorbar_pos)


        ax3.set_title('(e) Fin_Distribution_xy_middle')
        ax3.set_xlabel('x/mm')
        ax3.set_ylabel('y/mm')

        ax4 = fig.add_subplot(3, 3, 8, projection='3d')
        (h4, xedge4, yedge4) = np.histogram2d(Fin_x2, Fin_y2, bins=bins, range=[[-100, 100], [-100, 100]])
        xpos4, ypos4 = np.meshgrid(xedge4[:-1], yedge4[:-1], indexing="ij")
        xpos4 = xpos4.ravel()
        ypos4 = ypos4.ravel()
        vpos4 = 0
        dx4 = xedge4[1] - xedge4[0]
        dy4 = yedge4[1] - yedge4[0]
        dv4 = h4.ravel()

        cmap4 = cm.get_cmap('plasma')
        norm4 = colors.Normalize(vmin=min(dv3), vmax=max(dv3))
        colors4 = cmap4(norm4(dv4))

        ax4.bar3d(xpos4, ypos4, vpos4, dx4, dy4, dv4, zsort='average', color=colors4)
        sc4 = cm.ScalarMappable(cmap=cmap4, norm=norm4)
        sc4.set_array([])
        ax4.set_zlim(0,z_lim_fin)
        plt.colorbar(sc4, pad =colorbar_pos)

        ax4.set_title('(h) Fin_Distribution_xy_bottom')
        ax4.set_xlabel('x/mm')
        ax4.set_ylabel('y/mm')

        ax5 = fig.add_subplot(3, 3, 2, projection='3d')
        (h5, xedge5, yedge5) = np.histogram2d(Fin_x3, Fin_y3, bins=bins, range=[[-100, 100], [-100, 100]])
        print(xedge5, yedge5)
        xpos5, ypos5 = np.meshgrid(xedge5[:-1], yedge5[:-1], indexing="ij")
        xpos5 = xpos5.ravel()
        ypos5 = ypos5.ravel()
        vpos5 = 0
        dx5 = xedge5[1] - xedge5[0]
        dy5 = yedge5[1] - yedge5[0]
        dv5 = h5.ravel()

        cmap5 = cm.get_cmap('plasma')
        norm5 = colors.Normalize(vmin=min(dv3), vmax=max(dv3))
        colors5 = cmap5(norm5(dv5))

        ax5.bar3d(xpos5, ypos5, vpos5, dx5, dy5, dv5, zsort='average', color=colors5)
        sc5 = cm.ScalarMappable(cmap=cmap5, norm=norm5)
        sc5.set_array([])
        ax5.set_zlim(0,z_lim_fin)
        plt.colorbar(sc5, pad =colorbar_pos)

        ax5.set_title('(b) Fin_Distribution_xy_top')
        ax5.set_xlabel('x/mm')
        ax5.set_ylabel('y/mm')



        ax6 = fig.add_subplot(3, 3, 6, projection='3d')

        xy1_2d_effi_array = np.zeros((bins, bins))

        for i in range(bins):
            for j in range(bins):
                if h0[i][j] != 0:
                    element_xy = h3[i][j] / h0[i][j]
                else:
                    element_xy = 0
                if element_xy >abnormal_cut:
                    element_xy = abnormal_cut
                xy1_2d_effi_array[i][j] = element_xy
        (h6, xedge6, yedge6) = np.histogram2d(Ini_x2, Ini_y2, bins=bins, range=[[-100, 100], [-100, 100]])
        xpos6, ypos6 = np.meshgrid(xedge6[:-1], yedge6[:-1], indexing="ij")
        xpos6 = xpos6.ravel()
        ypos6 = ypos6.ravel()
        vpos6 = 0
        dx6 = xedge6[1] - xedge6[0]
        dy6 = yedge6[1] - yedge6[0]
        dv6 = xy1_2d_effi_array.ravel()

        cmap6 = cm.get_cmap('plasma')
        norm6 = colors.Normalize(vmin=min(dv6), vmax=max(dv6))
        colors6 = cmap6(norm6(dv6))

        ax6.bar3d(xpos6, ypos6, vpos6, dx6, dy6, dv6, zsort='average', color=colors6)
        sc6 = cm.ScalarMappable(cmap=cmap6, norm=norm6)
        sc6.set_array([])
        ax6.set_zlim(0,0.1)
        plt.colorbar(sc6, pad =colorbar_pos)

        ax6.set_title('(f) Efficiency_middle')
        ax6.set_xlabel('x/mm')
        ax6.set_ylabel('y/mm')

        ax7 = fig.add_subplot(3, 3, 9, projection='3d')

        xy2_2d_effi_array = np.zeros((bins, bins))

        for i in range(bins):
            for j in range(bins):
                if h1[i][j] != 0:
                    element_xy = h4[i][j] / h1[i][j]
                else:
                    element_xy = 0

                if element_xy >abnormal_cut:
                    element_xy = abnormal_cut
                    # print(i, j)
                xy2_2d_effi_array[i][j] = element_xy
        (h7, xedge7, yedge7) = np.histogram2d(Ini_x2, Ini_y2, bins=bins, range=[[-100, 100], [-100, 100]])
        xpos7, ypos7 = np.meshgrid(xedge7[:-1], yedge7[:-1], indexing="ij")
        xpos7 = xpos7.ravel()
        ypos7 = ypos7.ravel()
        vpos7 = 0
        dx7 = xedge7[1] - xedge7[0]
        dy7 = yedge7[1] - yedge7[0]
        dv7 = xy2_2d_effi_array.ravel()

        cmap7 = cm.get_cmap('plasma')
        norm7 = colors.Normalize(vmin=min(dv7), vmax=max(dv7))
        colors7 = cmap7(norm7(dv7))

        ax7.bar3d(xpos7, ypos7, vpos7, dx7, dy7, dv7, zsort='average', color=colors7)
        sc7 = cm.ScalarMappable(cmap=cmap7, norm=norm7)
        sc7.set_array([])
        plt.colorbar(sc7, pad =colorbar_pos)

        ax7.set_title('(i) Efficiency_bottom')
        ax7.set_xlabel('x/mm')
        ax7.set_ylabel('y/mm')
        ax7.set_zlim(0,0.1)

        ax8 = fig.add_subplot(3, 3, 3, projection='3d')

        xy3_2d_effi_array = np.zeros((bins, bins))

        for i in range(bins):
            for j in range(bins):
                if h2[i][j] != 0:
                    element_xy = h5[i][j] / h2[i][j]
                else:
                    element_xy = 0
                if element_xy >abnormal_cut:
                    element_xy =abnormal_cut
                xy3_2d_effi_array[i][j] = element_xy
        (h8, xedge8, yedge8) = np.histogram2d(Ini_x2, Ini_y2, bins=bins, range=[[-100, 100], [-100, 100]])
        xpos8, ypos8 = np.meshgrid(xedge8[:-1], yedge8[:-1], indexing="ij")
        xpos8 = xpos8.ravel()
        ypos8 = ypos8.ravel()
        vpos8 = 0
        dx8 = xedge8[1] - xedge8[0]
        dy8 = yedge8[1] - yedge8[0]
        dv8 = xy3_2d_effi_array.ravel()

        cmap8 = cm.get_cmap('plasma')
        norm8 = colors.Normalize(vmin=min(dv8), vmax=max(dv8))
        colors8 = cmap8(norm8(dv8))

        ax8.bar3d(xpos8, ypos8, vpos8, dx8, dy8, dv8, zsort='average', color=colors8)
        sc8 = cm.ScalarMappable(cmap=cmap8, norm=norm8)
        sc8.set_array([])
        plt.colorbar(sc8, pad =colorbar_pos)

        ax8.set_title('(c) Efficiency_top')
        ax8.set_xlabel('x/mm')
        ax8.set_ylabel('y/mm')
        ax8.set_zlim(0,0.1)
        plt.show()

    def plot_hist_rslice(self, read=False):
        bins = 20
        colorbar_pos = .10
        abnormal_cut= 0.1
        z_lim_ini =3000
        z_lim_fin = 200
        half_bin = int(bins / 2)
        print(self.outputfile)
        if read:
            df = pd.read_csv(self.outputfile)
            # df = pd.read_csv(self.outputfile, nrows=10000)
            # df = pd.read_csv(self.outputfile, nrows=2000)
        else:
            print("You have to first run read_information() function before plot_cross if read = False. Otherwise might cause error!")
        # df['y'] < 25) & (df['y'] > -25)
        Ini_x1 = df[(df['z'] < 500) & (df['z'] > 480)]['x'].to_list()
        Ini_y1 = df[(df['z'] < 500) & (df['z'] > 480)]['y'].to_list()
        Ini_x2 = df[(df['z'] < 400) & (df['z'] > 380)]['x'].to_list()
        Ini_y2 = df[(df['z'] < 400) & (df['z'] > 380)]['y'].to_list()
        Ini_x3 = df[(df['z'] < 620) & (df['z'] > 600)]['x'].to_list()
        Ini_y3 = df[(df['z'] < 620) & (df['z'] > 600)]['y'].to_list()


        Fin_x1 = df[(df['z'] < 500) & (df['z'] > 480) & (df['Hit'] == True)]['x'].to_list()
        Fin_y1 = df[(df['z'] < 500) & (df['z'] > 480) & (df['Hit'] == True)]['y'].to_list()
        Fin_x2 = df[(df['z'] < 400) & (df['z'] > 380) & (df['Hit'] == True)]['x'].to_list()
        Fin_y2 = df[(df['z'] < 400) & (df['z'] > 380) & (df['Hit'] == True)]['y'].to_list()
        Fin_x3 = df[(df['z'] < 620) & (df['z'] > 600) & (df['Hit'] == True)]['x'].to_list()
        Fin_y3 = df[(df['z'] < 620) & (df['z'] > 600) & (df['Hit'] == True)]['y'].to_list()


        # fig, axs = plt.subplots(2, 3, figsize=(9, 3))

        fig = plt.figure()
        # ax0 = fig.add_subplot(3,3,4,projection ='3d')
        (h0, xedge0, yedge0) = np.histogram2d(Ini_x1, Ini_y1, bins=bins, range=[[-100,100],[-100,100]])
        # print(h0)
        # xpos0, ypos0 = np.meshgrid(xedge0[:-1],yedge0[:-1], indexing = "ij")
        # xpos0 = xpos0.ravel()
        # ypos0 = ypos0.ravel()
        # vpos0 = 0
        # dx0 = xedge0[1]-xedge0[0]
        # dy0 = yedge0[1]-yedge0[0]
        # dv0 = h0.ravel()
        #
        # cmap0 = cm.get_cmap('plasma')
        # norm0 = colors.Normalize(vmin=min(dv0), vmax= max(dv0))
        # colors0=cmap0(norm0(dv0))
        #
        # ax0.bar3d(xpos0, ypos0, vpos0, dx0, dy0, dv0, zsort='average', color=colors0)
        # sc0 = cm.ScalarMappable(cmap=cmap0, norm=norm0)
        # sc0.set_array([])
        # plt.colorbar(sc0, pad =colorbar_pos)

        # ax0.azim = 300
        # ax0.elev = 30

        # ax0.bar3d(xpos0, vpos0, ypos0, dx0, dw0, dy0, zsort='average')

        # ax0.set_title('(d) Ini_Distribution_xy_middle')
        # ax0.set_xlabel('x/mm')
        # ax0.set_ylabel('y/mm')
        # ax0.set_zlim(0,z_lim_ini)
        #
        # ax1 = fig.add_subplot(3, 3, 7, projection='3d')

        (h1, xedge1, yedge1) = np.histogram2d(Ini_x2, Ini_y2, bins=bins, range=[[-100,100],[-100,100]])
        # xpos1, ypos1 = np.meshgrid(xedge1[:-1], yedge1[:-1], indexing="ij")
        # xpos1 = xpos1.ravel()
        # ypos1 = ypos1.ravel()
        # vpos1 = 0
        # dx1 = xedge1[1] - xedge1[0]
        # dy1 = yedge1[1] - yedge1[0]
        # dv1 = h1.ravel()
        #
        # cmap1 = cm.get_cmap('plasma')
        # norm1 = colors.Normalize(vmin=min(dv0), vmax=max(dv0))
        # colors1 = cmap1(norm1(dv1))
        #
        # ax1.bar3d(xpos1, ypos1, vpos1, dx1, dy1, dv1, zsort='average',color=colors1)
        # ax1.set_title('(g) Ini_Distribution_xy_bottom')
        # ax1.set_xlabel('x/mm')
        # ax1.set_ylabel('y/mm')
        # ax1.set_zlim(0,z_lim_ini)
        #
        # sc1 = cm.ScalarMappable(cmap=cmap1, norm=norm1)
        # sc1.set_array([])
        # plt.colorbar(sc1, pad =colorbar_pos)
        #
        # #xdege2 != xedge0 when sample number is not large enough!
        # ax2 = fig.add_subplot(3, 3, 1, projection='3d')
        (h2, xedge2, yedge2) = np.histogram2d(Ini_x3, Ini_y3, bins=bins,range=[[-100,100],[-100,100]])
        # xpos2, ypos2 = np.meshgrid(xedge2[:-1], yedge2[:-1], indexing="ij")
        # xpos2 = xpos2.ravel()
        # ypos2 = ypos2.ravel()
        # vpos2 = 0
        # dx2 = xedge2[1] - xedge2[0]
        # dy2 = yedge2[1] - yedge2[0]
        # dv2 = h2.ravel()
        #
        # cmap2 = cm.get_cmap('plasma')
        # norm2 = colors.Normalize(vmin=min(dv0), vmax=max(dv0))
        # colors2 = cmap2(norm2(dv2))
        #
        # ax2.bar3d(xpos2, ypos2, vpos2, dx2, dy2, dv2, zsort='average', color=colors2)
        # ax2.set_title('(a) Ini_Distribution_xy_top')
        # ax2.set_xlabel('x/mm')
        # ax2.set_ylabel('y/mm')
        # ax2.set_zlim(0,z_lim_ini)
        #
        # sc2 = cm.ScalarMappable(cmap=cmap2, norm=norm2)
        # sc2.set_array([])
        # plt.colorbar(sc2, pad =colorbar_pos)
        #
        # ax3 = fig.add_subplot(3, 3, 5, projection='3d')

        (h3, xedge3, yedge3) = np.histogram2d(Fin_x1, Fin_y1, bins=bins, range=[[-100, 100], [-100, 100]])
        # xpos3, ypos3 = np.meshgrid(xedge3[:-1], yedge3[:-1], indexing="ij")
        # xpos3 = xpos3.ravel()
        # ypos3 = ypos3.ravel()
        # vpos3 = 0
        # dx3 = xedge3[1] - xedge3[0]
        # dy3 = yedge3[1] - yedge3[0]
        # dv3 = h3.ravel()
        #
        # cmap3 = cm.get_cmap('plasma')
        # norm3 = colors.Normalize(vmin=min(dv3), vmax=max(dv3))
        # colors3 = cmap3(norm3(dv3))
        #
        # ax3.bar3d(xpos3, ypos3, vpos3, dx3, dy3, dv3, zsort='average', color=colors3)
        # sc3 = cm.ScalarMappable(cmap=cmap3, norm=norm3)
        # sc3.set_array([])
        # ax3.set_zlim(0,z_lim_fin)
        # plt.colorbar(sc3, pad =colorbar_pos)
        #
        #
        # ax3.set_title('(e) Fin_Distribution_xy_middle')
        # ax3.set_xlabel('x/mm')
        # ax3.set_ylabel('y/mm')
        #
        # ax4 = fig.add_subplot(3, 3, 8, projection='3d')
        (h4, xedge4, yedge4) = np.histogram2d(Fin_x2, Fin_y2, bins=bins, range=[[-100, 100], [-100, 100]])
        # xpos4, ypos4 = np.meshgrid(xedge4[:-1], yedge4[:-1], indexing="ij")
        # xpos4 = xpos4.ravel()
        # ypos4 = ypos4.ravel()
        # vpos4 = 0
        # dx4 = xedge4[1] - xedge4[0]
        # dy4 = yedge4[1] - yedge4[0]
        # dv4 = h4.ravel()
        #
        # cmap4 = cm.get_cmap('plasma')
        # norm4 = colors.Normalize(vmin=min(dv3), vmax=max(dv3))
        # colors4 = cmap4(norm4(dv4))
        #
        # ax4.bar3d(xpos4, ypos4, vpos4, dx4, dy4, dv4, zsort='average', color=colors4)
        # sc4 = cm.ScalarMappable(cmap=cmap4, norm=norm4)
        # sc4.set_array([])
        # ax4.set_zlim(0,z_lim_fin)
        # plt.colorbar(sc4, pad =colorbar_pos)
        #
        # ax4.set_title('(h) Fin_Distribution_xy_bottom')
        # ax4.set_xlabel('x/mm')
        # ax4.set_ylabel('y/mm')
        #
        # ax5 = fig.add_subplot(3, 3, 2, projection='3d')
        (h5, xedge5, yedge5) = np.histogram2d(Fin_x3, Fin_y3, bins=bins, range=[[-100, 100], [-100, 100]])
        # print(xedge5, yedge5)
        # xpos5, ypos5 = np.meshgrid(xedge5[:-1], yedge5[:-1], indexing="ij")
        # xpos5 = xpos5.ravel()
        # ypos5 = ypos5.ravel()
        # vpos5 = 0
        # dx5 = xedge5[1] - xedge5[0]
        # dy5 = yedge5[1] - yedge5[0]
        # dv5 = h5.ravel()
        #
        # cmap5 = cm.get_cmap('plasma')
        # norm5 = colors.Normalize(vmin=min(dv3), vmax=max(dv3))
        # colors5 = cmap5(norm5(dv5))

        # ax5.bar3d(xpos5, ypos5, vpos5, dx5, dy5, dv5, zsort='average', color=colors5)
        # sc5 = cm.ScalarMappable(cmap=cmap5, norm=norm5)
        # sc5.set_array([])
        # ax5.set_zlim(0,z_lim_fin)
        # plt.colorbar(sc5, pad =colorbar_pos)
        #
        # ax5.set_title('(b) Fin_Distribution_xy_top')
        # ax5.set_xlabel('x/mm')
        # ax5.set_ylabel('y/mm')
        #
        #

        # ax6 = fig.add_subplot(3, 3, 6, projection='3d')

        xy1_2d_effi_array = np.zeros((bins, bins))

        for i in range(bins):
            for j in range(bins):
                if h0[i][j] != 0:
                    element_xy = h3[i][j] / h0[i][j]
                else:
                    element_xy = 0
                if element_xy >abnormal_cut:
                    element_xy = abnormal_cut
                xy1_2d_effi_array[i][j] = element_xy
        (h6, xedge6, yedge6) = np.histogram2d(Ini_x2, Ini_y2, bins=bins, range=[[-100, 100], [-100, 100]])
        r_eff_middle0 = xy1_2d_effi_array[half_bin]
        r_eff_middle1 = []
        for i in range(bins):
            r_eff_middle1.append(xy1_2d_effi_array[i,half_bin])
        # r_eff_middle_45 = []
        # for i in range(bins):
        #     r_eff_middle_45.append(xy1_2d_effi_array[i,i])
        # r_eff_middle_135 = []
        # for i in range(bins):
        #     r_eff_middle_135.append(xy1_2d_effi_array[i, bins-1-i])
        print("0",r_eff_middle0)
        print("1",r_eff_middle1)
        # print("45",r_eff_middle_45)
        # print("135",r_eff_middle_135)

        r_eff_middle =[]
        for i in range(bins):
            r_eff_middle.append((r_eff_middle0[i]+r_eff_middle1[i])/2)


        # xpos6, ypos6 = np.meshgrid(xedge6[:-1], yedge6[:-1], indexing="ij")
        # xpos6 = xpos6.ravel()
        # ypos6 = ypos6.ravel()
        # vpos6 = 0
        # dx6 = xedge6[1] - xedge6[0]
        # dy6 = yedge6[1] - yedge6[0]
        # dv6 = xy1_2d_effi_array.ravel()
        #
        # cmap6 = cm.get_cmap('plasma')
        # norm6 = colors.Normalize(vmin=min(dv6), vmax=max(dv6))
        # colors6 = cmap6(norm6(dv6))
        #
        # ax6.bar3d(xpos6, ypos6, vpos6, dx6, dy6, dv6, zsort='average', color=colors6)
        # sc6 = cm.ScalarMappable(cmap=cmap6, norm=norm6)
        # sc6.set_array([])
        # ax6.set_zlim(0,0.1)
        # plt.colorbar(sc6, pad =colorbar_pos)
        #
        # ax6.set_title('(f) Efficiency_middle')
        # ax6.set_xlabel('x/mm')
        # ax6.set_ylabel('y/mm')
        #
        # ax7 = fig.add_subplot(3, 3, 9, projection='3d')

        xy2_2d_effi_array = np.zeros((bins, bins))

        for i in range(bins):
            for j in range(bins):
                if h1[i][j] != 0:
                    element_xy = h4[i][j] / h1[i][j]
                else:
                    element_xy = 0

                if element_xy >abnormal_cut:
                    element_xy = abnormal_cut
                    # print(i, j)
                xy2_2d_effi_array[i][j] = element_xy
        (h7, xedge7, yedge7) = np.histogram2d(Ini_x2, Ini_y2, bins=bins, range=[[-100, 100], [-100, 100]])
        r_eff_bottom0 = xy2_2d_effi_array[half_bin]
        r_eff_bottom1 = []
        for i in range(bins):
            r_eff_bottom1.append(xy1_2d_effi_array[i, half_bin])
        r_eff_bottom = []
        for i in range(bins):
            r_eff_bottom.append((r_eff_bottom0[i] + r_eff_bottom1[i]) / 2)

        # xpos7, ypos7 = np.meshgrid(xedge7[:-1], yedge7[:-1], indexing="ij")
        # xpos7 = xpos7.ravel()
        # ypos7 = ypos7.ravel()
        # vpos7 = 0
        # dx7 = xedge7[1] - xedge7[0]
        # dy7 = yedge7[1] - yedge7[0]
        # dv7 = xy2_2d_effi_array.ravel()
        #
        # cmap7 = cm.get_cmap('plasma')
        # norm7 = colors.Normalize(vmin=min(dv7), vmax=max(dv7))
        # colors7 = cmap7(norm7(dv7))
        #
        # ax7.bar3d(xpos7, ypos7, vpos7, dx7, dy7, dv7, zsort='average', color=colors7)
        # sc7 = cm.ScalarMappable(cmap=cmap7, norm=norm7)
        # sc7.set_array([])
        # plt.colorbar(sc7, pad =colorbar_pos)
        #
        # ax7.set_title('(i) Efficiency_bottom')
        # ax7.set_xlabel('x/mm')
        # ax7.set_ylabel('y/mm')
        # ax7.set_zlim(0,0.1)
        #
        # ax8 = fig.add_subplot(3, 3, 3, projection='3d')

        xy3_2d_effi_array = np.zeros((bins, bins))

        for i in range(bins):
            for j in range(bins):
                if h2[i][j] != 0:
                    element_xy = h5[i][j] / h2[i][j]
                else:
                    element_xy = 0
                if element_xy >abnormal_cut:
                    element_xy =abnormal_cut
                xy3_2d_effi_array[i][j] = element_xy
        (h8, xedge8, yedge8) = np.histogram2d(Ini_x2, Ini_y2, bins=bins, range=[[-100, 100], [-100, 100]])
        r_eff_top0 = xy3_2d_effi_array[half_bin]
        r_eff_top1 = []
        for i in range(bins):
            r_eff_top1.append(xy1_2d_effi_array[i, half_bin])
        r_eff_top = []
        for i in range(bins):
            r_eff_top.append((r_eff_top0[i] + r_eff_top1[i]) / 2)
        # xpos8, ypos8 = np.meshgrid(xedge8[:-1], yedge8[:-1], indexing="ij")
        # xpos8 = xpos8.ravel()
        # ypos8 = ypos8.ravel()
        # vpos8 = 0
        # dx8 = xedge8[1] - xedge8[0]
        # dy8 = yedge8[1] - yedge8[0]
        # dv8 = xy3_2d_effi_array.ravel()
        #
        # cmap8 = cm.get_cmap('plasma')
        # norm8 = colors.Normalize(vmin=min(dv8), vmax=max(dv8))
        # colors8 = cmap8(norm8(dv8))
        #
        # ax8.bar3d(xpos8, ypos8, vpos8, dx8, dy8, dv8, zsort='average', color=colors8)
        # sc8 = cm.ScalarMappable(cmap=cmap8, norm=norm8)
        # sc8.set_array([])
        # plt.colorbar(sc8, pad =colorbar_pos)
        #
        # ax8.set_title('(c) Efficiency_top')
        # ax8.set_xlabel('x/mm')
        # ax8.set_ylabel('y/mm')
        # ax8.set_zlim(0,0.1)

        ax= fig.add_subplot()
        ax.plot(xedge0[:-1],r_eff_top,color = "blue", label="top")
        ax.plot(xedge0[:-1],r_eff_middle,color = "red", label="middle")
        ax.plot(xedge0[:-1], r_eff_bottom, color="green", label="bottom")
        ax.set_xlabel("x axis/mm")
        ax.set_ylabel("Efficiency/bin")
        ax.set_ylim(0,0.1)
        plt.legend()



        plt.show()





if __name__=="__main__":
    # get hits number and plot positions
    tnc = photon_efficiency_measurement()
    # tnc.read_Information()
    # tnc.plot_hist(True)
    tnc.PCE_count(read=True)
    # tnc.plot_hist_y0plane(True)
    # tnc.plot_hist_rzplane(read= True)
    # tnc.plot_hist_nonrzplane(read= True)
    # tnc.plot_hist_zplane(read=True)
    # tnc.plot_hist_rslice(read=True)