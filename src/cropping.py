import cv2
from virtualcamerafeed import VirtualCameraFeed # Threaded video feed
from imageprocessing import scale_image, Crop

class Cropping:
    def __init__(self, device_index, resolution):
        self.cropping = [0, 0, 0, 0]
        self.window_name = "Cropping window"
        self.stream = VirtualCameraFeed(device_index, resolution)
        self.stream.start()
        self.scale = 1
        self.image = self.stream.read()
        self.p1 = [-1, -1]
        self.p2 = [-1, -1]
        print("Pick two points for your cropping area.",
                "Left click for p1, right click for p2.")
        print("Press space to confirm selection,",
            "Press Esc or C for no cropping. - and + resizes the window.")
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        while True:
            c = cv2.waitKey(1)
            # Resize the picture with +/-
            if c == 43:
                self.scale += 0.25
                self.scale = min(1, self.scale)
            elif c == 45:
                self.scale -= 0.25
                self.scale = max(0.25, self.scale)
            elif c == 32:
                break
            elif c == 27 or c == 99:
                # Cancel selections
                self.p1 = [-1, -1]
                self.p2 = [-1, -1]
                print("No cropping selected.")
                break

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
                (0,0,255), 1)
            cv2.imshow(self.window_name, self.image)
        
        #self.cropping = cv2.selectROI(self.window_name, self.image, False)
        cv2.destroyWindow(self.window_name)
        tl = [min(self.p1[0], self.p2[0]), min(self.p1[1], self.p2[1])]
        br = [max(self.p1[0], self.p2[0]), max(self.p1[1], self.p2[1])]
        if self.p1 != [-1, -1] and self.p2 != [-1, -1]:
            self.cropping = tl + br
        while True:
            c = cv2.waitKey(1)
            if c != -1:
                cv2.destroyWindow(self.window_name + " preview")
                break
            
            self.image = Crop(self.stream.read(), self.cropping)
            self.image = scale_image(self.image, self.scale)
        
            cv2.imshow(self.window_name + " preview", self.image)
        self.stream.stop()

        print(self.cropping)

    def mouse_callback(self, action, x, y, flags, *userdata):
        if action == cv2.EVENT_LBUTTONDOWN:
            self.p1 = [int(x/self.scale), int(y/self.scale)]
        elif action == cv2.EVENT_RBUTTONDOWN:
            self.p2 = [int(x/self.scale), int(y/self.scale)]
    def convert_position(self, position):
        return [int(i * self.scale) for i in position]
    def done(self):
        return self.cropping
