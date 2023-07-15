# some source: https://drive.google.com/drive/folders/1BS-knr-jMv1ntBGK46O6mbwc_Llwx8tb
import matplotlib.pyplot as plt
import numpy as np

def transmission2m(wavelength_nm):
    a=90.5633
    b=1.6057*pow(10,23)
    t=-0.33382
    transmission2m =a / (1 + b*np.exp( t*wavelength_nm)) / 100
    return transmission2m

def AbsL_cm(T):
    L=-0.2/np.log(T)
    return L

def transmission_limit(wavelength_nm):
    a = 90.5633
    b = 1.6057 * pow(10, 23)
    t = -0.33382
    # transmission_limit = a*(1-b*np.exp(t*wavelength_nm))/100
    # transmission_limit = a*(1-b*np.exp(t*wavelength_nm)+np.exp(-0.047*wavelength_nm))/100
    transmission_limit = a*(1-np.exp(-0.0199*wavelength_nm))/100
    return transmission_limit



def guess():
    a = 90.5633
    b = 1.6057 * pow(10, 23)
    t = -0.33382
    B = np.log(85/a-1+b*np.exp(t*140))/(-140)
    C = np.log(1-0.85/0.905633)/(-140)
    print('set',C)
    return B



if __name__ == "__main__":
    T = []
    T_max= []
    ABS = []

    # wavelen_nm = [2058.2, 1800.0, 1600.0, 1529.6, 1300, 1000, 844.7, 766.5, 706.5, 627.8, 546.1, 508.6, 467.8, 410.2, 340.4, 303.4, 250.3, 193.6, 179.4272, 177.6278, 175.8641, 144.5]
    wavelen_nm=[170.07,179.95,189.87]
    for ele in wavelen_nm:
        T.append(transmission2m(ele))
        T_max.append(transmission_limit(ele))
        ABS.append(AbsL_cm(transmission2m(ele)))
    print("T", T)
    print("ABS", ABS)
    # plt.plot(wavelen_nm,T,'.')
    # plt.plot(wavelen_nm,ABS,'.')
    # plt.show()

    print("log", -1 / np.log(0.86))

    x = np.linspace(140, 240, 100)
    y = transmission2m(x)
    z = AbsL_cm(y)
    w = transmission_limit(x)
    plt.plot(x,y,'.')
    # plt.plot(x, z, '.')
    # plt.xlabel('Wavelength/nm')
    # plt.ylabel('ABSL/cm')

    plt.plot(x,w,'.')
    plt.xlabel('Wavelength/nm')
    plt.ylabel('Theoretical max Transmission/cm')
    plt.ylim(0,1)

    plt.grid()
    plt.show()

    print("guess", guess())


