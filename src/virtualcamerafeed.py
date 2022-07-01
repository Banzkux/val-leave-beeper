# import the necessary packages
from threading import Thread
import cv2

class VirtualCameraFeed:
	def __init__(self, src=0, resolution=[640,480], name="VirtualCameraFeed"):
		# initialize the virtual camera feed and read the first frame
		# from the stream
		self.stream = cv2.VideoCapture(src)
		self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
		self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
		(self.grabbed, self.frame) = self.stream.read()

		# initialize the thread name
		self.name = name

		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False
	
	def read(self):
		# return the frame most recently read
		return self.frame

	def start(self):
		# start the thread to read frames from the video stream
		t = Thread(target=self.update, name=self.name, args=())
		t.daemon = True
		t.start()
		return self
	
	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True

	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				self.stream.release()
				return

			# otherwise, read the next frame from the stream
			(self.grabbed, self.frame) = self.stream.read()