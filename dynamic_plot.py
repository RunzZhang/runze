import random
from itertools import count
import time
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits import mplot3d
import numpy as np
import os, pickle
import sys
import pandas as pd
plt.style.use('fivethirtyeight')
x_values = []
y_values = []
z_values = []
q_values = []
counter = 0
index = count()
def animate(i):
    #print(counter)
    x = next(index) # counter or x variable -> index
    counter = next(index)
    print(counter)
    x_values.append(x)
    '''
    Three random value series ->
    Y : 0-5
    Z : 3-8
    Q : 0-10
    '''
    y = random.randint(0, 5)
    z = random.randint(3, 8)
    q = random.randint(0, 10)
    # append values to keep graph dynamic
    # this can be replaced with reading values from a csv files also
    # or reading values from a pandas dataframe
    y_values.append(y)
    z_values.append(z)
    q_values.append(q)
    if counter >40:
        '''
        This helps in keeping the graph fresh and refreshes values after every 40 timesteps
        '''
        x_values.pop(0)
        y_values.pop(0)
        z_values.pop(0)
        q_values.pop(0)
        #counter = 0
        plt.cla() # clears the values of the graph
    plt.plot(x_values, y_values,linestyle='--')
    plt.plot(x_values, z_values,linestyle='--')
    plt.plot(x_values, q_values,linestyle='--')
    ax.legend(["Value 1 ","Value 2","Value 3"])
    ax.set_xlabel("X values")
    ax.set_ylabel("Values for Three different variable")
    plt.title('Dynamic line graphs')
    time.sleep(.25) # keep refresh rate of 0.25 seconds
#fig, ax = plt.subplots(dpi=120)
#area = pd.DataFrame(np.random.rand(10, 4), columns=['a', 'b', 'c', 'd'])
#area.plot(kind='area',ax=ax)
#plt.title('Demo graph for Area plot')
#plt.show()
print('matplotlib: {}'.format(matplotlib.__version__))
fig, ax = plt.subplots()
ani = FuncAnimation(plt.gcf(), animate, 1000)
plt.tight_layout()
plt.show()
'''
fig = plt.figure()
ax = plt.axes(projection='3d')
ani = FuncAnimation(plt.gcf(), animate, 10)
plt.tight_layout()
plt.show()'''