import cv2
import numpy as np
from utils import VirtualCameraFeed # Threaded video feed
from utils.imageprocessing import scale_image, Crop

class Cropping:
    def __init__(self, device_index, cropping):
        self.cropping = cropping
        self.window_name = "Cropping window"
        self.stream = VirtualCameraFeed(device_index)
        self.stream.start()
        self.scale = 1
        self.image = self.stream.read()

        # Mouse button held
        self.l_button = False
        self.r_button = False

        if np.any(cropping):
            self.p1 = [self.cropping[0], self.cropping[1]]
            self.p2 = [self.cropping[2], self.cropping[3]]
        else:
            self.p1 = [-1, -1]
            self.p2 = [-1, -1]
        print("Pick two points for your cropping area.",
                "Left click for p1, right click for p2.")
        print("Press space to confirm selection,",
            "Press R to reset the cropping selection. - and + resizes the window.")
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        while cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) > 0:
            self.image = scale_image(self.stream.read(), self.scale)
            if self.p1 != [-1, -1]:
                converted_pos = self.convert_position(self.p1)
                self.image = cv2.circle(self.image, converted_pos, 1, (255,0,0))
            if self.p2 != [-1, -1]:
                converted_pos = self.convert_position(self.p2)
                self.image = cv2.circle(self.image, converted_pos, 1, (0,255,0))
            if self.p1 != [-1, -1] and self.p2 != [-1, -1]:
                self.image = cv2.rectangle(self.image, 
self.convert_position(self.p1), self.convert_position(self.p2),
                (0,0,255), 2)

            cv2.imshow(self.window_name, self.image)

            c = cv2.waitKey(1)
            # Resize the picture with +/-
            if c == 43:
                self.scale += 0.25
                self.scale = min(1, self.scale)
            elif c == 45:
                self.scale -= 0.25
                self.scale = max(0.25, self.scale)
            # Space pressed
            elif c == 32:
                cv2.destroyWindow(self.window_name)
                break
            elif c == 114:
                # Cancel selections
                self.p1 = [-1, -1]
                self.p2 = [-1, -1]

        # Gets top left and bottom right corners
        tl = [min(self.p1[0], self.p2[0]), min(self.p1[1], self.p2[1])]
        br = [max(self.p1[0], self.p2[0]), max(self.p1[1], self.p2[1])]
        if self.p1 != [-1, -1] and self.p2 != [-1, -1]:
            self.cropping = tl + br
        else:
            self.cropping = [0, 0, 0, 0]
        
        window_name = self.window_name + " preview"
        cv2.namedWindow(window_name)
        
        while cv2.getWindowProperty(window_name , cv2.WND_PROP_VISIBLE) > 0:
            self.image = Crop(self.stream.read(), self.cropping)
            self.image = scale_image(self.image, self.scale)
        
            cv2.imshow(window_name, self.image)

            c = cv2.waitKey(1)
            if c != -1:
                cv2.destroyWindow(window_name)
                break
            
        self.stream.stop()

    def mouse_callback(self, action, x, y, flags, *userdata):
        max_width = self.stream.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
        max_height = self.stream.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
        # Keep x and y inside the window
        x = max(min(max_width * self.scale, x), 0)
        y = max(min(max_height * self.scale, y), 0)
        if action == cv2.EVENT_LBUTTONDOWN:
            self.l_button = True
        elif action == cv2.EVENT_LBUTTONUP:
            self.l_button = False
        elif action == cv2.EVENT_RBUTTONDOWN:
            self.r_button = True
        elif action == cv2.EVENT_RBUTTONUP:
            self.r_button = False
        elif action == cv2.EVENT_MOUSEMOVE:
            if self.l_button:
                self.p1 = [int(x/self.scale), int(y/self.scale)]
            if self.r_button:
                self.p2 = [int(x/self.scale), int(y/self.scale)]

    def convert_position(self, position):
        return [int(i * self.scale) for i in position]
    def done(self):
        return self.cropping
