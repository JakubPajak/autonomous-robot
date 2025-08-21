import cv2 as cv
from ultralytics import YOLO


class NNProcessVideoFrame:
    def __init__(self, model_path="../best.pt"):

        # wczytanie modelu YOLOv8
        self.model = YOLO(model_path)

        print("YOLOv8 standalone listener started...")

    def process(self, frame):
        if not frame.any():
            raise RuntimeError("Brak klatki z video!")

            # detekcja obiektów
        results = self.model.predict(frame, verbose=False)

        # narysowanie bboxów na obrazie
        annotated_frame = results[0].plot()

        return annotated_frame
