import cv2 as cv

class CameraStream:
    def __init__(self, camera_id=0, width=None, height=None, fps=30):
        self.cap = cv.VideoCapture(camera_id)
        if width:
            self.cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
        if height:
            self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        if fps:
            self.cap.set(cv.CAP_PROP_FPS, fps)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera {camera_id}")

    def get_frame(self, binary=False):
        """Zwraca ramkę RGB lub binarną (mono)."""
        ret, frame = self.cap.read()
        if not ret:
            return None

        if binary:
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            _, frame = cv.threshold(gray, 128, 255, cv.THRESH_BINARY)
        return frame

    def show_stream(self, binary=False):
        """Podgląd w oknie."""
        frame = self.get_frame(binary=binary)
        if frame is not None:
            cv.imshow("Camera", frame)
            return True
        return False

    def release(self):
        self.cap.release()
        cv.destroyAllWindows()
