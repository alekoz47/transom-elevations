
import cv2

vidcap = cv2.VideoCapture("../videos/TR5-R1.94A1V.mp4")
success,image = vidcap.read()
count = 0
success = True
while success:
    cv2.imwrite("../images/frame%d.jpg" % count, image)   #save frame #count as jpeg
    success,image = vidcap.read()
    print("Read a new frame: ", success)
    count += 1
vidcap.release()
