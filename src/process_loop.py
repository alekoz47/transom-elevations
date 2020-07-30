
import cv2
import numpy as np
import csv

def corrected_perspective(image):
    """Return image with corrected perspective"""
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # project image to vertical plane
    #   this is based on first frame of TR5-R1.94A1V
    #   camera position shouldn't change between runs
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
    crop = proj[150:800, 500:1450]
    return crop

def masked_image(proj_image, lower_range, upper_range):
    """Return image with specified color mask"""
    # hide everything but selected color
    hsv = cv2.cvtColor(proj_image, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, lower_range, upper_range)
    return mask

def largest_contour(cropped_image):
    """Return contour with largest area from image"""
    gray = cropped_image
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)
    contours, hierarchy = cv2.findContours(thresh,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
#    big_contours = filter(lambda c: cv2.contourArea(c) > 1000,
#                          contours)
    best_cnt = sorted(contours,
                      key=lambda c: cv2.contourArea(c),
                      reverse=True)[0]
    return best_cnt

def elevations(transom_contour, waterline_contour):
    """Return elevations from contours"""
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
    
    # find scaled wave heights
    # may replace this code if I get sizing of grid
    scale = 0.23 / (transom_tr[0] - transom_tl[0]) # beam is 0.23 m
    transom_height = (transom_tr[1] + transom_tl[1]) / 2
    transom_to_waterline = 0.09 / scale # top to design waterline is 0.09 m
    unscaled_wave_heights = [h - (transom_height + transom_to_waterline) 
                             for h in raw_wave_heights]
    wave_heights = [-h * scale for h in unscaled_wave_heights]
    return wave_heights

def apply_morphology(masked_image):
    # smooth the image with alternative closing and opening
    # with an enlarging kernel
    morph = masked_image.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    
    # take morphological gradient
    gradient_image = cv2.morphologyEx(morph, cv2.MORPH_GRADIENT, kernel)
    
    # split the gradient image into channels
    image_channels = np.split(np.asarray(gradient_image), 3, axis=2)
    channel_height, channel_width, _ = image_channels[0].shape
    
    # apply Otsu threshold to each channel
    for i in range(0, 3):
        _, image_channels[i] = cv2.threshold(~image_channels[i], 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
        image_channels[i] = np.reshape(image_channels[i], newshape=(channel_height, channel_width, 1))
    
    # merge the channels
    image_channels = np.concatenate((image_channels[0], image_channels[1], image_channels[2]), axis=2)
    return image_channels

def test_mask(frame):
    image_name = "../images/frame%d.jpg" % frame
    img = cv2.imread(image_name)
    
    prj = apply_morphology(corrected_perspective(img))
    cv2.imwrite("../images/testing/frame%dtest.jpg" % frame, prj)
    #tsm = masked_image(prj, np.array([26,150,130]), np.array([30,255,215]))
    #transom = largest_contour(tsm)
    #wtl = masked_image(prj, np.array([30,204,105]), np.array([40,255,224]))
    #waterline = largest_contour(wtl)
    
    #cv2.drawContours(prj, [transom], 0, 0, 2)
    #cv2.drawContours(prj, [waterline], 0, 0, 2)
    #cv2.cvtColor(prj, cv2.COLOR_BGR2RGB)
    #cv2.imwrite("../images/testing/frame%dtest.jpg" % frame, prj)

def write_elevations(heights, data_path):
    with open(data_path,'a') as data:
        write = csv.writer(data)
        write.writerows([heights])

def get_elevations(data_path):
    for frame in range(1500):
        image_name = "../images/frame%d.jpg" % frame
        img = cv2.imread(image_name)
        
        prj = apply_morphology(corrected_perspective(img))
        tsm = masked_image(prj, np.array([26,150,130]), np.array([30,255,215]))
        transom = largest_contour(tsm)
        wtl = masked_image(prj, np.array([30,204,105]), np.array([40,255,224]))
        waterline = largest_contour(wtl)
        heights = elevations(transom, waterline)
        
        write_elevations(heights, data_path)
    print("Video processing complete.")
        