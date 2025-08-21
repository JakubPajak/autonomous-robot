import cv2 as cv
from ultralytics import YOLO


class NNProcessFrame:
    def __init__(self, cam_index=0, model_path="best.pt"):

        # wczytanie modelu YOLOv8
        self.model = YOLO(model_path)

        print("YOLOv8 standalone listener started...")

    def run(self, frame):
        if not frame.any():
            print("Brak klatki z kamery")

            # detekcja obiektów
        results = self.model.predict(frame, verbose=False)

        # narysowanie bboxów na obrazie
        annotated_frame = results[0].plot()

        return annotated_frame

    def stop(self):
        cv.destroyAllWindows()
