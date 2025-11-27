import cv2
from app.vision.camera_thread import CameraThread
from app.vision.hand_detector import HandGesture  # or wherever you put it

# Initialize camera and hand detector
cam = CameraThread(0)
detector = HandGesture()

cam.start()

while True:
    frame = cam.read_frame()
    if frame is None:
        continue

    finger_count, annotated, tip = detector.process(frame)

    # Draw fingertip marker if detected
    if tip is not None:
        cv2.circle(annotated, tip, 10, (0, 0, 255), -1)
        cv2.putText(annotated, f"Tip: {tip}", (tip[0]+10, tip[1]), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # Show finger count
    cv2.putText(annotated, f"Fingers: {finger_count}", (10,30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

    cv2.imshow("Hand Test", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.stop()
cam.release()
cv2.destroyAllWindows()
