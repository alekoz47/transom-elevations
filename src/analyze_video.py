
import cv2
import os
from process_loop import get_elevations

def slice_video(video_path):
    vidcap = cv2.VideoCapture(video_path)
    success,image = vidcap.read()
    
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    rate = duration / 1500
    
    count = 0
    success = True
    while success:
        print(count)
        vidcap.set(cv2.CAP_PROP_POS_MSEC, (count * rate * 1000))
        cv2.imwrite("../images/frame%d.jpg" % count, image)
        success,image = vidcap.read()
        count += 1
    vidcap.release()


for filename in os.listdir("../videos/2016-06-29_T5"):
    if filename != "Thumbs.db":
        video_path = "../videos/2016-06-29_T5/" + filename
        print(video_path)
        slice_video(video_path)
        data_path = video_path.replace("videos", "data")
        get_elevations(data_path)
