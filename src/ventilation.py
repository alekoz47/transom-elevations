
import os
import csv
import re
import math
import numpy as np

def get_ventilation(data_path):
    """Find average ventilation factor for given run"""
    
    # test for T1 hull
    if data_path.find("T1") > 0:
        static_draft = 0.029
    else:
        static_draft = 0.052
    
    with open(data_path, 'r') as data:
        data_reader = csv.reader(data, delimiter=',')
        steady_data = list(data_reader)[400:1100]
    steady_data = [map(float, row) for row in steady_data]
    
    # test for steady run
    if data_path.find("A1VS") > 0:
        elevations = map(get_elevation_averages_steady, steady_data)
    else:
        elevations = map(get_elevation_averages_unsteady, steady_data)
        
    ventilations = [draft_from_elevation(el, static_draft) for el in elevations]
    return ventilations

def get_elevation_averages_steady(steady_data):
    """Find average ventilation factor for steady runs"""
    steady_data = list(steady_data)
    average_ventilations = np.quantile(steady_data, 0.5)
    
    return [average_ventilations, 0]
    
def get_elevation_averages_unsteady(steady_data):
    """Find min and max ventilation factors for unsteady runs"""
    steady_data = list(steady_data)
    min_ventilations = np.quantile(steady_data, 0.33)
    max_ventilations = np.quantile(steady_data, 0.67)
    
    return [min_ventilations, max_ventilations]

def vf_from_elevation(elevation, static_draft):
    draft = static_draft + elevation
    ventilation = vf(static_draft, draft)
    return ventilation

def draft_from_elevation(elevation, static_draft):
    return elevation + static_draft

def vf(static_draft, draft):
    return (static_draft - draft) / static_draft



get_ventilation("../data/2016-06-29_T5/TR5-R1.94A1V.csv")
"""
# scan all T5 runs
for filename in os.listdir("../data/2016-06-29_T5"):
    if filename != "Thumbs.db":
        data_path = "../data/2016-06-29_T5/" + filename
        speed_match = re.search('-R(.*)A1V', filename)
        speed = float(speed_match.group(1)) / 3.28084 # convert ft/s to m/s
        fn = speed / math.sqrt(9.81 * 0.052)
        ventilations = get_ventilation(data_path)
        print(data_path)
        with open("../data/ventilation/2016-06-29_T5.csv", 'a', newline='') as data:
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
"""
