import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import scipy.integrate as itg
import math
size=30
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

matplotlib.rc('font', **font)
C = 2.99*10**8
PI = 3.1415
H = 6.626*10**(-34)
E = 1.602*10**(-19)
Pi = 3.1415

# Density (ρ) at -196 °C (solid)	1.943 g.cm-3
# Density (ρ) at -183 °C	1.89 g.cm-3
# Density (ρ) at -127.8 °C (liquid)	1.603 g.cm-3
# Density (ρ) at -80 °C (gas)	1.317 kg.m-3
# Density (ρ) at 15 °C (gas)	3.72 kg.m-3
# Density (ρ) at 21 °C (gas)	3.858 kg.m-3

H_bar = 1.054* 10**(-34)
E_charge = 1.602*10**(-19)
A_0 = 5.291*10**(-11)
M_e = 9.109*10**(-31)
Av = 6.023*10**23
CF_MASS = 88
N_density = 3.72*Av*10**(3)/(CF_MASS)
# N_density = 1.89*10**6*Av/CF_MASS
# k = Pi**2*H_bar**3/(M_e**2*A_0)*(diff_sigma_value/E_charge)*((N_desity)/frequency)
# k = sigma*c*h_bar*N_density/E

class k_plot():
    def __init__(self):
        self.A = 0.124523
        # self.o0 = (2.611*10**(-4)*10**4*2*PI*C)**(1/2)
        self.o0 = 2 * PI * C / (61.88 * 10 ** (-9))
        self.o1 = 2 * PI * C / (140.47 * 10 ** (-9))
        self.Q = (2 * PI * C) ** 2 * self.A * 10 ** (-6)
        self.wave = [643.99, 587.7, 546.23, 508.72, 480.12, 435.95, 280.28, 244.08, 206.82, 182.20, 167.15, 152.47, 150.93, 140.47]
        print('0', self.o0, 1, self.o1)
        self.N = 1
        self.a = []
        self.b = []
        self.c = []
        self.funa = []
        self.funb = []
        self.func = []
        self.k = []

        self.o = []
        for i in self.wave:
            self.o.append(2 * PI * C / (i * 10 ** (-9)))

        self.energy = []
        for i in self.o:
            self.energy.append(i * H / (2 * PI * E))
        print("energy", self.energy)

        for i in self.o:
            self.a.append(self.o0 / (2 * (self.o0 - i)))
            self.b.append(self.o0 / (2 * (self.o0 + i)))
            self.c.append(-i ** 2 / (self.o0 ** 2 - i ** 2))
            # self.funa.append(np.log(-(self.o1 - self.o0) / self.o0))
            # self.funb.append(np.log((self.o1 + self.o0) / self.o0))
            # self.func.append(np.log((self.o1 - i) / i))
             # integrate includes negative parts
            self.funa.append(np.log(self.N * (self.o0 - self.o1) / self.o0))
            self.funb.append(np.log((self.N * (self.o0 - self.o1) + self.o1 + self.o0) / self.o0))
            self.func.append(np.log((self.N * (self.o0 - self.o1) + self.o0 + self.o1 - i) / i))

            #integrate to

        print('a', self.a)
        print('b',self.b)
        print('c',self.c)
        print('funa', self.funa)
        print('funb', self.funb)
        print('funb', self.func)

        for i in range(len(self.o)):
            self.k.append(-self.Q * (self.funa[i] * self.a[i] + self.b[i] * self.funb[i] + self.c[i] * self.func[i]) / PI)

            # self.a = self.o0/(2*(self.o0-o))
            # self.b = self.o0 / (2 * (self.o0 + o))
            # self.c = -o**2/(self.o0**2-o**2)
            # self.funa = np.log(self.N*(self.o0-self.o1)/self.o0)
            # self.funb = np.log((self.N*(self.o0-self.o1)+self.o1 + self.o0)/self.o0)
            # self.func = np.log((self.N*(self.o0-self.o1)+self.o1-o)/o)
            # self.k=-self.Q*(self.funa*self.a+self.b*self.funb+self.c*self.func)/PI


    def plot_k(self):
        fig = plt.figure()
        print(self.k)
        ax = fig.add_subplot()
        ax.plot(self.energy,self.k)
        plt.show()




class k2_plot():
    def __init__(self):
        self.wave_ex=[643.99, 587.7, 546.23, 508.72, 480.12, 435.95, 280.28, 244.08, 206.82, 182.20, 167.15, 152.47, 150.93, 140.47]
        self.n_ex = []
        for i in self.wave_ex:
            self.n_ex.append(0.124523*10**(-6)/(2.61154*10**(-4)-i**(-2)))
        print(self.n_ex)
        self.energy = [ 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0,12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0,
                       16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0, 24.5, 25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0, 29.5, 30.0,
                       31.0,  32.0,  33.0,  34.0,  35.0,  36.0,  37.0,  38.0,  39.0,  40.0,  41.0,  42.0,  43.0,  44.0,  45.0,  46.0,  47.0,  48.0,  49.0,  50.0,  55.0, 60.0, 65.0, 70.0,
                       75.0, 80.0,  85.0,  86.0,  87.0,  88.0,  89.0,
                       90.0,  91.0,  92.0,  93.0,  94.0,  95.0,  96.0,  97.0,  98.0,  99.0,
                       100.0, 110.0,  120.0,130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0, 200.,  210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 380, 390]

        # self.diff_strength = [ 0, 0.91, 2.38 , 10.50, 22.25, 21.38, 13.83, 14.58, 23.92, 26.28, 27.95, 29.99, 32.89, 35.57, 36.69, 39.64, 40.89, 42.11, 45.70, 48.61, 50.61, 52.36, 52.27, 51.39, 49.15,
        #                       18.17, 46.91, 45.11, 42.37, 40.83, 40.19,39.57,39.02,39.03,38.71,38.91,38.95,38.91,38.78,38.59,39.42,39.79,39.55,39.42,38.76,39.39,39.21,38.99,38.65,37.08,35.24,33.38,
        #                       31.37,30.01,29.05,27.99,27.07,26.37,23.92,22.45,19.83, 18.09, 16.39, 15.02, 13.71, 13.23, 13.28, 12.73, 12.58, 12.56, 12.02, 11.76, 11.57, 11.55, 11.27, 11.08, 10.89, 10.73,
        #                        10.59, 10.39, 8.93, 7.63, 6.53, 5.63, 4.88, 4.39, 3.64, 3.12, 3.18, 2.61 , 0.02454300312462909, 0.022285050881348207, 0.020317926193681647, 0.018594869920703472, 0.017077969047513818,
        #                        0.01573625911369157, 0.014544276309394415, 0.013480943846999152, 0.012528708755720267, 0.011672867742475855, 0.010901036892542182, 0.010202731622834083, 0.009569031757387542,
        #                        0.008992312783148342, 0.008466028905748808, 0.007984536911596667, 0.0075429523748064935, 0.007137031653988118, 0.006763074568968942]
        # print(len(self.energy))
        # print(len(self.diff_strength))
        # print(len(self.energy)==len(self.diff_strength))
        self.high_energy = []
        self.high_strength = []
        for i in range(200,400,10):
            self.high_energy.append(i)
            self.high_strength.append(18.439*np.power(i,-1.5)+1.46525*1e4*np.power(i,-2.5)-5.9640*1e5*(np.power(i,-3.5)))
        self.diff_sigma = [ 0.07583333333333334, 0.15166666666666667, 0.2275, 0.30333333333333334, 0.37916666666666665, 0.455, 0.5308333333333334, 0.6066666666666667, 0.6825, 0.7583333333333333, 0.8341666666666666, 0.91, 2.38 , 10.50, 22.25, 21.38, 13.83, 14.58, 23.92, 26.28, 27.95, 29.99, 32.89, 35.57, 36.69, 39.64, 40.89, 42.11, 45.70, 48.61, 50.61, 52.36, 52.27, 51.39, 49.15,
                              18.17, 46.91, 45.11, 42.37, 40.83, 40.19,39.57,39.02,39.03,38.71,38.91,38.95,38.91,38.78,38.59,39.42,39.79,39.55,39.42,38.76,39.39,39.21,38.99,38.65,37.08,35.24,33.38,
                              31.37,30.01,29.05,27.99,27.07,26.37,23.92,22.45,19.83, 18.09, 16.39, 15.02, 13.71, 13.23, 13.28, 12.73, 12.58, 12.56, 12.02, 11.76, 11.57, 11.55, 11.27, 11.08, 10.89, 10.73,
                               10.59, 10.39, 8.93, 7.63, 6.53, 5.63, 4.88, 4.39, 3.64, 3.12, 3.18, 2.61 , 0.02454300312462909, 0.022285050881348207, 0.020317926193681647, 0.018594869920703472, 0.017077969047513818,
                               0.01573625911369157, 0.014544276309394415, 0.013480943846999152, 0.012528708755720267, 0.011672867742475855, 0.010901036892542182, 0.010202731622834083, 0.009569031757387542,
                               0.008992312783148342, 0.008466028905748808, 0.007984536911596667, 0.0075429523748064935, 0.007137031653988118, 0.006763074568968942]
        # df/dE = k*E, k =0.91/12= 0.0758
        # df/dE = exp(E/E0)-1, E0 = 18.54
        self.diff_sigma_exp = [0.055,0.113,0.1755,0.2407,0.3094,0.3820,0.4586,0.5394,0.6247,0.7147,0.80973, 0.91, 2.38 , 10.50, 22.25, 21.38, 13.83, 14.58, 23.92, 26.28, 27.95, 29.99, 32.89, 35.57, 36.69, 39.64, 40.89, 42.11, 45.70, 48.61, 50.61, 52.36, 52.27, 51.39, 49.15,
                              18.17, 46.91, 45.11, 42.37, 40.83, 40.19,39.57,39.02,39.03,38.71,38.91,38.95,38.91,38.78,38.59,39.42,39.79,39.55,39.42,38.76,39.39,39.21,38.99,38.65,37.08,35.24,33.38,
                              31.37,30.01,29.05,27.99,27.07,26.37,23.92,22.45,19.83, 18.09, 16.39, 15.02, 13.71, 13.23, 13.28, 12.73, 12.58, 12.56, 12.02, 11.76, 11.57, 11.55, 11.27, 11.08, 10.89, 10.73,
                               10.59, 10.39, 8.93, 7.63, 6.53, 5.63, 4.88, 4.39, 3.64, 3.12, 3.18, 2.61 , 0.02454300312462909, 0.022285050881348207, 0.020317926193681647, 0.018594869920703472, 0.017077969047513818,
                               0.01573625911369157, 0.014544276309394415, 0.013480943846999152, 0.012528708755720267, 0.011672867742475855, 0.010901036892542182, 0.010202731622834083, 0.009569031757387542,
                               0.008992312783148342, 0.008466028905748808, 0.007984536911596667, 0.0075429523748064935, 0.007137031653988118, 0.006763074568968942]
        self.diff_sigma_assume = [0.055*10**(-8), 0.113*10**(-8), 0.1755*10**(-8), 0.2407*10**(-8), 0.3094*10**(-8), 0.3820*10**(-8), 0.4586*10**(-8), 0.5394*10**(-8), 0.6247*10**(-8), 0.9*10**(-8), 10**(-7), 0.91, 2.38, 10.50, 22.25, 21.38, 13.83, 14.58, 23.92, 26.28, 27.95, 29.99, 32.89,
                               35.57, 36.69, 39.64, 40.89, 42.11, 45.70, 48.61, 50.61, 52.36, 52.27, 51.39, 49.15,
                               18.17, 46.91, 45.11, 42.37, 40.83, 40.19, 39.57, 39.02, 39.03, 38.71, 38.91, 38.95, 38.91, 38.78, 38.59, 39.42, 39.79, 39.55, 39.42, 38.76, 39.39, 39.21, 38.99, 38.65,
                               37.08, 35.24, 33.38,
                               31.37, 30.01, 29.05, 27.99, 27.07, 26.37, 23.92, 22.45, 19.83, 18.09, 16.39, 15.02, 13.71, 13.23, 13.28, 12.73, 12.58, 12.56, 12.02, 11.76, 11.57, 11.55, 11.27, 11.08,
                               10.89, 10.73,
                               10.59, 10.39, 8.93, 7.63, 6.53, 5.63, 4.88, 4.39, 3.64, 3.12, 3.18, 2.61, 0.02454300312462909, 0.022285050881348207, 0.020317926193681647, 0.018594869920703472,
                               0.017077969047513818,
                               0.01573625911369157, 0.014544276309394415, 0.013480943846999152, 0.012528708755720267, 0.011672867742475855, 0.010901036892542182, 0.010202731622834083,
                               0.009569031757387542,
                               0.008992312783148342, 0.008466028905748808, 0.007984536911596667, 0.0075429523748064935, 0.007137031653988118, 0.006763074568968942]
        self.diff_sigma_assume_5 = [0.055 * 10 ** (-5), 0.113 * 10 ** (-5), 0.1755 * 10 ** (-5), 0.2407 * 10 ** (-5), 0.3094 * 10 ** (-5), 0.3820 * 10 ** (-5), 0.4586 * 10 ** (-5), 0.5394 * 10 ** (-5),
                                  0.6247 * 10 ** (-5), 0.9 * 10 ** (-5), 10 ** (-4), 0.91, 2.38, 10.50, 22.25, 21.38, 13.83, 14.58, 23.92, 26.28, 27.95, 29.99, 32.89,
                                  35.57, 36.69, 39.64, 40.89, 42.11, 45.70, 48.61, 50.61, 52.36, 52.27, 51.39, 49.15,
                                  18.17, 46.91, 45.11, 42.37, 40.83, 40.19, 39.57, 39.02, 39.03, 38.71, 38.91, 38.95, 38.91, 38.78, 38.59, 39.42, 39.79, 39.55, 39.42, 38.76, 39.39, 39.21, 38.99,
                                  38.65,
                                  37.08, 35.24, 33.38,
                                  31.37, 30.01, 29.05, 27.99, 27.07, 26.37, 23.92, 22.45, 19.83, 18.09, 16.39, 15.02, 13.71, 13.23, 13.28, 12.73, 12.58, 12.56, 12.02, 11.76, 11.57, 11.55, 11.27,
                                  11.08,
                                  10.89, 10.73,
                                  10.59, 10.39, 8.93, 7.63, 6.53, 5.63, 4.88, 4.39, 3.64, 3.12, 3.18, 2.61, 0.02454300312462909, 0.022285050881348207, 0.020317926193681647, 0.018594869920703472,
                                  0.017077969047513818,
                                  0.01573625911369157, 0.014544276309394415, 0.013480943846999152, 0.012528708755720267, 0.011672867742475855, 0.010901036892542182, 0.010202731622834083,
                                  0.009569031757387542,
                                  0.008992312783148342, 0.008466028905748808, 0.007984536911596667, 0.0075429523748064935, 0.007137031653988118, 0.006763074568968942]
        self.diff_sigma_assume_3 = [0.055 * 10 ** (-3), 0.113 * 10 ** (-3), 0.1755 * 10 ** (-3), 0.2407 * 10 ** (-3), 0.3094 * 10 ** (-3), 0.3820 * 10 ** (-3), 0.4586 * 10 ** (-3),
                                    0.5394 * 10 ** (-3),
                                    0.6247 * 10 ** (-3), 0.9 * 10 ** (-3), 10 ** (-2), 0.91, 2.38, 10.50, 22.25, 21.38, 13.83, 14.58, 23.92, 26.28, 27.95, 29.99, 32.89,
                                    35.57, 36.69, 39.64, 40.89, 42.11, 45.70, 48.61, 50.61, 52.36, 52.27, 51.39, 49.15,
                                    18.17, 46.91, 45.11, 42.37, 40.83, 40.19, 39.57, 39.02, 39.03, 38.71, 38.91, 38.95, 38.91, 38.78, 38.59, 39.42, 39.79, 39.55, 39.42, 38.76, 39.39, 39.21, 38.99,
                                    38.65,
                                    37.08, 35.24, 33.38,
                                    31.37, 30.01, 29.05, 27.99, 27.07, 26.37, 23.92, 22.45, 19.83, 18.09, 16.39, 15.02, 13.71, 13.23, 13.28, 12.73, 12.58, 12.56, 12.02, 11.76, 11.57, 11.55, 11.27,
                                    11.08,
                                    10.89, 10.73,
                                    10.59, 10.39, 8.93, 7.63, 6.53, 5.63, 4.88, 4.39, 3.64, 3.12, 3.18, 2.61, 0.02454300312462909, 0.022285050881348207, 0.020317926193681647, 0.018594869920703472,
                                    0.017077969047513818,
                                    0.01573625911369157, 0.014544276309394415, 0.013480943846999152, 0.012528708755720267, 0.011672867742475855, 0.010901036892542182, 0.010202731622834083,
                                    0.009569031757387542,
                                    0.008992312783148342, 0.008466028905748808, 0.007984536911596667, 0.0075429523748064935, 0.007137031653988118, 0.006763074568968942]
        self.wave = []
        self.frequency = []
        self.trans_frequency = []

        self.transformed_wave = []
        self.n = []
        self.n_assume=[]
        self.n_exp = []
        self.n_fst = []
        self.k = []
        self.k_assume =[]
        self.k_assume_5 = []
        self.k_assume_3 = []
        self.k_exp = []
        self.KN=[]
        self.integral_buffer = 0

    def energy_into_frequency(self):
        for i in self.energy:
            self.wave.append(C*H_bar*2*Pi/(i*E_charge))

        for i in self.wave:
            self.frequency.append(C / i)
            self.KN.append(2*PI/(i*100))
        print("KN",self.KN)
        for i in range(len(self.frequency)):
            try:
                # try different transfered frequency
                # weight=0.03
                weight = 0.5
                self.trans_frequency.append(self.frequency[i]*weight  + (1-weight)*self.frequency[i + 1] )
            except:
                continue
        for i in self.trans_frequency:
            self.transformed_wave.append(C / i)
        # for i in range(len(self.trans_frequency)):
        for i in range(len(self.frequency)):
            #add a factor of 2 in the denomenator
            self.k.append((Pi * H_bar ** 3) *(self.diff_sigma[i] *10**(-2)/ E_charge)*(N_density)/ ((M_e ** 2 * A_0) * ( 2*self.frequency[i])))
            # self.k.append((Pi * H_bar ** 3) * (self.diff_sigma_exp[i] * 10 ** (-2) / E_charge) * (N_density) / ((M_e ** 2 * A_0) * (self.frequency[i])))
            # self.k.append(1.0975*self.diff_sigma[i]*10**(-28)*10**(6)*N_density*C/(4*Pi*self.frequency[i]))
            # self.k.append(1.0975 * self.diff_sigma_assume[i] * 10 ** (-28) * 10 ** (6) * N_density * C / (4 * Pi * self.frequency[i]))
        for i in range(len(self.frequency)):
            #add a factor of 2 in the denomenator
            self.k_assume.append((Pi * H_bar ** 3) *(self.diff_sigma_assume[i] *10**(-2)/ E_charge)*(N_density)/ ((M_e ** 2 * A_0) * ( 2*self.frequency[i])))

        for i in range(len(self.frequency)):
            #add a factor of 2 in the denomenator
            self.k_exp.append((Pi * H_bar ** 3) *(self.diff_sigma_exp[i] *10**(-2)/ E_charge)*(N_density)/ ((M_e ** 2 * A_0) * ( 2*self.frequency[i])))

        for i in range(len(self.frequency)):
            #add a factor of 2 in the denomenator
            self.k_assume_5.append((Pi * H_bar ** 3) *(self.diff_sigma_assume_5[i] *10**(-2)/ E_charge)*(N_density)/ ((M_e ** 2 * A_0) * ( 2*self.frequency[i])))

        for i in range(len(self.frequency)):
            #add a factor of 2 in the denomenator
            self.k_assume_3.append((Pi * H_bar ** 3) *(self.diff_sigma_assume_3[i] *10**(-2)/ E_charge)*(N_density)/ ((M_e ** 2 * A_0) * ( 2*self.frequency[i])))


        self.reverse_wave = self.wave
        print("wave",self.wave)

        # self.reverse_wave.reverse()
        # print("reverse", self.reverse_wave)
        # self.reverse_wave_nm = [10**9*x for x in self.wave]
        # self.reverse_wave_nm = [10 ** 9 * x for x in self.reverse_wave]
        self.reverse_wave_nm = [10 ** 9 * x for x in self.wave]
        print("nm",self.reverse_wave_nm)
        print("k",self.k)
        # for j in range(len(self.diff_sigma)):
        #     if self.energy[j] in [12,20,30,40,50,60,70,80,90,100]:
        #         print(j)
        #         print("lambda",self.wave[j]*10**(9))
        #         print("Diff",self.diff_sigma[j])
    def Cauchy_integral(self):
        print(len(self.frequency))
        for i in range(len(self.trans_frequency)):
            # # manually calculate the integral
            for j in range(len(self.frequency)-2):
                # print(j)
                bin = self.frequency[j + 1] - self.frequency[j]
                self.integral_buffer = self.integral_buffer + bin * (self.k[j] + self.k[j + 1]) / (2 * (self.frequency[j] - self.trans_frequency[i]))
            self.n_fst.append(self.integral_buffer/Pi)
            self.integral_buffer = 0
            # using scipy to calculate cauchy integral
            cauchy_function = []
            # print("k",len(self.k))
            # print("frequency",len(self.frequency))
            # print("trans_fre",len(self.trans_frequency))
            for f in range(len(self.frequency)):
                # print(self.frequency[118])
                # print(j)
                cauchy_function.append(self.k[f]/(PI*(self.frequency[f]-self.trans_frequency[i])))

            cauchy_integral = itg.simps(cauchy_function,self.frequency)

            # print(cauchy_integral)
            self.n.append(cauchy_integral)

            cauchy_function_assume = []
            for l in range(len(self.frequency)):
                # print(self.frequency[118])
                # print(j)
                cauchy_function_assume.append(self.k_assume[l]/(PI*(self.frequency[l]-self.trans_frequency[i])))

            cauchy_integral_assume = itg.simps(cauchy_function_assume,self.frequency)

            # print(cauchy_integral_assume)
            self.n_assume.append(cauchy_integral_assume)

            cauchy_function_exp = []
            for m in range(len(self.frequency)):
                # print(self.frequency[118])
                # print(j)
                cauchy_function_exp.append(self.k[m]/(PI*(self.frequency[m]-self.trans_frequency[i])))

            cauchy_integral_exp = itg.simps(cauchy_function_exp,self.frequency)

            # print(cauchy_integral)
            self.n_exp.append(cauchy_integral_exp)


    def plot_k(self):
        fig = plt.figure()
        # print(self.high_energy)
        # print(self.high_strength)
        ax = fig.add_subplot()

        # ax.plot(self.energy,self.k)
        # ax.set_xlabel("energy/ev", fontsize=size)
        # ax.set_xlim(0,100)
        # ax.set_ylim(10**(-5),10**(-3))
        # ax.set_yscale('log')
        # ax.set_ylabel("complex part of refractive index k", fontsize=size)

        ax.plot(self.reverse_wave_nm, self.k)
        ax.set_xlabel("wavelenth/nm", fontsize=size)
        ax.set_xlim(0, 700)
        ax.set_ylim(10 ** (-5), 10 ** (-3))
        ax.set_yscale('log')
        ax.set_ylabel("complex part of refractive index k", fontsize=size)


        # ax.set_title("Unmoodified density")
        # ax.plot(self.high_energy, self.high_strength)
        plt.show()

    def plot_n(self):
        fig = plt.figure()
        # print(self.high_energy)
        # print(self.high_strength)
        ax = fig.add_subplot()
        # ax.plot(self.energy[:-1], self.n)
        print("n",self.n)
        n_divided2=[]
        for i in self.n:
            n_divided2.append(i*2)
        # ax.plot(self.KN[:-1], self.n, color="blue", label="Theoretical based on KK")

        # ax.plot(self.reverse_wave_nm[:-1], self.n, color="blue", label="Theoretical based on KK")
        # ax.plot(self.reverse_wave_nm[:-1], self.n_exp, color="green", label="Theoretical based on KK with exponential extrapolation")
        # ax.plot(self.reverse_wave_nm[:-1], self.n_assume, color="orange", label="Theoretical based on KK with step extrapolation")

        ax.plot(self.reverse_wave_nm[:-1], self.n_fst, color="green", label="Theoretical based on KK")
        ax.plot(self.reverse_wave_nm[:-1], n_divided2, color="blue", label="Theoretical based on KK but doubled")
        ax.plot(self.wave_ex,self.n_ex,color="red",label="Experimental")


        ax.legend()
        # ax.set_yscale('log')
        ax.set_xlim(0,700)
        ax.set_xlabel("wavelength/nm", fontsize=size)
        ax.set_ylabel("refractive index (n-1)", fontsize=size)
        ax.set_title("Refractive Index vs Wavelength", fontsize=size)

        # ax.plot(self.wave[:-1], self.n)
        # ax.plot(self.energy[:-1], self.k)
        #might be inverse

        # ax.plot(self.high_energy, self.high_strength)
        plt.show()
    def interpolate(self):
        initial=[0,0.91]
        points = 12
        final=[]
        for i in range(points):
            final.append(initial[0]+(initial[1]-initial[0])*i/points)
        # print(final)

    def calulate_ABSL(self,idx=6):
        # print(self.wave)
        L=self.wave[idx]/(4*Pi*self.k_assume[idx])
        L_5= self.wave[idx] / (4 * Pi * self.k_assume_5[idx])
        L_3 = self.wave[idx] / (4 * Pi * self.k_assume_3[idx])
        print("ABSL",L)
        print("ABSL_5", L_5)
        print("ABSL_3", L_3)
    def integrate_test(self):
        x=[0,1,2,3]
        y=[1,1,1,1]
        print(itg.simps(y,x))
    def plot_extrapo(self):
        fig = plt.figure()
        ax = fig.add_subplot()

        initial=20
        ax.plot(self.energy[:initial], self.k[:initial], color="blue", label="linear extrapolation")
        ax.plot(self.energy[:initial], self.k_exp[:initial], color="green", label="exponetial extrapolation")
        ax.plot(self.energy[:initial], self.k_assume[:initial], color="orange", label="step extrapolation ABSL = 77km")
        ax.plot(self.energy[:initial], self.k_assume_5[:initial], color="red", label="exponetial extrapolation ABSL = 78 m")
        ax.plot(self.energy[:initial], self.k_assume_3[:initial], color="maroon", label="step extrapolation ABSL = 78 cm")

        ax.legend()
        ax.set_yscale('log')
        ax.set_ylim(10**(-8),10**(-3))
        ax.set_xlabel("energy/eV",fontsize=size )
        ax.set_ylabel("extrapolation value k", fontsize=size)
        ax.set_title("extraplolated k vs energy", fontsize=size)


        plt.show()
    def plot_function(self):
        fig = plt.figure()
        ax = fig.add_subplot()

        initial=12
        ax.plot(self.energy[:initial], self.diff_sigma[:initial], color="blue", label="linear extrapolation")
        ax.plot(self.energy[:initial], self.diff_sigma_exp[:initial], color="green", label="exponetial extrapolation")
        ax.plot(self.energy[:initial], self.diff_sigma_assume[:initial], color="orange", label="step extrapolation ABSL = 77km")
        ax.plot(self.energy[:initial], self.diff_sigma_assume_5[:initial], color="red", label="exponetial extrapolation ABSL = 78 m")
        ax.plot(self.energy[:initial], self.diff_sigma_assume_3[:initial], color="maroon", label="step extrapolation ABSL = 78 cm")

        ax.legend()
        ax.set_yscale('log')
        # ax.set_ylim(10**(-8),10**(-3))
        ax.set_xlabel("energy/eV",fontsize=size )
        ax.set_ylabel("df/dE  in 1E-2 1/eV", fontsize=size)
        ax.set_title("differential oscillator strength df/dE vs energy", fontsize=size)


        plt.show()
    def plot_in_Knumber(self):
        fig = plt.figure()

        ax = fig.add_subplot()


        ax.plot(self.KN, self.k, color="blue", label="Theoretical Calculation based on KK")
        # ax.plot(self.KN[:-1], self.n, color="blue", label="Theoretical Calculation based on KK")
        lowlimit = min(self.KN[:-1])
        uplimit = max(self.KN[:-1])
        ax.set_xlim(uplimit,lowlimit)

        ax.legend()
        ax.set_xlabel("wave number/ cm^(-1)", fontsize=size)
        ax.set_ylabel("refractive index k", fontsize=size)
        ax.set_title("Refractive Index k vs Wave number", fontsize=size)
        # ax.set_title("Refractive Index n vs Wave number", fontsize=size)

        # ax.plot(self.wave[:-1], self.n)
        # ax.plot(self.energy[:-1], self.k)
        #might be inverse

        # ax.plot(self.high_energy, self.high_strength)
        plt.show()
       #
if __name__ == '__main__':
    KP= k2_plot()
    # KP.integrate_test()
    KP.energy_into_frequency()
    KP.Cauchy_integral()
    KP.plot_n()
    KP.plot_k()
    KP.calulate_ABSL(6)
    # KP.interpolate()
    KP.plot_extrapo()
    KP.plot_function()
    KP.plot_in_Knumber()