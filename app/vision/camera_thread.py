# app/vision/camera_thread.py
import cv2

class CameraThread:
    def __init__(self, cam_idx=0):
        self.cap = cv2.VideoCapture(cam_idx)
        self.last_frame = None
        self.running = False

    def read_frame(self):
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                self.last_frame = frame
        return self.last_frame

    def stop(self):
        self.running = False

    def start(self):
        self.running = True

    def release(self):
        self.cap.release()
