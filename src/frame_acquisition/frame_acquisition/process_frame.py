import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import cv2 as cv
import numpy as np

class ProcessFrame(Node):

    def __init__(self):
        super().__init__('proces_frame')
        self.bridge = CvBridge()

        self.frame_subscriber_rgb = self.create_subscription(
            Image, 
            'img_raw',
            self.listener_callback,
            10
        )

        self.frame_subscriber_rgb
        self.get_logger().info('Listener opened ... ')

    def listener_callback(self, img):
        frame = self.bridge.imgmsg_to_cv2(img, encoding='rgb8')

def main(args=None):
    rclpy.init(args=args)
    frame_subscriber = ProcessFrame()
    rclpy.spin(frame_subscriber)
    frame_subscriber.stop()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
