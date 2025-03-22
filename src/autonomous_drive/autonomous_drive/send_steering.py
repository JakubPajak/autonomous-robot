import rclpy
from rclpy.node import Node
import serial
import time

class SerialSender(Node):
    def __init__(self):
        super().__init__('serial_sender')

        self.serial_port = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        time.sleep(2)  

        self.timer = self.create_timer(1.0, self.send_data)  
        self.get_logger().info("Serial sender node started.")

    def send_data(self):
        data = '1' if int(time.time()) % 2 == 0 else '0'

        self.serial_port.write(f"{data}\n".encode())

        self.get_logger().info(f"Sent: {data}")

    def stop(self):
        self.serial_port.close()

def main(args=None):
    rclpy.init(args=args)
    node = SerialSender()
    rclpy.spin(node)
    node.stop()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
