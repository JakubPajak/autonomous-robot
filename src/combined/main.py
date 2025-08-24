from acquire_frame import FrameStream
from process_frame_nn import NNProcessFrame
from process_frame_rgb import LaneDetector
from process_frame_bin import ProcessFrameBin
import cv2 as cv
import time

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
    print("2 - Lane Detection mode (binarized):")
    print("3 - YOLOv8 NN Detection")
    mode = input("Your choice [1/2]: ").strip()

    if mode == "1":
        detector = LaneDetector()
    if mode == "2":
        detector = ProcessFrameBin()
    if mode == "3":
        detector = NNProcessFrame(model_path="/workspace/src/best.pt")

    with open(f'output_{mode}.txt', 'w') as output:
        index = 0
        while True:
            frame = stream.get_frame()
            processed = frame
            if frame is None:
                break
            
            start_time = time.time()
            if mode == "1":
                processed , _, _= detector.process(frame)
            if mode == "2":
                processed, _, _ = detector.process(frame)
            if mode == "3": 
                processed, _ = detector.process(frame)


            end_time = time.time()
            duration = end_time - start_time
            output.write(f'{index},{duration}\n')
            # print(f"Detection status: {status}\n")
            cv.imshow("Detection", resize_to_fhd(processed))
            cv.imshow("Default image", resize_to_fhd(frame))
            
            index = index + 1
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
