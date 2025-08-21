import cv2 as cv
import numpy as np
from collections import deque

class LaneDetector:
    def __init__(self, history_len=5):
        self.left_history = deque(maxlen=history_len)
        self.right_history = deque(maxlen=history_len)

    def process(self, frame):
        """
        Wykonuje detekcję linii na obrazie.
        Zwraca: (frame_with_overlay, offset, status)
        """
        left_lines, right_lines, roi_debug = self.detect_black_lines(frame)
        left_poly_raw = self.average_line(left_lines) if len(left_lines) > 0 else None
        right_poly_raw = self.average_line(right_lines) if len(right_lines) > 0 else None

        # wygładzenie wyników
        left_poly = self.smooth_poly(self.left_history, left_poly_raw)
        right_poly = self.smooth_poly(self.right_history, right_poly_raw)

        output = frame.copy()
        output, status, offset = self.draw_guideline(output, left_poly, right_poly)

        return output, offset, status

    def detect_black_lines(self, frame):
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        lower_black = np.array([0, 0, 0], dtype="uint8")
        upper_black = np.array([180, 50, 80], dtype="uint8")
        mask = cv.inRange(hsv, lower_black, upper_black)

        height, width = mask.shape
        roi_mask = np.zeros_like(mask)

        top_width = int(width * 0.3)
        bottom_width = width
        top_y = int(height * 0.5)
        bottom_y = height

        vertices = np.array([[
            ((width - top_width) // 2, top_y),
            ((width + top_width) // 2, top_y),
            (bottom_width, bottom_y),
            (0, bottom_y)
        ]], dtype=np.int32)

        roi_debug = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)
        cv.polylines(roi_debug, [vertices], isClosed=True, color=(255, 0, 0), thickness=2)

        cv.fillPoly(roi_mask, vertices, 255)
        roi = cv.bitwise_and(mask, roi_mask)

        kernel = np.ones((3, 3), np.uint8)
        roi = cv.erode(roi, kernel, iterations=1)
        roi = cv.dilate(roi, kernel, iterations=2)

        edges = cv.Canny(roi, 50, 150)

        lines = cv.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=20)

        left_lines, right_lines = [], []
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    slope = (y2 - y1) / (x2 - x1 + 0.0001)
                    if abs(slope) < 0.5:
                        continue
                    if (x1 + x2) / 2 < width / 2:
                        left_lines.append((x1, y1, x2, y2))
                    else:
                        right_lines.append((x1, y1, x2, y2))
        return left_lines, right_lines, roi_debug

    def smooth_poly(self, history, new_poly):
        if new_poly is not None:
            history.append(new_poly)
            return np.mean(history, axis=0)
        else:
            return None

    def average_line(self, lines):
        if len(lines) == 0:
            return None
        x_coords, y_coords = [], []
        for x1, y1, x2, y2 in lines:
            x_coords += [x1, x2]
            y_coords += [y1, y2]
        poly = np.polyfit(y_coords, x_coords, deg=1)
        return poly

    def draw_guideline(self, frame, left_poly, right_poly):
        height, width, _ = frame.shape
        y1 = int(height * 0.5)
        y2 = height

        center_status = "NO LINES"
        offset = None

        if left_poly is not None and right_poly is not None:
            left_x1 = int(left_poly[0] * y1 + left_poly[1])
            left_x2 = int(left_poly[0] * y2 + left_poly[1])
            right_x1 = int(right_poly[0] * y1 + right_poly[1])
            right_x2 = int(right_poly[0] * y2 + right_poly[1])

            mid_x1 = (left_x1 + right_x1) // 2
            mid_x2 = (left_x2 + right_x2) // 2

            cv.line(frame, (mid_x1, y1), (mid_x2, y2), (0, 0, 255), 3)
            cv.line(frame, (left_x1, y1), (left_x2, y2), (0, 255, 0), 2)
            cv.line(frame, (right_x1, y1), (right_x2, y2), (0, 255, 0), 2)

            mid_screen = width // 2
            offset = mid_x2 - mid_screen

            if abs(offset) < width * 0.05:
                center_status = "CENTER"
            elif offset < 0:
                center_status = "LEFT"
            else:
                center_status = "RIGHT"
        elif left_poly is not None:
            center_status = "LEFT (ONLY LEFT LINE)"
        elif right_poly is not None:
            center_status = "RIGHT (ONLY RIGHT LINE)"

        return frame, center_status, offset
