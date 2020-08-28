
import os
import csv
import re
import math
import numpy as np

def get_ventilation(data_path):
    """Find average ventilation factor for given run"""
    
    # set static draft by hull type
    if data_path.find("T1") > 0:
        static_draft = 0.029
    elif data_path.find("T4") > 0:
        static_draft = 0.052
    else: # assume this is T5
        static_draft = 0.052
    
    # read from elevations data files
    with open(data_path, 'r') as data:
        data_reader = csv.reader(data, delimiter=',')
        steady_data = list(data_reader)[700:1100]
    
    # convert raw elevation data to happy format
    steady_data = [map(float, row) for row in steady_data]
    
    # find average elevation at each of 7 buttocks
    sum_elevations = [0 for i in range(7)]
    for row in steady_data:
        sum_elevations = map(sum, zip(sum_elevations, row))
    elevations = [elevation / len(steady_data) for elevation in sum_elevations]
    
    # convert elevations to ventilations using static draft
    drafts = [static_draft + elevation for elevation in elevations]
    ventilations = [(static_draft - draft) / static_draft for draft in drafts]
    
    # TODO: read FFT amplitudes from ../data/fft/______.csv
    #   output [elevation - amptitude / 2, elevation + amplitude / 2] for unsteady
    #   output [elevation, elevation] for steady???
    # 
    
    # # test for steady run
    # if data_path.find("A1VS") > 0:
    #     elevations = map(get_elevation_averages_steady, steady_data)
    # else:
    #     elevations = map(get_elevation_averages_unsteady, steady_data)
        
    return ventilations



if __name__ == "__main__":
    # scan all T5 runs
    for filename in os.listdir("../data/2016-06-29_T5"):
        if filename != "Thumbs.db":
            data_path = "../data/2016-06-29_T5/" + filename
            # number in filename is model speed in ft/s
            speed_match = re.search('-R(.*)A1V', filename)
            speed = float(speed_match.group(1)) / 3.28084 # convert ft/s to m/s
            # we convert to transom FN here to help comparison
            fn = speed / math.sqrt(9.81 * 0.052)
            ventilations = get_ventilation(data_path)
            print(data_path)
            with open("../data/ventilation/2016-06-29_T5.csv", 'a', newline='') as data:
                write = csv.writer(data)
                row = [fn] + ventilations
                write.writerows([row])
            print("Data %s analysis complete." % filename)
            
    # scan all T4 runs
    for filename in os.listdir("../data/2016-03-11, T4"):
        if filename != "Thumbs.db":
            data_path = "../data/2016-03-11, T4/" + filename
            speed_match = re.search('-R(.*)[AD]1', filename)
            speed = float(speed_match.group(1)) / 3.28084 # convert ft/s to m/s
            fn = speed / math.sqrt(9.81 * 0.052)
            ventilations = get_ventilation(data_path)
            print(data_path)
            with open("../data/ventilation/2016-03-11, T4.csv", 'a', newline='') as data:
                write = csv.writer(data)
                row = [fn] + ventilations
                write.writerows([row])
            print("Data %s analysis complete." % filename)
            
    # scan all T1 runs
    for filename in os.listdir("../data/2016-06-27_T1"):
        if filename != "Thumbs.db":
            data_path = "../data/2016-06-27_T1/" + filename
            speed_match = re.search('-R(.*)A1V', filename)
            speed = float(speed_match.group(1)) / 3.28084 # convert ft/s to m/s
            fn = speed / math.sqrt(9.81 * 0.029)
            ventilations = get_ventilation(data_path)
            print(data_path)
            with open("../data/ventilation/2016-06-27_T1.csv", 'a', newline='') as data:
                write = csv.writer(data)
                row = [fn] + ventilations
                write.writerows([row])
            print("Data %s analysis complete." % filename)
    
