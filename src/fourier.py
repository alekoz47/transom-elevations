
from scipy.fft import fft, ifft
import csv
import numpy as np
import matplotlib.pyplot as plt

def get_elevations(data_path, buttock):
    """Find elevations for given run at given buttock"""
    
    with open(data_path, 'r') as data:
        data_reader = csv.reader(data, delimiter=',')
        steady_data = list(data_reader)[700:1050]
    steady_data = [map(float, row) for row in steady_data]
    steady_data = [list(row) for row in steady_data]
    
    elevations = [row[buttock] for row in steady_data]
    return elevations



elevations = get_elevations("../data/2016-06-27_T1/T1-R1.94A1V_1.csv", 3)
x = np.array(elevations)
y = fft(x)
y = list(map(abs, y))

incident_max = max(y[1:60]) # remove starting signal at 0hz
incident_max_index = y.index(incident_max)
y = np.array(y)

y0 = y.copy()
y0[incident_max_index] = 0
x0 = ifft(y0)
x0 = list(map(abs, x0))

plt.subplot(221),plt.plot(x),plt.ylim(-0.02,0.01),plt.xlim(0,400)
plt.subplot(222),plt.plot(x0),plt.ylim(-0.02,0.01),plt.xlim(0,400)
plt.subplot(223),plt.plot(y),plt.ylim(0,1),plt.xlim(0,60)
plt.subplot(224),plt.plot(y0),plt.ylim(0,1),plt.xlim(0,60)
plt.show()
