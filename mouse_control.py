import cv2
import mediapipe as mp
import pyautogui
from control_panel import GestureControlPanel
from threading import Thread


def click_copy():
    pyautogui.hotkey("ctrl", "c")


def click_paste():
    pyautogui.hotkey("ctrl", "v")


def click_undo():
    pyautogui.hotkey("ctrl", "z")


def click_redo():
    pyautogui.hotkey("ctrl", "y")


def click_go_back():
    pyautogui.hotkey("alt", "left")


def click_go_forward():
    pyautogui.hotkey("alt", "right")


"""def do_custom_function(keys):
    if keys is None or keys == "":
        pass  # do nothing
    else:
        try:
            key_seq = keys.replace(" ", "").lower().split("+")
            pyautogui.hotkey(*key_seq)
        except:
            print("Custom function incapable")"""


def show_command(img, command, font, y, color):
    cv2.putText(
        img,
        command,
        (10, y),
        font,
        3,
        color,
        2,
        cv2.LINE_AA,
    )


"""left_tasks = [
    "copy",
    "paste",
    "undo",
    "redo",
    "go back",
    "go forward",
]"""

function_map = {
    "copy": click_copy,
    "paste": click_paste,
    "undo": click_undo,
    "redo": click_redo,
    "go back": click_go_back,
    "go forward": click_go_forward,
}


control_panel = GestureControlPanel()


def run_camera():
    # Precaution
    pyautogui.FAILSAFE = True

    # Remember actions
    is_dragging = False
    has_clicked = False

    # Create hands object
    mediapipe_hands = mp.solutions.hands
    hands = mediapipe_hands.Hands()
    mediapipe_draw = mp.solutions.drawing_utils

    captured = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    screen_width, screen_height = pyautogui.size()

    # Smoothing
    p_x, p_y = 0, 0
    c_x, c_y = 0, 0

    while True:
        success, image = captured.read()
        if not success:
            continue

        image = cv2.flip(image, 0)
        image_bgr_to_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        processed_image = hands.process(image_bgr_to_rgb)

        # RIGHT HAND
        if processed_image.multi_hand_landmarks:
            for hand_index, right_hand_landmarks in enumerate(processed_image.multi_hand_landmarks):
                handedness = processed_image.multi_handedness[hand_index].classification[0].label
                if handedness != "Right":
                    continue
                # print(right_hand_landmarks)
                # Gathering fingertips
                hand_landmarks = right_hand_landmarks.landmark

                fingers_open = [False, False, False, False]
                thumb_open = False

                finger_tip_ids = [
                    mediapipe_hands.HandLandmark.THUMB_TIP,
                    mediapipe_hands.HandLandmark.INDEX_FINGER_TIP,
                    mediapipe_hands.HandLandmark.MIDDLE_FINGER_TIP,
                    mediapipe_hands.HandLandmark.RING_FINGER_TIP,
                    mediapipe_hands.HandLandmark.PINKY_TIP,
                ]
                finger_tips = [hand_landmarks[tip_id] for tip_id in finger_tip_ids]

                # THUMB
                """
                Checks if fingertip landmark's x is currently below x of a landmark indicating the middle of the
                finger if not then changes thumb's status to open
                """
                threshold = hand_landmarks[2].x
                if not hand_landmarks[3].x < threshold and hand_landmarks[4].x < threshold:
                    thumb_open = True

                # INDEX FINGER
                threshold = hand_landmarks[6].y
                if hand_landmarks[7].y < threshold and hand_landmarks[8].y < threshold:
                    fingers_open[0] = True

                # MIDDLE FINGER
                threshold = hand_landmarks[10].y
                if hand_landmarks[11].y < threshold and hand_landmarks[12].y < threshold:
                    fingers_open[1] = True

                # RING FINGER
                threshold = hand_landmarks[14].y
                if hand_landmarks[15].y < threshold and hand_landmarks[16].y < threshold:
                    fingers_open[2] = True

                # PINKY
                threshold = hand_landmarks[18].y
                if hand_landmarks[19].y < threshold and hand_landmarks[20].y < threshold:
                    fingers_open[3] = True

                # Gesture recognition
                # V-shape: Cursor-moving state
                if fingers_open == [1, 1, 0, 0]:  # Ignored thumb for anlge issue
                    if is_dragging:
                        pyautogui.mouseUp()
                        is_dragging = False
                    has_clicked = False  # Reset click state
                    x = int(finger_tips[1].x * screen_width)
                    y = int(finger_tips[1].y * screen_height)

                    # Smoothing formula
                    c_x = p_x + (x - p_x) / control_panel.smoothing
                    c_y = p_y + (y - p_y) / control_panel.smoothing

                    pyautogui.moveTo(c_x, c_y)
                    p_x, p_y = c_x, c_y
                    if control_panel.show_command:
                        show_command(image, "Moving", font, 70, (0, 0, 255))

                elif fingers_open == [1, 0, 0, 0] and not has_clicked:  # Only middle finger open: Left click
                    if is_dragging:
                        pyautogui.mouseUp()
                        is_dragging = False
                    pyautogui.click()
                    has_clicked = True  # Set click state to prevent multiple clicks
                    if control_panel.show_command:
                        show_command(image, "Left Click", font, 70, (0, 0, 255))

                elif fingers_open == [0, 1, 0, 0] and not has_clicked:  # Only index finger open: Right click
                    if is_dragging:
                        pyautogui.mouseUp()
                        is_dragging = False
                    pyautogui.rightClick()
                    has_clicked = True
                    if control_panel.show_command:
                        show_command(image, "Right Click", font, 70, (0, 0, 255))

                # Index finger closed: Scroll
                elif fingers_open == [0, 1, 1, 1]:
                    scroll_y = (
                            hand_landmarks[mediapipe_hands.HandLandmark.INDEX_FINGER_MCP].y
                            * screen_height
                    )
                    if scroll_y > screen_height / 2:
                        pyautogui.scroll(-120)  # Scroll down
                        if control_panel.show_command:
                            show_command(image, "Scroll Down", font, 70, (0, 0, 255))
                    else:
                        pyautogui.scroll(120)  # Scroll up
                        if control_panel.show_command:
                            show_command(image, "Scroll Up", font, 70, (0, 0, 255))

                # All closed: Drag
                elif fingers_open == [0, 0, 0, 0]:
                    if not is_dragging:
                        pyautogui.mouseDown()
                        is_dragging = True
                    x = int(finger_tips[1].x * screen_width)
                    y = int(finger_tips[1].y * screen_height)
                    pyautogui.moveTo(x, y)
                    has_clicked = False  # Reset click state
                    if control_panel.show_command:
                        show_command(image, "Drag", font, 70, (0, 0, 255))

                else:
                    if is_dragging:
                        pyautogui.mouseUp()
                        is_dragging = False
                    has_clicked = False

                if control_panel.debug:
                    # print("R:", thumb_open, fingers_open)
                    if control_panel.show_camera:
                        mediapipe_draw.draw_landmarks(
                            image, right_hand_landmarks, mediapipe_hands.HAND_CONNECTIONS
                        )

        if control_panel.show_camera:
            cv2.imshow("Hand Tracking", image)

        if not control_panel.show_camera and cv2.getWindowProperty("Hand Tracking", cv2.WND_PROP_VISIBLE):
            cv2.destroyWindow("Hand Tracking")

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        if not control_panel.is_running:
            break

    captured.release()
    cv2.destroyAllWindows()
    exit()


control_panel_thread = Thread(target=control_panel.run)
control_panel_thread.start()
run_camera()
control_panel_thread.join()
