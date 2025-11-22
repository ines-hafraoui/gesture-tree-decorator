import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


# Count fingers from hand landmarks
def count_fingers(hand_landmarks, hand_label=None):
    lm = hand_landmarks.landmark
    count = 0

    # Thumb: comparison direction differs for left/right hands
    # MediaPipe handedness label is 'Left' or 'Right'
    if hand_label is None:
        if lm[4].x > lm[3].x:
            count += 1
    else:
        if hand_label == 'Right':
            # Right hand: thumb tip x less than IP joint x when extended
            if lm[4].x < lm[3].x:
                count += 1
        else:
            # Left hand: thumb tip x greater than IP joint x when extended
            if lm[4].x > lm[3].x:
                count += 1

    # if TIP.y < PIP.y, the finger is extended.
    finger_tips = [8, 12, 16, 20]
    for tip_id in finger_tips:
        if lm[tip_id].y < lm[tip_id - 2].y:
            count += 1

    return count


class HandGesture:
    def __init__(self):
        self.hands = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def process(self, frame):
        """
        Process frame and return detected finger count (int) and frame
        with drawn hand landmarks.
        """
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        finger_count = 0

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )
                
                hand_label = None
                if results.multi_handedness and len(results.multi_handedness) > idx:
                    hand_label = results.multi_handedness[idx].classification[0].label

                finger_count = count_fingers(hand_landmarks, hand_label)

        return finger_count, frame
