'''
Gesture Control System for Mouse Scrolling and Media Volume
- Uses ultrasonic distance sensor for gesture recognition
- Uses IR button for mode switching and tap actions
'''
import serial
import pyautogui
import time
from collections import deque

pyautogui.PAUSE = 0.0 # zero delay for instant responsiveness

PORT = 'COM12' # change to your Arduino's serial port
BAUD_RATE = 115200 

COOLDOWN = 0.05
TAP_THRESHOLD = 0.4 
HOLD_THRESHOLD = 1.5 

SCROLL_STRENGTH = 25 # 
VOLUME_STEPS = 2

MID_ZONE = 14.0
DEADZONE = 3.0 # deadzone for stable scrolling/volume control
MAX_DIST = 45.0 # maximum distance to consider for gestures


mode = "mouse"
ir_pressed_time = None
mode_switched = False
last_action_time = 0
local_volume = 50

raw_history = deque(maxlen=5)

# LCD state tracking to minimize lcd spam and ensure smooth updates
last_lcd_message = ""
last_lcd_update = 0

event_expire_time = 0
persistent_line2 = "Ready..." 

LCD_COOLDOWN = 0.4
EVENT_DISPLAY_TIME = 1.5

# Initialization 
print(f"Initializing Gesture Control System [{mode.upper()} MODE]")

try:
    arduino = serial.Serial(PORT, BAUD_RATE, timeout=1)
    time.sleep(2)

    print("✅ Hardware Serial Connection Established!")

except Exception as e:
    print(f"❌ Serial Connection Failed: {e}")
    exit()


# LCD COMMUNICATION 
def send_lcd(line1, line2, force=False):

    global last_lcd_message
    global last_lcd_update

    now = time.time()

    message = f"{line1}|{line2}"

    # Prevent unnecessary LCD spam
    if not force:
        # Skip duplicate updates
        if message == last_lcd_message:
            return
        # Enforce cooldown between updates to prevent flickering
        if now - last_lcd_update < LCD_COOLDOWN:
            return
    try:
        arduino.write((message + "\n").encode())
        last_lcd_message = message
        last_lcd_update = now
    except:
        pass

# Event display helper
def show_event(line2):
    global event_expire_time
    send_lcd(
        f"{mode.upper()} MODE",
        line2
    )

    event_expire_time = time.time() + EVENT_DISPLAY_TIME

# basic median filter for distance readings to smooth out noise
def process_filtered_distance(val):

    if val <= 1.5 or val >= 200.0:
        return 999.0
    raw_history.append(val)

    sorted_history = sorted(list(raw_history)) 
    return sorted_history[len(sorted_history) // 2] # return median value


# Initial boot screen
send_lcd(
    "GESTURE CTRL",
    "System Ready",
    force=True
)

time.sleep(2)

send_lcd(
    f"{mode.upper()} MODE",
    persistent_line2,
    force=True
)

# ----------------------- MAIN LOOP ---------------------------
while True:
    try:
         # Restore default LCD line if no event is active
        if time.time() > event_expire_time:
            desired_message = f"{mode.upper()} MODE|{persistent_line2}"
            if last_lcd_message != desired_message:
                send_lcd(
                    f"{mode.upper()} MODE",
                    persistent_line2
                )

        # Read serial data 
        if arduino.in_waiting > 0:

            data = arduino.readline().decode('utf-8').strip()
            if not data or "," not in data:
                continue

            parts = data.split(",")

            if len(parts) != 2:
                continue

            raw_dist, raw_ir = parts
            dist = process_filtered_distance(float(raw_dist))

            ir = int(raw_ir)
            now = time.time()
            action = "IDLE"

            # IR button handling 
            if ir == 1:

                if ir_pressed_time is None:
                    ir_pressed_time = now
                    mode_switched = False

                duration = now - ir_pressed_time

                # Mode switch - Hold for HOLD_THRESHOLD sec to switch modes
                if duration >= HOLD_THRESHOLD and not mode_switched:
                    mode = "media" if mode == "mouse" else "mouse"
                    print(f"\n🔁 MODE SWITCHED → {mode.upper()}\n")
                    show_event("MODE CHANGED")
                    mode_switched = True

            else:
                if ir_pressed_time is not None:
                    duration = now - ir_pressed_time
                    # TAP ACTION
                    if duration < TAP_THRESHOLD and not mode_switched:
                        if mode == "mouse":
                            pyautogui.click()
                            action = "MOUSE CLICK"
                            show_event("CLICK")

                        else:
                            pyautogui.press("playpause")
                            action = "MEDIA PLAY/PAUSE"
                            show_event("PLAY/PAUSE")

                    ir_pressed_time = None
                    mode_switched = False

            # Ultrasonic gesture handling
            if dist <= MAX_DIST:

                if now - last_action_time > COOLDOWN:

                    # Near distance behavior
                    if dist < (MID_ZONE - DEADZONE):

                        if mode == "mouse":
                            pyautogui.scroll(-SCROLL_STRENGTH)
                            action = f"SCROLL DOWN ({dist:.1f}cm)"
                            show_event("SCROLL DOWN")

                        else:
                            pyautogui.press("volumedown")
                            action = "VOLUME DOWN"
                            show_event("VOL DOWN")

                    # Far distance behavior
                    elif dist > (MID_ZONE + DEADZONE):

                        if mode == "mouse":
                            pyautogui.scroll(SCROLL_STRENGTH)
                            action = "SCROLL UP"
                            show_event("SCROLL UP")
                        else:
                            pyautogui.press("volumeup")
                            action = "VOLUME UP"
                            show_event("VOL UP")
                    else:

                        action = f"NEUTRAL DEADZONE ({dist:.1f}cm)"
                    last_action_time = now
            else:

                if action == "IDLE" and len(raw_history) > 0:
                    raw_history.clear() # remove old readings when hand is removed to prevent jumps during next gesture

            # Debug console output if there's an IR event or any action taken
            if ir == 1 or action != "IDLE":

                print(
                    f"Mode: {mode.upper():5s} | "
                    f"Dist: {dist:5.1f}cm | "
                    f"IR: {ir} | "
                    f"Action: {action}"
                )

    except KeyboardInterrupt:
        print("\n interrupted, exiting...")
        break

    except Exception:
        continue