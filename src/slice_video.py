
import cv2

vidcap = cv2.VideoCapture("../videos/TR5-R1.94A1V.mp4")
success,image = vidcap.read()

fps = vidcap.get(cv2.CAP_PROP_FPS)
frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count / fps
rate = duration / 1500

print(rate * 1000)

count = 0
success = True
while success:
    if count % 100 == 0:
        print(count)
    vidcap.set(cv2.CAP_PROP_POS_MSEC, (count * rate * 1000))
    cv2.imwrite("../images/frame%d.jpg" % count, image)
    success,image = vidcap.read()
    count += 1
vidcap.release()
