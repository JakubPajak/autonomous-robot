import cv2
import numpy as np
from collections import deque

class LaneDetectorBin:
    def __init__(self, history_len=5):
        self.left_history = deque(maxlen=history_len)
        self.right_history = deque(maxlen=history_len)

    def process(self, frame):
        """
        Główna metoda: wykrywa linie, uśrednia, wygładza i zwraca obraz, offset i status.
        """
        left_lines, right_lines, roi_debug = self.detect_bin_lines(frame)

        left_line_raw = self.average_line(left_lines) if len(left_lines) > 0 else None
        right_line_raw = self.average_line(right_lines) if len(right_lines) > 0 else None

        left_line = self.smooth_poly(self.left_history, left_line_raw)
        right_line = self.smooth_poly(self.right_history, right_line_raw)

        output = frame.copy()
        output, status, offset = self.draw_guideline(output, left_line, right_line)

        return output, offset, status, roi_debug

    def detect_bin_lines(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        edges = cv2.Canny(blur, 50, 150)

        height, width = edges.shape
        roi_vertices = np.array([
            [int(0.15*width), height],
            [int(0.35*width), int(0.5*height)],
            [int(0.65*width), int(0.5*height)],
            [int(0.85*width), height]
        ])

        mask = np.zeros_like(edges)
        cv2.fillPoly(mask, [roi_vertices], 255)
        roi_edges = cv2.bitwise_and(edges, mask)

        roi_debug = cv2.cvtColor(roi_edges, cv2.COLOR_GRAY2BGR)
        cv2.polylines(roi_debug, [roi_vertices], isClosed=True, color=(0,255,255), thickness=2)

        lines = cv2.HoughLinesP(
            roi_edges,
            rho=1,
            theta=np.pi/180,
            threshold=40,
            minLineLength=150,
            maxLineGap=20
        )

        left_lines, right_lines = [], []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x2 == x1:
                    continue
                slope = (y2 - y1) / (x2 - x1)
                dx = abs(x2 - x1)
                mid_x = (x1 + x2) / 2
                if slope < -0.3 and dx > 50 and mid_x < width/2:
                    left_lines.append((x1,y1,x2,y2))
                elif slope > 0.3 and dx > 50 and mid_x > width/2:
                    right_lines.append((x1,y1,x2,y2))

        return left_lines, right_lines, roi_debug

    def average_line(self, lines):
        if len(lines) == 0:
            return None
        x_coords, y_coords = [], []
        for x1,y1,x2,y2 in lines:
            x_coords += [x1, x2]
            y_coords += [y1, y2]
        poly = np.polyfit(y_coords, x_coords, 1)
        return poly

    def smooth_poly(self, history, new_poly):
        if new_poly is not None:
            history.append(new_poly)
            return np.mean(history, axis=0)
        return None

    def draw_guideline(self, frame, left_poly, right_poly):
        height, width, _ = frame.shape
        y1 = int(height * 0.5)
        y2 = height

        center_status = "NO LINES"
        offset = None

        if left_poly is not None and right_poly is not None:
            left_x1 = int(left_poly[0]*y1 + left_poly[1])
            left_x2 = int(left_poly[0]*y2 + left_poly[1])
            right_x1 = int(right_poly[0]*y1 + right_poly[1])
            right_x2 = int(right_poly[0]*y2 + right_poly[1])

            mid_x1 = (left_x1 + right_x1) // 2
            mid_x2 = (left_x2 + right_x2) // 2

            cv2.line(frame, (mid_x1, y1), (mid_x2, y2), (0,0,255), 3)
            cv2.line(frame, (left_x1,y1), (left_x2,y2), (255,0,0), 3)
            cv2.line(frame, (right_x1,y1), (right_x2,y2), (0,255,0), 3)

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



import cv2

# zakładamy, że LaneDetectorBin jest już zaimportowany

if __name__ == "__main__":
    image = cv2.imread("IMG_3156.jpg")
    detector = LaneDetectorBin()
    result, offset, status, roi_debug = detector.process(image)

    # Tworzymy okna i ustawiamy je w tryb fullscreen
    cv2.namedWindow("Lane Detection", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Lane Detection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    cv2.namedWindow("ROI Mask", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("ROI Mask", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        cv2.imshow("Lane Detection", result)
        cv2.imshow("ROI Mask", roi_debug)
        print(f"Offset: {offset}, Status: {status}")  # debug/log

        # ESC żeby wyjść
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
