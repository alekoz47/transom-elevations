
import cv2
import numpy as np

def find_mask(image_name):
    print(image_name)
    img = cv2.imread(image_name)
        
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
    transom_contour = best_cnt
    
    out = np.zeros_like(gray)
    out[mask == 255] = gray[mask == 255]
    
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
    
    out = np.zeros_like(gray)
    out[mask == 255] = gray[mask == 255]
    
    final = cv2.cvtColor(final, cv2.COLOR_BGR2RGB)
    
    cv2.drawContours(final, [transom_contour], 0, 0, 2)
    cv2.drawContours(final, [waterline_contour], 0, 0, 2)
    
    return final

for i in range(1500):
    mask = find_mask("../images/frame" + str(i) + ".jpg")
    cv2.imwrite("../images/testing/test0/frame" + str(i) + ".jpg", mask)