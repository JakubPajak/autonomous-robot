import cv2 as cv
import os 

class FrameStream:
    def __init__(self, camera_id, folder_path, width=None, 
                 height=None, fps=30):
        if camera_id is not None:
            self.cap = cv.VideoCapture(camera_id)
            self.mode = "live"
            if width:
                self.cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
            if height:
                self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
            if fps:
                self.cap.set(cv.CAP_PROP_FPS, fps)
            if not self.cap.isOpened():
                raise RuntimeError(f"Cannot open camera {camera_id}")
            
        elif folder_path is not None:
            self.folder_path = folder_path
            self.mode = "photo"
            self.files = sorted([
                os.path.join(folder_path, f) 
                for f in os.listdir(folder_path) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))
                ])
            self.index = 0
            if not self.files:
                raise RuntimeError(f"No images in the folder path provided: {folder_path}")

    def get_frame(self, binary=False):
        if self.mode == "live":
            ret, frame = self.cap.read()
            if not ret:
                return None

            if binary:
                gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                _, frame = cv.threshold(gray, 128, 255, cv.THRESH_BINARY)
            return frame
        else:
            if self.index < len(self.files):
                frame = cv.imread(self.files[self.index])
                self.index += 1
                return frame
            return None

    def release(self):
        self.cap.release()
        cv.destroyAllWindows()
