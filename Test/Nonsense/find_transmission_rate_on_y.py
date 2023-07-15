import numpy as np

def AbsL_cm(T):
    L=-0.2/np.log(T)
    return L

x_pixel = [129,1765]
y_pixel = [979, 60]
x_wavelength = [140,240]
y_percentage = [0, 100]
x_interval = [170.07,179.95,189.87]
y_pixel_interval_max = [154,148,144]
y_pixel_interval_raw = [186,152,146]


max_transmission = [89.771, 90.424, 90.860]
raw_transmission = [86.289, 89.989, 90.642]
true_transmission = []
ABSL = []
true_transmission_output = [0.9612124182642502, 0.995189330266301, 0.9976007043803654]
ABSL_output = [5.055630175068579, 41.47417250229005, 83.25775812883292]

if __name__ == "__main__":
    x_pixel_interval = []
    y_percentage_interval_max = []
    y_percentage_interval_raw = []
    for element in x_interval:
        x_pixel_interval.append(x_pixel[0]+(element-x_wavelength[0])*(x_pixel[1]-x_pixel[0])/(x_wavelength[1]-x_wavelength[0]))
    print('x_pixel_interval',x_pixel_interval)

    for element in y_pixel_interval_max:
        y_percentage_interval_max.append(y_percentage[0]+(element-y_pixel[0])*(y_percentage[1]-y_percentage[0])/(y_pixel[1]-y_pixel[0]))
    print('y_percentage_interval_max',y_percentage_interval_max)

    for element in y_pixel_interval_raw:
        y_percentage_interval_raw.append(y_percentage[0]+(element-y_pixel[0])*(y_percentage[1]-y_percentage[0])/(y_pixel[1]-y_pixel[0]))
    print('y_percentage_interval_raw',y_percentage_interval_raw)

    for i in range(0,3):
        true_transmission.append(raw_transmission[i]/max_transmission[i])

    for i in range(0,3):
        ABSL.append(AbsL_cm(true_transmission[i]))
    print('ABSL',ABSL)
    print('transmiision',true_transmission)
