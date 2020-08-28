
import cv2
from elevations_utils import get_elevations

def slice_video(video_path):
    """ Slices any video into 1500 frames """
    # TODO: error handling in case 1500 frames not possible
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



if __name__ == "__main__":
    video_path = "../videos/2016-06-29_T5/TR5-R3.00A1V.mp4"
    slice_video(video_path)
    data_path = video_path.replace("videos", "data/testing").replace("mp4", "csv")
    get_elevations(data_path)
