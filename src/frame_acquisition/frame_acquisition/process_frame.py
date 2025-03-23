import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from std_msgs.msg import String
from std_msgs.msg import Float32
import cv2 as cv
import numpy as np
from collections import deque

class ProcessFrame(Node):

    def __init__(self):
        super().__init__('proces_frame')
        self.bridge = CvBridge()
        self.left_history = deque(maxlen=5)
        self.right_history = deque(maxlen=5)
        self.msg = Float32()
        
        self.frame_subscriber_rgb = self.create_subscription(
            Image, 
            'img_raw',
            self.listener_callback,
            10
        )

        self.offset_value_publisher_ = self.create_publisher(
            Float32, 
            'offset_value',
            10,
        )
        self.image_debug = self.create_publisher(
            Image, 
            'image_debug',
            10,
        )

        self.frame_subscriber_rgb
        self.get_logger().info('Listener opened ... ')

    def listener_callback(self, img):
        frame = self.bridge.imgmsg_to_cv2(img, desired_encoding='passthrough')

        self.perform_detection(frame)


    def perform_detection(self, frame):

        left_lines, right_lines, roi_debug = self.detect_black_lines(frame)
        left_poly_raw = self.average_line(left_lines) if len(left_lines) > 0 else None
        right_poly_raw = self.average_line(right_lines) if len(right_lines) > 0 else None

        # Wygładzanie wyników (średnia ruchoma)
        left_poly = self.smooth_poly(self.left_history, left_poly_raw)
        right_poly = self.smooth_poly(self.right_history, right_poly_raw)

        output = frame.copy()  # Skopiuj klatkę do rysowania
        output, status = self.draw_guideline(output, left_poly, right_poly)  # Rysuj linie i status jazdy

        height, width, _ = frame.shape  # Potrzebne do obliczenia offsetu
        y2 = height  # Punkt na dole ekranu

        if left_poly is not None and right_poly is not None:
            # Oblicz pozycję linii środkowej na dole ekranu
            left_x2 = int(left_poly[0] * y2 + left_poly[1])
            right_x2 = int(right_poly[0] * y2 + right_poly[1])
            mid_x2 = (left_x2 + right_x2) // 2  # Środek między lewą a prawą linią
            mid_screen = width // 2  # Środek ekranu
            
            offset = mid_x2 - mid_screen  # Oblicz offset względem środka obrazu
            self.msg.data = float(offset)
            self.offset_value_publisher_.publish(self.msg)

            # Sprawdzenie czy punkt na środku ekranu leży "na linii"
            if abs(offset) < width * 0.05:  # Tolerancja 5% szerokości
                self.get_logger().info(f'On the line: "{offset:.2f}"')
                
            else:
                self.get_logger().info(f'Out the line: "{offset:.2f}"')
                



    def detect_black_lines(self, frame):
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)  # Konwersja obrazu z BGR na HSV

        lower_black = np.array([0, 0, 0], dtype="uint8")  # Dolny zakres dla koloru czarnego w HSV
        upper_black = np.array([180, 50, 80], dtype="uint8")  # Górny zakres dla koloru czarnego w HSV
        mask = cv.inRange(hsv, lower_black, upper_black)  # Tworzenie maski tylko dla czarnych obszarów

        height, width = mask.shape  # Pobranie wysokości i szerokości obrazu
        roi_mask = np.zeros_like(mask)  # Utworzenie pustej maski do wycięcia trapezu

        top_width = int(width * 0.3)  # Szerokość górnej krawędzi trapezu (30% szerokości obrazu)
        bottom_width = width  # Szerokość dolnej krawędzi trapezu (pełna szerokość)
        top_y = int(height * 0.5)  # Położenie górnej krawędzi trapezu na 50% wysokości obrazu
        bottom_y = height  # Dolna krawędź trapezu na dole obrazu

        # Definicja wierzchołków trapezu
        vertices = np.array([[ 
            ((width - top_width) // 2, top_y),  # Lewy górny punkt
            ((width + top_width) // 2, top_y),  # Prawy górny punkt
            (bottom_width, bottom_y),           # Prawy dolny punkt
            (0, bottom_y)                       # Lewy dolny punkt
        ]], dtype=np.int32)

        # Tworzenie podglądu maski z narysowanym konturem trapezu
        roi_debug = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)  # Zamiana maski na obraz kolorowy dla debugowania
        cv.polylines(roi_debug, [vertices], isClosed=True, color=(255, 0, 0), thickness=2)  # Narysowanie trapezu

        cv.fillPoly(roi_mask, vertices, 255)  # Wypełnienie trapezu na masce ROI
        roi = cv.bitwise_and(mask, roi_mask)  # Zastosowanie maski trapezu do obrazu z czarnymi liniami

        # Operacje morfologiczne dla wygładzenia konturów
        kernel = np.ones((3, 3), np.uint8)  # Małe jądro 3x3 piksele
        roi = cv.erode(roi, kernel, iterations=1)  # Erozja w celu usunięcia szumów
        roi = cv.dilate(roi, kernel, iterations=2)  # Dylacja w celu wzmocnienia linii

        edges = cv.Canny(roi, 50, 150)  # Detekcja krawędzi metodą Canny’ego

        # Detekcja linii metodą probabilistyczną Hougha
        lines = cv.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=20)

        left_lines = []  # Lista linii po lewej stronie
        right_lines = []  # Lista linii po prawej stronie

        if lines is not None:  # Jeśli wykryto jakieś linie
            for line in lines:  # Iteracja po każdej linii
                for x1, y1, x2, y2 in line:
                    slope = (y2 - y1) / (x2 - x1 + 0.0001)  # Obliczenie nachylenia linii
                    if abs(slope) < 0.5:  # Odrzucenie linii prawie poziomych
                        continue
                    if (x1 + x2) / 2 < width / 2:  # Sprawdzenie, czy linia leży po lewej stronie
                        left_lines.append((x1, y1, x2, y2))
                    else:  # Inaczej linia po prawej stronie
                        right_lines.append((x1, y1, x2, y2))

        return left_lines, right_lines, roi_debug  # Zwrócenie linii i obrazu debugującego


    def smooth_poly(self, history, new_poly):
        if new_poly is not None:  # Jeśli wykryto nową linię
            history.append(new_poly)  # Dodaj nową prostą do historii
            avg = np.mean(history, axis=0)  # Uśrednij prostą na podstawie historii
            return avg
        else:
            return None  # Jeśli nie wykryto linii, nie zmieniaj bufora

    # Funkcja do obliczenia prostej (y = ax + b) na podstawie zbioru punktów linii
    def average_line(self, lines):
        if len(lines) == 0:  # Jeśli brak linii, zwróć None
            return None
        x_coords = []  # Lista X-ów
        y_coords = []  # Lista Y-ów
        for x1, y1, x2, y2 in lines:
            x_coords += [x1, x2]  # Dodaj współrzędne X obu końców linii
            y_coords += [y1, y2]  # Dodaj współrzędne Y obu końców linii
        poly = np.polyfit(y_coords, x_coords, deg=1)  # Dopasuj linię prostą
        return poly  # Zwróć współczynniki prostej

    # Funkcja rysująca linie prowadzące i środek pasa
    def draw_guideline(self, frame, left_poly, right_poly):
        height, width, _ = frame.shape  # Pobranie wymiarów obrazu
        y1 = int(height * 0.5)  # Poziom startu rysowania (połowa obrazu)
        y2 = height  # Koniec rysowania na dole obrazu

        center_status = "NO LINES"  # Domyślny status

        if left_poly is not None and right_poly is not None:  # Obie linie wykryte
            # Obliczenie punktów przecięcia linii z poziomami y1 i y2
            left_x1 = int(left_poly[0] * y1 + left_poly[1])
            left_x2 = int(left_poly[0] * y2 + left_poly[1])
            right_x1 = int(right_poly[0] * y1 + right_poly[1])
            right_x2 = int(right_poly[0] * y2 + right_poly[1])

            # Obliczenie środka pasa na górze i dole trapezu
            mid_x1 = (left_x1 + right_x1) // 2
            mid_x2 = (left_x2 + right_x2) // 2

            # Narysowanie linii środkowej (czerwonej)
            cv.line(frame, (mid_x1, y1), (mid_x2, y2), (0, 0, 255), 3)
            # Narysowanie linii lewego pasa (zielonej)
            cv.line(frame, (left_x1, y1), (left_x2, y2), (0, 255, 0), 2)
            # Narysowanie linii prawego pasa (zielonej)
            cv.line(frame, (right_x1, y1), (right_x2, y2), (0, 255, 0), 2)

            img_2_send = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            self.image_debug.publish(img_2_send)
            
            mid_screen = width // 2  # Środek obrazu (ekranu)
            offset = mid_x2 - mid_screen  # Obliczenie przesunięcia od środka

            # Określenie statusu skrętu na podstawie offsetu
            if abs(offset) < width * 0.05:
                center_status = "CENTER"
            elif offset < 0:
                center_status = "LEFT"
            else:
                center_status = "RIGHT"
        elif left_poly is not None:  # Jeśli wykryto tylko lewą linię
            center_status = "LEFT (ONLY LEFT LINE)"
        elif right_poly is not None:  # Jeśli wykryto tylko prawą linię
            center_status = "RIGHT (ONLY RIGHT LINE)"

        return frame, center_status  # Zwróć obraz z liniami i status skrętu

def main(args=None):
    rclpy.init(args=args)
    frame_subscriber = ProcessFrame()
    rclpy.spin(frame_subscriber)
    frame_subscriber.stop()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
