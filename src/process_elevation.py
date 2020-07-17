
import cv2
import numpy as np
import matplotlib.pyplot as plt

img = cv2.imread("../images/frame0.jpg")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#np.savetxt("test1.csv", img.split()[0], delimiter=',')

# project image to vertical plane
#   this is based on first frame of TR5-R1.94A1V
#   based on camera position, this shouldn't change between runs
initial_rect = np.float32([[732, 480],
                           [1151, 483],
                           [1144, 576],
                           [741, 572]])
final_rect = np.float32([[732, 480],
                         [1151, 480],
                         [1151, 576],
                         [732, 576]])
matrix = cv2.getPerspectiveTransform(initial_rect, final_rect)
proj = cv2.warpPerspective(img, matrix, (1920, 1080))


######## Recognize Stern ########


# hide everything but stern (based on yellow)
hsv = cv2.cvtColor(proj, cv2.COLOR_RGB2HSV)
lower_range = np.array([20,100,50])
upper_range = np.array([60,242,215])
mask = cv2.inRange(hsv, lower_range, upper_range)

# crop image to only include stern + wave
crop = mask[150:800, 500:1350]

gray = crop
final = proj[150:800, 500:1350]
blur = cv2.GaussianBlur(gray, (5,5), 0)
thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)

contours, hierarchy = cv2.findContours(thresh,
                                       cv2.RETR_TREE,
                                       cv2.CHAIN_APPROX_SIMPLE)
# TODO: replace this with sort function lambda: cv2.contourArea()
best_cnt = contours[0]
max_area = 0
c = 0
for i in contours:
    area = cv2.contourArea(i)
    if area > 1000:
        if area > max_area:
            max_area = area
            best_cnt = i
            image = cv2.drawContours(img, contours, c, (0, 255, 0), 3)
    c += 1

mask = np.zeros((gray.shape), np.uint8)
cv2.drawContours(mask, [best_cnt], 0, 255, -1)
cv2.drawContours(mask, [best_cnt], 0, 0, 2)
transom_contour = best_cnt # save for later


######## Recognize Waterline #########
# this section has a lot of reused code


# hide everything but waterline (based on green)
lower_range = np.array([29,225,115])
upper_range = np.array([60,255,255])
mask = cv2.inRange(hsv, lower_range, upper_range)

# crop image to only include stern + wave
crop = mask[150:800, 500:1350]

gray = crop
blur = cv2.GaussianBlur(gray, (5,5), 0)
thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)

contours, hierarchy = cv2.findContours(thresh,
                                       cv2.RETR_TREE,
                                       cv2.CHAIN_APPROX_SIMPLE)
best_cnt = contours[0]
max_area = 0
c = 0
for i in contours:
    area = cv2.contourArea(i)
    if area > 1000:
        if area > max_area:
            max_area = area
            best_cnt = i
            image = cv2.drawContours(img, contours, c, (0, 255, 0), 3)
    c += 1

mask = np.zeros((gray.shape), np.uint8)
cv2.drawContours(mask, [best_cnt], 0, 255, -1)
cv2.drawContours(mask, [best_cnt], 0, 0, 2)
waterline_contour = best_cnt

final = cv2.cvtColor(final, cv2.COLOR_BGR2RGB)
cv2.drawContours(final, [transom_contour], 0, 0, 2)
cv2.drawContours(final, [waterline_contour], 0, 0, 2)


######## Locate Coordinates ########


# we have waterline_contour and transom_contour
#   find top left and right corners of transom
#   split vessel into buttocks
#   find most vertical waterline point at each buttock
#   scale and find coordinates of waterline relative to transom

# find top corners of transom
tl_dist = sorted(transom_contour,
                 key=lambda r: r[0][0])[0][0]
tr_dist = sorted(transom_contour,
                 key=lambda r: r[0][0])[len(transom_contour) -1][0]
print(tl_dist)
print(tr_dist)

# split vessel into buttocks
# use lambda to make line between corners
