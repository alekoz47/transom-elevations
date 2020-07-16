
import cv2
import numpy as np
import matplotlib.pyplot as plt

#read image
img = cv2.imread("../images/frame0.jpg")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

lower_range = np.array([20,100,50])
upper_range = np.array([60,242,215])

mask = cv2.inRange(hsv, lower_range, upper_range)

# testing color filter with waves
"""
img1 = cv2.imread("../images/frame1000.jpg")
img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
hsv1 = cv2.cvtColor(img1, cv2.COLOR_RGB2HSV)
mask1 = cv2.inRange(hsv1, lower_range, upper_range)

cv2.imshow("mask", mask)
cv2.imshow("mask1", mask1)
if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows()
"""

plt.subplot(121),plt.imshow(mask)
plt.subplot(122),plt.imshow(edges)
plt.show()

cv2.imshow("edges", edges)
if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows()

"""
######## Find Corners #########

gray = np.float32(gray)
#result is dilated for marking corners
dst = cv2.cornerHarris(gray, 2, 3, 0.04)
#threshold for optimal value
img[dst > 0.01 * dst.max()] = [0, 0, 255]

cv2.imshow("dst", img)
if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows()

######## Transform Image #########

rows,cols,ch = img.shape

#original boundary points
pts1 = np.float32([[56,65],[368,52],[28,387],[389,390]])
#new boundary points (rectangle)
pts2 = np.float32([[0,0],[300,0],[0,300],[300,300]])

M = cv2.getPerspectiveTransform(pts1,pts2)

#300,300 is sizing of final image
dst = cv2.warpPerspective(img,M,(300,300))

plt.subplot(221),plt.imshow(img),plt.title("Input")
plt.subplot(222),plt.imshow(gray),plt.title("Grayscale")
plt.subplot(223),plt.imshow(dst),plt.title("Output")
plt.show()

if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows()

######## Recognize Grid ########

# "crop" image to outside border of transom stern

blur = cv2.GaussianBlur(gray, (5,5), 0)
thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)
    
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
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

# deal with the "cropped" image

out = np.zeros_like(gray)
out[mask == 255] = gray[mask == 255]

blur = cv2.GaussianBlur(out, (5,5), 0)
thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)

contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

c = 0
for i in contours:
        area = cv2.contourArea(i)
        if area > 1000/2:
            cv2.drawContours(image, contours, c, (0, 255, 0), 3)
        c+=1
    
plt.subplot(221),plt.imshow(thresh),plt.title("threshold")
plt.subplot(222),plt.imshow(mask),plt.title("mask")
plt.subplot(223),plt.imshow(image),plt.title("final")
plt.show()
"""