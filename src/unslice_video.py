
import cv2
import os
from os.path import isfile, join

path_in = "../images/testing/test0/"
path_out = "../videos/testing/video5.mp4"
fps = 60

frame_array = []
files = [f for f in os.listdir(path_in) if isfile(join(path_in, f))]

#sort file names properly
files.sort(key = lambda x: x[5:-4])

for i in range(len(files)):
    filename = path_in + files[i]
    img = cv2.imread(filename)
    h, w, layers = img.shape
    size = (w, h)
    frame_array.append(img)

out = cv2.VideoWriter(path_out,
                      cv2.VideoWriter_fourcc(*'DIVX'),
                      fps,
                      size)
for i in range(len(frame_array)):
    out.write(frame_array[i])
out.release()
