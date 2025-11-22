import cv2
from vision.handgesture import HandGesture
import sys

print("Python:", sys.executable)
print("OpenCV:", cv2.__version__)

hg = HandGesture()

cap = None
for cam_idx in (0, 1, 2):
    print("Trying camera index", cam_idx)
    temp = cv2.VideoCapture(cam_idx)
    ret, frame = temp.read()
    print("ret:", ret, "frame:", None if frame is None else getattr(frame, "shape", None))
    if ret:
        cap = temp
        print("Using camera index", cam_idx)
        break
    temp.release()

if cap is None or not cap.isOpened():
    print("No camera available. Exiting.")
    sys.exit(1)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame read failed")
        break

    count, annotated = hg.process(frame)

    cv2.putText(
        annotated,
        f"Fingers: {count}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )

    cv2.imshow("Hand Gesture Test", annotated)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()