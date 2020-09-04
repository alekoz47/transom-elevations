
from scipy.fft import fft, ifft
import csv
import numpy as np
import os
import re
import math
# import matplotlib.pyplot as plt

def get_elevations_from_data(data_path, buttock):
    """Find elevations for given run at given buttock"""
    
    # read from elevation data files
    with open(data_path, 'r') as data:
        data_reader = csv.reader(data, delimiter=',')
        steady_data = list(data_reader)[700:1100]
    
    # convert raw elevation data to happy format
    steady_data = [map(float, row) for row in steady_data]
    steady_data = [list(row) for row in steady_data]
    elevations = [row[buttock] for row in steady_data]
    return elevations

def get_incident_data(elevations):
    """Find amplitude and frequency given elevations time history
    - Returns frequency in frames rather than Hz for now"""
    # TODO: convert frequency to Hz based on video metadata
    #   currently outputs in terms of frames
    
    # perform fast fourier transform on elevations time history
    x = np.array(elevations)
    y = fft(x)
    y = list(map(abs, y)) # fft outputs complex, so we find norm(y) here
    
    incident_max = max(y[1:60]) # remove 0hz and other high frequencies
    incident_max_index = y.index(incident_max)
    y = np.array(y)
    
    # perform inverse fast fourier transform without primary signal
    y0 = y.copy() # copy because Python variables are pointers
    # "zeroing out" could cause issues, essentially like noise-cancelling headphones,
    #   introduces inverted signal which could resurface
    y0[incident_max_index] = 0 # zero out primary signal
    x0 = ifft(y0)
    x0 = list(map(abs, x0))
    
    amp = incident_max
    freq = incident_max_index
    return amp, freq


if __name__ == "__main__":
    # # this code prints out plots of elevations time histories and fourier transforms
    # #     in the following format:
    # #
    # # (Elevations History)       (Elevations History with dominant signal removed)
    # # (Fourier Transform)       (Fourier Transform with dominant signal removed)
    # 
    # elevations = get_elevations("../data/2016-06-29_T5/TR5-R3.00A1V.csv", 3)
    # x = np.array(elevations)
    # y = fft(x)
    # y = list(map(abs, y))
    # incident_max = max(y[1:60]) # remove starting signal at 0hz
    # incident_max_index = y.index(incident_max)
    # y = np.array(y)
    # y0 = y.copy()
    # y0[incident_max_index] = 0
    # x0 = ifft(y0)
    # x0 = list(map(abs, x0))
    # plt.subplot(221),plt.plot(x),plt.ylim(-0.04,0.01),plt.xlim(0,300)
    # plt.subplot(222),plt.plot(x0),plt.ylim(-0.04,0.01),plt.xlim(0,300)
    # plt.subplot(223),plt.plot(y),plt.ylim(0,1),plt.xlim(0,60)
    # plt.subplot(224),plt.plot(y0),plt.ylim(0,1),plt.xlim(0,60)
    # plt.show()
    
    # scan all T5 runs
    # this is derivative of the file-traversing code in ventilation.py
    for filename in os.listdir("../data/2016-06-29_T5"):
        if filename != "Thumbs.db":
            data_path = "../data/2016-06-29_T5/" + filename
            speed_match = re.search('-R(.*)A1V', filename)
            speed = float(speed_match.group(1)) / 3.28084 # convert ft/s to m/s
            fn = speed / math.sqrt(9.81 * 0.052)
            elevations = get_elevations_from_data(data_path, 3)
            amp, freq = get_incident_data(elevations)
            print(data_path)
            with open("../data/fft/2016-06-29_T5.csv", 'a', newline='') as data:
                write = csv.writer(data)
                row = [fn] + [amp] + [freq]
                write.writerows([row])
            print("Data %s analysis complete." % filename)
    
    # scan all T4 runs
    for filename in os.listdir("../data/2016-03-11, T4"):
        if filename != "Thumbs.db":
            data_path = "../data/2016-03-11, T4/" + filename
            print(data_path)
            speed_match = re.search('-R(.*)[AD]1', filename)
            speed = float(speed_match.group(1)) / 3.28084 # convert ft/s to m/s
            fn = speed / math.sqrt(9.81 * 0.052)
            elevations = get_elevations_from_data(data_path, 3)
            amp, freq = get_incident_data(elevations)
            print(data_path)
            with open("../data/fft/2016-03-11, T4.csv", 'a', newline='') as data:
                write = csv.writer(data)
                row = [fn] + [amp] + [freq]
                write.writerows([row])
            print("Data %s analysis complete." % filename)
            
    # scan all T1 runs
    for filename in os.listdir("../data/2016-06-27_T1"):
        if filename != "Thumbs.db":
            data_path = "../data/2016-06-27_T1/" + filename
            speed_match = re.search('-R(.*)A1V', filename)
            speed = float(speed_match.group(1)) / 3.28084 # convert ft/s to m/s
            fn = speed / math.sqrt(9.81 * 0.052)
            elevations = get_elevations_from_data(data_path, 3)
            amp, freq = get_incident_data(elevations)
            print(data_path)
            with open("../data/fft/2016-06-27_T1.csv", 'a', newline='') as data:
                write = csv.writer(data)
                row = [fn] + [amp] + [freq]
                write.writerows([row])
            print("Data %s analysis complete." % filename)
