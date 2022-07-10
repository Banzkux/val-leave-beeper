import cv2
import numpy as np

def Crop(image, cropping):
    if np.any(cropping):
        return image[int(cropping[1]):int(cropping[3]),
                    int(cropping[0]):int(cropping[2])]
    else:
        return image

def DrawFPS(image, fps):
    font                   = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (0,30)
    fontScale              = 1
    fontColor              = (255,255,255)
    thickness              = 2
    lineType               = 1

    cv2.putText(image, fps, 
    bottomLeftCornerOfText, 
    font, 
    fontScale,
    fontColor,
    thickness,
    lineType)
    return image

def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def scale_image(image, scale):
    width = int(image.shape[1] * scale)
    height = int(image.shape[0] * scale)
    dim = (width, height)
    return cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

def change_aspect_ratio(image, aspect):
    width = int(image.shape[1] + image.shape[1] % aspect[0])
    height = int(width/aspect[0] * aspect[1])
    return cv2.resize(image, (width, height), interpolation = cv2.INTER_AREA)

def match_template(image, template):
    img_gray = get_grayscale(image)
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    return loc