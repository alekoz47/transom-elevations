
import cv2
import numpy as np
import csv

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
    lower_range = np.array([26,150,130])
    upper_range = np.array([30,255,215])
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
    lower_range = np.array([29,204,105])
    upper_range = np.array([40,255,224])
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
    # TODO: check corner points with transom and wave
    
    # find top corners of transom
    transom_tl = sorted(transom_contour,
                     key=lambda r: r[0][0])[0][0]
    transom_tr = sorted(transom_contour,
                     key=lambda r: r[0][0])[len(transom_contour) -1][0]
    
    #find edges of waterline
    waterline_l = sorted(waterline_contour,
                     key=lambda r: r[0][0])[0][0][0]
    waterline_r = sorted(waterline_contour,
                     key=lambda r: r[0][0])[len(waterline_contour) -1][0][0]
    
    # split vessel into buttocks
    waterline_span = waterline_r - waterline_l
    buttocks = []
    for b in range(7):
        buttocks.append(waterline_l + (b / 6) * waterline_span)
    
    # find raw wave heights
    raw_wave_heights = []
    wave_contour_bounds = []
    for x in buttocks:
        wave_contour_bounds = sorted(waterline_contour,
                                     key=lambda r: abs(x - r[0][0]))[:5]
        raw_wave_heights.append(min(wave_contour_bounds,
                                    key=lambda r: r[0][1])[0][1])
    #wave_points = np.int32([np.int32([buttocks[i], raw_wave_heights[i]]) for i in range(7)])
    
    # find scaled wave heights
    # may replace this code if I get sizing of grid
    scale = 0.23 / (transom_tr[0] - transom_tl[0]) # beam is 0.23 m
    transom_height = (transom_tr[1] + transom_tl[1]) / 2
    transom_to_waterline = 0.09 / scale # top to design waterline is 0.09 m
    
    unscaled_wave_heights = [h - (transom_height + transom_to_waterline) 
                             for h in raw_wave_heights]
    wave_heights = [-h * scale for h in unscaled_wave_heights]
    
    with open("../data/test3.csv",'a') as data:
        write = csv.writer(data)
        write.writerows([wave_heights])
        
    return final

for i in range(1500):
    mask = find_mask("../images/frame" + str(i) + ".jpg")
    cv2.imwrite("../images/testing/test0/frame" + str(i) + ".jpg", mask)
