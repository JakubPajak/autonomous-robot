import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import numpy as np
import cv2 as cv
from cv_bridge import CvBridge

class CameraFramePublisher(Node):

    def __init__(self):
        super().__init__('camera_frame_publisher')
        self.publisher_rgb_ = self.create_publisher(Image, 'img_raw', 10)
        self.publisher_bin_ = self.create_publisher(Image, 'img_bin', 10)

        self.camera = cv.VideoCapture(0)
        self.bridge = CvBridge()

        self.timer = self.create_timer(1/30, self.publisher_callback)  

        self.get_logger().info('Publishing video frames in bin & rgb')

    def publisher_callback(self):
        ret, frame = self.camera.read()
        if not ret:
            return

        msg_rgb = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        self.publisher_rgb_.publish(msg_rgb)

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        _, binary = cv.threshold(gray, 128, 255, cv.THRESH_BINARY)

        msg_bin = self.bridge.cv2_to_imgmsg(binary, encoding="mono8")
        self.publisher_bin_.publish(msg_bin)

    def stop(self):
        self.camera.release()
        cv.destroyAllWindows()

def main(args=None):
    rclpy.init(args=args)
    camera_publisher = CameraFramePublisher()
    rclpy.spin(camera_publisher)
    camera_publisher.stop()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
