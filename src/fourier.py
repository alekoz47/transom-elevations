
from scipy.fft import fft, ifft
import csv
import numpy as np
import matplotlib.pyplot as plt

def get_elevations(data_path, buttock):
    """Find elevations for given run at given buttock"""
    
    with open(data_path, 'r') as data:
        data_reader = csv.reader(data, delimiter=',')
        steady_data = list(data_reader)[700:990]
    steady_data = [map(float, row) for row in steady_data]
    steady_data = [list(row) for row in steady_data]
    
    elevations = [row[buttock] for row in steady_data]
    return elevations



elevations = get_elevations("../data/2016-06-29_T5/TR5-R2.47A1V.csv", 3)
x = np.array(elevations)
y = fft(x)

y = list(y)[1:] # remove starting signal at 0hz
#incident_min = min(y, key=lambda z: np.real(z))
#incident_max = max(y, key=lambda z: np.real(z))
incident_min = min(y, key=np.real)
incident_max = max(y, key=np.real)
incident_min_index = y.index(incident_min)
incident_max_index = y.index(incident_max)
print("Values:")
print(incident_min)
print(incident_max)
print("Indices:")
print(incident_min_index)
print(incident_max_index)
y = np.array(y)

y0 = y.copy()
y0[incident_min_index:incident_max_index + 1] = 0
x0 = ifft(y0)

plt.subplot(221),plt.plot(x),plt.ylim(-0.02,0.01),plt.xlim(0,300)
plt.subplot(222),plt.plot(x0),plt.ylim(-0.02,0.01),plt.xlim(0,300)
plt.subplot(223),plt.plot(y),plt.ylim(-0.5,0.5),plt.xlim(0,60)
plt.subplot(224),plt.plot(y0),plt.ylim(-0.5,0.5),plt.xlim(0,60)
plt.show()
