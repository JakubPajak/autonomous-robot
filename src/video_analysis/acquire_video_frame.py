import cv2 as cv
import os

class PhotoStream:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.files = sorted([
            os.path.join(folder_path, f) 
            for f in os.listdir(folder_path) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])
        self.index = 0

        if not self.files:
            raise RuntimeError(f"Brak obrazów w folderze: {folder_path}")

    def get_frame(self):
        if self.index < len(self.files):
            frame = cv.imread(self.files[self.index])
            self.index += 1
            return frame
        return None

    def reset(self):
        self.index = 0

    def release(self):
        pass
