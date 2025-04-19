import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from std_msgs.msg import String
from std_msgs.msg import Float32
import cv2 as cv
import numpy as np
from collections import deque

class ProcessFrameBin(Node):

    def __init__(self):
        super().__init__('proces_frame_bin')
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
            'offset_value_bin',
            10,
        )
        self.image_debug = self.create_publisher(
            Image, 
            'image_debug_bin',
            10,
        )

        self.frame_subscriber_rgb
        self.get_logger().info('Listener opened ... ')


    def listener_callback(self, img):
        frame = self.bridge.imgmsg_to_cv2(img, desired_encoding='passthrough')

        self.perform_detection(frame)

    def perform_detection(self, frame):
        kernel = np.ones((5, 5), np.uint8)  

        height = frame.shape[0]
        bottom = frame[int(height * 0.7):, :]

        gray = cv.cvtColor(bottom, cv.COLOR_BGR2GRAY)
        blur = cv.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv.threshold(blur, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)

        dilated = cv.dilate(thresh, kernel, iterations=1)

        histogram = np.sum(dilated, axis=0)
        lines = np.where(histogram > np.max(histogram) * 0.5)[0]

        if len(lines) > 1:
            left = lines[0]
            right = lines[-1]

            # if right - left < 50:
            #     cv.imshow("Progowanie", dilated)
            #     cv.imshow("Linie", dol)
            #     if cv2.waitKey(10) & 0xFF == ord('q'):
            #         break
            #     continue

            left_border = []
            right_border = []
            center_line = []

            for y in range(bottom.shape[0]):
                left_point = None
                right_point = None

                    
                for x in range(left, right - 1):
                    if dilated[y, x] == 255 and dilated[y, x + 1] == 0:
                        left_point = (x, y)
                        break

                    
                for x in range(right, left + 1, -1):
                    if dilated[y, x] == 255 and dilated[y, x - 1] == 0:
                        right_point = (x, y)
                        break

                if left_point and right_point:
                    left_border.append(left_point)
                    right_border.append(right_point)
                    center_line.append(((left_point[0] + right_point[0]) // 2, y))

            if len(left_border) > 1:
                left_line = np.array(left_border)
                cv.polylines(bottom, [left_line], False, (255, 0, 0), 2)  

            if len(right_border) > 1:
                right_line = np.array(right_border)
                cv.polylines(bottom, [right_line], False, (0, 0, 255), 2)  

            if len(center_line) > 1:
                center_line = np.array(center_line)
                cv.polylines(bottom, [center_line], False, (0, 255, 0), 2)  

        img_2_send = self.bridge.cv2_to_imgmsg(frame)
        self.image_debug.publish(img_2_send)
        self.offset_value_publisher_.publish(center_line)

        # cv2.imshow("Progowanie", dilated)
        # cv2.imshow("Linie", dol)


def main(args=None):
    rclpy.init(args=args)
    frame_subscriber = ProcessFrameBin()
    rclpy.spin(frame_subscriber)
    frame_subscriber.stop()
    rclpy.shutdown()

if __name__ == '__main__':
    main()


