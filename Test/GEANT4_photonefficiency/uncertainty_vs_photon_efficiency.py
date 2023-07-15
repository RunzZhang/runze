from sipm_matrix_plot import *
import matplotlib.pyplot as plt
import matplotlib
size=20
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : size}

def uncern_absl():
    absl = [2.02, 1.99, 1.49]
    absl90 = []
    absl95 = []
    absl100 = []
    absl105 = []
    absl110 = []
    for i in absl:
        absl90.append(i * 0.9)
        absl95.append(i * 0.95)
        absl100.append(i * 1)
        absl105.append(i * 1.05)
        absl110.append(i * 1.1)

    print('absl90', absl90)
    print('absl95', absl95)
    print('absl100', absl100)
    print('absl105', absl105)
    print('absl110', absl110)

def plot_absl_effi():

    # efficienty_absl = [1.853*1532 / 1742, 1.853*1698 / 1742,1.853* 1742 / 1742, 1.853*1775/1742, 1.853*1833/1742]
    # efficienty_absl = [3.736,3.746,3.803,3.816,3.815]
    # x=[0.90,0.95,1.00,1.05,1.10]
    # efficienty_absl = [3.375, 3.555, 3.580, 3.640, 3.709]
    efficienty_absl = [3.375, 3.555, 3.580, 3.640, 3.709]
    x = [0.5, 0.75, 1.00, 1.25, 1.5]
    fig = plt.figure()
    ax = fig.add_subplot()
    lenx = len(x)
    leny = len(efficienty_absl)

    print(lenx, leny)
    for i in range(lenx):
        ax.scatter(x[i], efficienty_absl[i], s=200, marker='o')
    ax.set_xlabel('Relative ABSL',fontsize = size)
    ax.set_ylabel('Photon Efficiency/%',fontsize = size)
    plt.xticks(fontsize=size)
    plt.yticks(fontsize=size)
    plt.show()


def plot_refle_effi():
    # reflectivity = [1.853*1532 / 1742, 1.853*1634 / 1742,1.853* 1742 / 1742, 1.853*1802/1742, 1.853*1812/1742]
    # reflectivity = [3.084,3.425,3.803,4.075,4.303]
    reflectivity = [3.04, 3.3, 3.579, 3.78, 3.95]
    x=[0.85,0.90,0.95,0.98,0.99]
    fig = plt.figure()

    ax = fig.add_subplot()
    lenx = len(x)
    leny = len(reflectivity)

    print(lenx, leny)
    for i in range(lenx):
        ax.scatter(x[i], reflectivity[i], s=200, marker='o')
    ax.set_xlabel('Reflectivity',fontsize = size)
    ax.set_ylabel('Photon Efficiency/%',fontsize = size)
    plt.xticks(fontsize=size)
    plt.yticks(fontsize=size)
    plt.show()

if __name__ == "__main__":
    plot_refle_effi()
    # plot_absl_effi()

