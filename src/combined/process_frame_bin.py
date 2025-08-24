import cv2 as cv
import numpy as np
from collections import deque

class ProcessFrameBin:
    def __init__(self, history_len=5):
        self.left_history = deque(maxlen=history_len)
        self.right_history = deque(maxlen=history_len)

    def process(self, frame):
        h, w = frame.shape[:2]
        out = frame.copy()

        # --- ROI: trapez nad jezdnią (bez ucinania dołu) ---
        top_y = int(0.55 * h)
        roi_poly = np.array([[
            (int(0.15 * w), top_y),
            (int(0.85 * w), top_y),
            (w - 1, h - 1),
            (0,     h - 1),
        ]], dtype=np.int32)
        roi_mask = np.zeros((h, w), np.uint8)
        cv.fillPoly(roi_mask, roi_poly, 255)

        # --- Binaryzacja ukierunkowana na białe/żółte linie ---
        hls = cv.cvtColor(frame, cv.COLOR_BGR2HLS)
        white  = cv.inRange(hls, (0, 200,   0), (180, 255, 120))   # jasne linie
        yellow = cv.inRange(hls, (15, 100, 100), ( 40, 255, 255))  # żółte pasy
        binmask = cv.bitwise_or(white, yellow)
        binmask = cv.bitwise_and(binmask, roi_mask)
        binmask = cv.GaussianBlur(binmask, (5, 5), 0)

        # --- Trzymaj pionowe struktury (wytnij poziome śmieci) ---
        vert = cv.getStructuringElement(cv.MORPH_RECT, (3, 21))
        binmask = cv.morphologyEx(binmask, cv.MORPH_CLOSE, vert, iterations=1)

        # --- Krawędzie + Hough ---
        edges = cv.Canny(binmask, 50, 150)
        lines = cv.HoughLinesP(edges, 1, np.pi/180, threshold=60,
                               minLineLength=int(0.06*h), maxLineGap=int(0.02*h))

        left_pts, right_pts = [], []
        if lines is not None:
            for x1, y1, x2, y2 in lines[:, 0, :]:
                dx = (x2 - x1) + 1e-6
                slope = (y2 - y1) / dx
                if abs(slope) < 0.5:          # odfiltruj poziome
                    continue
                xm = (x1 + x2) / 2
                # klasyfikacja lewa/prawa
                if slope < 0 and xm < 0.55 * w:
                    left_pts  += [(x1, y1), (x2, y2)]
                elif slope > 0 and xm > 0.45 * w:
                    right_pts += [(x1, y1), (x2, y2)]

        # Dopasowanie prostych x = a*y + b
        left_poly  = self._fit_line(left_pts)
        right_poly = self._fit_line(right_pts)

        # Wygładzanie
        left_poly  = self._smooth(self.left_history,  left_poly)
        right_poly = self._smooth(self.right_history, right_poly)

        # --- Rysowanie, środek, offset ---
        status = "NO LINES"
        offset = None

        self._draw_roi(out, roi_poly)
        self._draw_line(out, left_poly,  (255,   0,   0), top_y, h - 1)
        self._draw_line(out, right_poly, (  0,   0, 255), top_y, h - 1)

        # Żółta strzałka prowadząca (krótka)
        self._draw_guideline_arrow(out, left_poly, right_poly, top_y, h - 1)

        if left_poly is not None and right_poly is not None:
            yb = h - 1
            xl = int(left_poly[0]  * yb + left_poly[1])
            xr = int(right_poly[0] * yb + right_poly[1])
            midx = (xl + xr) // 2

            # zielona linia pomocnicza (pełna)
            cv.line(out, (midx, top_y), (midx, h - 1), (0, 255, 0), 2)

            offset = midx - w // 2
            if abs(offset) < 0.05 * w:
                status = "CENTER"
            elif offset < 0:
                status = "LEFT"
            else:
                status = "RIGHT"

        return out, offset, status

    # ---------- helpers ----------

    def _fit_line(self, pts):
        """Dopasuj x = a*y + b do punktów."""
        if len(pts) < 4:
            return None
        pts = np.array(pts)
        y = pts[:, 1].astype(np.float32)
        x = pts[:, 0].astype(np.float32)
        a, b = np.polyfit(y, x, 1)
        return np.array([a, b], dtype=np.float32)

    def _smooth(self, hist, new_poly):
        """Prosta średnia ruchoma dla współczynników prostej."""
        if new_poly is None:
            return None if not hist else np.mean(np.stack(hist), axis=0)
        hist.append(new_poly)
        return np.mean(np.stack(hist), axis=0)

    def _line_x_at_y(self, poly, y):
        """Zwraca x(y) dla prostej x = a*y + b (lub None)."""
        if poly is None:
            return None
        return int(poly[0] * y + poly[1])

    def _draw_line(self, img, poly, color, y1, y2):
        if poly is None:
            return
        x1 = self._line_x_at_y(poly, y1)
        x2 = self._line_x_at_y(poly, y2)
        cv.line(img, (x1, y1), (x2, y2), color, 3)

    def _draw_guideline_arrow(self, img, left_poly, right_poly, y_top, y_bottom,
                              color=(0, 255, 255), shorten=0.35, min_sep_px=40):
        """
        Rysuje krótką żółtą strzałkę między dwiema liniami.
        - tail (start) na dole ROI, head ~shorten odległości w stronę góry.
        - nie rysuje, gdy odległość między liniami za mała.
        """
        if left_poly is None or right_poly is None:
            return

        xl_b = self._line_x_at_y(left_poly,  y_bottom)
        xr_b = self._line_x_at_y(right_poly, y_bottom)
        xl_t = self._line_x_at_y(left_poly,  y_top)
        xr_t = self._line_x_at_y(right_poly, y_top)
        if None in (xl_b, xr_b, xl_t, xr_t):
            return

        # separacja na dole ROI – gdy za mała, pomijamy
        if abs(xr_b - xl_b) < min_sep_px:
            return

        # środek między liniami na dole i u góry
        mid_b = ( (xl_b + xr_b)//2, y_bottom )
        mid_t = ( (xl_t + xr_t)//2, y_top )

        # skrócona strzałka (np. 35% drogi)
        dx = mid_t[0] - mid_b[0]
        dy = mid_t[1] - mid_b[1]
        head = ( int(mid_b[0] + dx * shorten), int(mid_b[1] + dy * shorten) )

        # narysuj strzałkę (grubsza, dobrze widoczna)
        cv.arrowedLine(img, mid_b, head, color, thickness=4, tipLength=0.25)

    def _draw_roi(self, img, poly):
        cv.polylines(img, [poly], isClosed=True, color=(0, 255, 255), thickness=2)
