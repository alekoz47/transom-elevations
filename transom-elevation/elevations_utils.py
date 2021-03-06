
import cv2
import numpy as np
import csv

def corrected_perspective(image):
    """Return image with corrected perspective"""
    # convert BGR to RGB
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # project image to vertical plane
    #   this is based on first frame of TR5-R1.94A1V
    #   camera position shouldn't change between runs
    # getPerspectiveTransform uses four points that *should* be a rectangle
    #   and four points that *make* a rectangle, to which the original points
    #   are mapped by warpPerspective
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
    return proj

def masked_image(proj_image, lower_range, upper_range):
    """Return image with specified color mask"""
    # hide everything but selected color
    # use hsv for easier matching of hues
    hsv = cv2.cvtColor(proj_image, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, lower_range, upper_range)
    return mask

def largest_contour(cropped_image):
    """Return contour with largest area from image"""
    # "blacks out" image behind mask, then finds boundaries of largest
    #   contour around the mask (sorted by internal contour area)
    gray = cropped_image
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)
    contours, hierarchy = cv2.findContours(thresh,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
    best_cnt = sorted(contours,
                      key=lambda c: cv2.contourArea(c),
                      reverse=True)[0]
    return best_cnt

def elevations(transom_contour, waterline_contour, data_path):
    """Return elevations from contours"""
    # we have waterline_contour and transom_contour
    #   find top left and right corners of transom
    #   split vessel into buttocks
    #   find most vertical waterline point at each buttock
    #   scale and find coordinates of waterline relative to transom
    
    # find boundaries of transom to define "box"
    transom_l = max(transom_contour,
                    key=lambda r: r[0][0])[0][0]
    transom_r = min(transom_contour,
                    key=lambda r: r[0][0])[0][0]
    transom_b = max(transom_contour,
                    key=lambda r: r[0][1])[0][1]
    transom_t = min(transom_contour,
                    key=lambda r: r[0][1])[0][1]
    
    # find top corners of transom by distance from top corners of "box"
    transom_tl = min(transom_contour,
                     key=lambda r: (r[0][0] - transom_l) ** 2 + (r[0][1] - transom_t) ** 2)[0]
    transom_tr = min(transom_contour,
                     key=lambda r: (r[0][0] - transom_r) ** 2 + (r[0][1] - transom_t) ** 2)[0]
    
    # find x coordinates of edges of waterline by distance from bottom corners of "box"
    waterline_l = min(waterline_contour,
                     key=lambda r: (r[0][0] - transom_l) ** 2 + (r[0][1] - transom_b) ** 2)[0][0]
    waterline_r = min(waterline_contour,
                     key=lambda r: (r[0][0] - transom_r) ** 2 + (r[0][1] - transom_b) ** 2)[0][0]
    
    # split vessel into buttocks
    # currently just splits space between edges of waterline into 6 equal portions
    waterline_span = waterline_r - waterline_l
    buttocks = []
    for b in range(7):
        buttocks.append(waterline_l + (b / 6) * waterline_span)

    # find raw wave heights at each buttock
    # this is difficult because contours aren't defined at every x coordinate
    #   so they are not necessarily defined at each buttock
    # to remedy this, we search the closest 40 points (by distance in x from buttock) 
    #   on the waterline coordinate, then find the closest two points
    #   (by distance in x and y from buttock and top of transom)
    #   and then interpolate between the two points to find the value of y
    #   at the buttock's x coordinate
    raw_wave_heights = []
    for x in buttocks:
        heights_search = sorted(waterline_contour, key=lambda r: abs(x - r[0][0]))[:40]
        sorted_heights = sorted(heights_search, key=lambda r: r[0][1] ** 2 + (r[0][0]-x) ** 2)
        heights_x = [sorted_heights[0][0][0], sorted_heights[1][0][0]]
        heights_y = [sorted_heights[0][0][1], sorted_heights[1][0][1]]
        height = np.interp(x, heights_x, heights_y)
        raw_wave_heights.append(height)
        
    # find scaled wave heights
    # currently experiencing issues, so we make corrections later
    # theoretically, this should work on its own
    scale = 0.23 / (transom_tr[0] - transom_tl[0]) # beam is 0.23 m
    transom_height = (transom_tr[1] + transom_tl[1]) / 2
    if data_path.find("T1") > 0 or data_path.find("T4") > 0:
        transom_to_waterline = 0.10 / scale # T1 or T4
    elif data_path.find("T5") > 0:
        transom_to_waterline = 0.09 / scale # T5
    unscaled_wave_heights = [h - (transom_height + transom_to_waterline) 
                             for h in raw_wave_heights]
    wave_heights = [-h * scale for h in unscaled_wave_heights]
    
    # make corrections for hulls
    if data_path.find("T1") > 0:
        wave_heights = [0.1 - (h / 2) for h in wave_heights]
    elif data_path.find("T4") > 0:
        wave_heights = [0.175 - h for h in wave_heights]
    else: # assume T5
        wave_heights = [0.1 - (h / 2) for h in wave_heights]
        
    return wave_heights

def test_mask(frame):
    """ Tests mask on singular frame """
    image_name = "../images/frame%d.jpg" % frame
    img = cv2.imread(image_name)
    
    # this is temporary
    # replace with whatever mask you need to test
    tsm_low = np.array([18,150,130])
    tsm_high = np.array([24,255,215])
    wtl_low = np.array([22,102,105])
    wtl_high = np.array([40,255,200])
    
    # standard steps for finding contours
    prj = corrected_perspective(img)
    tsm = masked_image(prj, tsm_low, tsm_high)
    transom = largest_contour(tsm)
    wtl = masked_image(prj, wtl_low, wtl_high)
    waterline = largest_contour(wtl)
    
    # draw contours on projected image
    cv2.drawContours(prj, [transom], 0, 0, 2)
    cv2.drawContours(prj, [waterline], 0, 0, 2)
    cv2.cvtColor(prj, cv2.COLOR_BGR2RGB)
    # output image for viewing
    cv2.imwrite("../images/testing/frame%dtest.jpg" % frame, prj)

def write_elevations(heights, data_path):
    """ Write elevations data to CSV file """
    with open(data_path,'a', newline='') as data:
        write = csv.writer(data)
        write.writerows([heights])

def get_elevations(data_path):
    """ Finds and writes elevations time history for each frame in ../images"""
    for frame in range(1500):
        image_name = "../images/frame%d.jpg" % frame
        img = cv2.imread(image_name)
        
        # switch for hull masks
        # TODO: T4 mask still needs work
        if data_path.find("T1") > 1:
            tsm_low = np.array([21,147,130])
            tsm_high = np.array([35,255,200])
            wtl_low = np.array([29,116,105])
            wtl_high = np.array([43,255,224])
        elif data_path.find("T4") > 1:
            tsm_low = np.array([18,150,130])
            tsm_high = np.array([24,255,215])
            wtl_low = np.array([22,102,105])
            wtl_high = np.array([40,255,200])
        elif data_path.find("T5") > 1:
            tsm_low = np.array([26,150,130])
            tsm_high = np.array([30,255,215])
            wtl_low = np.array([30,204,105])
            wtl_high = np.array([40,255,180])
        else: # catch any other hulls in filename
            tsm_low = np.array([26,150,130])
            tsm_high = np.array([30,255,215])
            wtl_low = np.array([30,204,105])
            wtl_high = np.array([40,255,224])
        
        # standard steps for finding contours
        prj = corrected_perspective(img)
        tsm = masked_image(prj, tsm_low, tsm_high)
        transom = largest_contour(tsm)
        wtl = masked_image(prj, wtl_low, wtl_high)
        waterline = largest_contour(wtl)
        
        heights = elevations(transom, waterline, data_path)
            
        write_elevations(heights, data_path)
    print("Video processing complete.")
        