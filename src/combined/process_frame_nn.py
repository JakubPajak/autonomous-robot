import cv2 as cv
from ultralytics import YOLO

class NNProcessFrame:
    def __init__(self, model_path="best.pt"):
        self.model = YOLO(model_path)
        print("YOLOv8 standalone listener started...")

    def process(self, frame):
        if frame is None or not frame.any():
            print("Brak klatki z kamery")
            return frame, None

        results = self.model.predict(frame, verbose=False)
        annotated_frame = results[0].plot()

        boxes = results[0].boxes
        if len(boxes) < 2:
            return annotated_frame, None
        
        boxes_sorted = sorted(boxes, key=lambda b: (b.xyxy[0][3]-b.xyxy[0][1]), reverse=True)
        main_boxes = boxes_sorted[:2]

        centers = []
        for box in main_boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            centers.append((cx, cy))
            cv.circle(annotated_frame, (int(cx), int(cy)), 6, (0, 255, 0), -1)

        middle_point = None
        if len(centers) == 2:
            x_mid = int((centers[0][0] + centers[1][0]) / 2)
            y_mid = int((centers[0][1] + centers[1][1]) / 2)
            middle_point = (x_mid, y_mid)
            cv.circle(annotated_frame, middle_point, 8, (0, 0, 255), -1)

        annotated_frame = self.draw_middle_line(annotated_frame, middle_point, (main_boxes))

        return annotated_frame, middle_point
    
    def draw_middle_line(self, frame, middle_point, boxes):
        if middle_point is None or len(boxes) < 2:
            return frame

        h, w = frame.shape[:2]
        x_mid, y_mid = middle_point

        top_centers = []
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cx_top = (x1 + x2) / 2
            cy_top = y1
            top_centers.append((cx_top, cy_top))

        if abs(top_centers[0][0] - top_centers[1][0]) < 40:
            return frame

        top_middle = (
            int((top_centers[0][0] + top_centers[1][0]) / 2),
            int((top_centers[0][1] + top_centers[1][1]) / 2),
        )

        # rysujemy prostą między punktami
        cv.line(frame, middle_point, top_middle, (255, 0, 0), 2)

        return frame

