from acquire_frame import FrameStream
from process_frame_nn import NNProcessFrame
from process_frame_rgb import LaneDetector
import cv2 as cv

def main():
    print("Choose the source of the data")
    print("1 - Live Video")
    print("2 - Photos")
    source = input("Your choice [1/2]: ").strip()

    if source == "1":
        stream = FrameStream(camera_id=0)
    else:
        stream = FrameStream(camera_id=None,folder_path="/workspace/test-photos")

    print("Choose detection mode:")
    print("1 - Lane Detection")
    print("2 - YOLOv8 NN Detection")
    mode = input("Your choice [1/2]: ").strip()

    if mode == "1":
        detector = LaneDetector()
    else:
        detector = NNProcessFrame(model_path="/workspace/src/best.pt")

    while True:
        frame = stream.get_frame()
        if frame is None:
            break

        processed , _= detector.process(frame)
        # print(f"Detection status: {status}\n")
        cv.imshow("Detection", resize_to_fhd(processed))
        cv.imshow("Default image", resize_to_fhd(frame))
        if cv.waitKey(5500 if source == "2" else 1) & 0xFF == ord('q'):  
            break

    stream.release()
    cv.destroyAllWindows()

def resize_to_fhd(frame, max_width=1920, max_height=1080):
    h, w = frame.shape[:2]
    if w > max_width or h > max_height:
        scale = min(max_width / w, max_height / h)
        new_size_w = int(w * scale)
        new_size_h = int(h * scale)
        frame = cv.resize(frame, (new_size_w, new_size_h))
    return frame


if __name__ == "__main__":
    main()
