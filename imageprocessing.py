import cv2
import numpy as np

def Crop(image, cropping):
    if np.any(cropping):
        return image[int(cropping[1]):int(cropping[1]+cropping[3]), 
                    int(cropping[0]):int(cropping[0]+cropping[2])]
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

# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)