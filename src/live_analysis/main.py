from acquire_frame import CameraStream 
from process_frame_rgb import LaneDetector
from process_frame_nn import NNProcessFrame
import cv2 as cv


def main():
    # wybór trybu działania
    print("Wybierz tryb działania:")
    print("1 - Lane Detection")
    print("2 - YOLOv8 NN Detection")
    mode = input("Twój wybór [1/2]: ").strip()

    cam = CameraStream(camera_id=0)

    if mode == "1":
        detector = LaneDetector()
        while True:
            frame = cam.get_frame()
            if frame is None:
                break

            processed, offset, status = detector.process(frame)

            if offset is not None:
                print(f"Offset: {offset:.2f}, Status: {status}")
            else:
                print(f"Status: {status}")

            cv.imshow("Lane Detection", processed)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

    elif mode == "2":
        detector = NNProcessFrame(model_path="src/best.pt")
        while True:
            frame = cam.get_frame()
            if frame is None:
                break

            processed = detector.run(frame)

            cv.imshow("YOLOv8 Detection", processed)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

    else:
        print("Nieprawidłowy wybór trybu.")

    cam.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
