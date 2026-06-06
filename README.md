# Hand Gesture–Controlled Multi-Mode Interface
### Arduino + Python | Non-Contact PC Control via Ultrasonic Sensing

Control your computer without touching it. This project maps physical hand gestures to real-time OS actions — scrolling and media volume — using an ultrasonic distance sensor, an IR button, and a Python script running on Windows.

---

## Demo

https://github.com/user-attachments/assets/1ced3061-bd4a-4bc3-8a9e-3e68e884c8e8

---

## How It Works

An Arduino Uno reads distance from an HC-SR04 ultrasonic sensor and sends the data over serial to a Python script at 115200 baud. The Python script processes the readings and fires OS-level actions using PyAutoGUI.

Two modes, one IR button:
- **Tap** (< 0.4s) → Mouse click or Play/Pause
- **Hold** (≥ 1.5s) → Switch between Mouse Mode and Media Mode

Distance-based gestures:
- **Hand close** (< 11cm) → Scroll down / Volume down
- **Hand far** (> 17cm) → Scroll up / Volume up
- **11–17cm neutral zone** → No action (deadzone)

A 16x2 I2C LCD displays the current mode and active gesture in real time.

---

## Hardware

| Component | Details |
|---|---|
| Microcontroller | Arduino Uno (ATmega328P) |
| Distance Sensor | HC-SR04 Ultrasonic Module |
| Input | Active Infrared (IR) Sensor |
| Display | 16x2 LCD with I2C backpack (0x27) |

### Wiring

![Circuit Diagram](assets/circuit_diagram.png)

---

## Software

- **Python 3.x**
  - `pyserial` — serial communication with Arduino
  - `pyautogui` — OS-level mouse, scroll, and media key control
- **Arduino C++**
  - `Wire.h` + `LiquidCrystal_I2C.h` — I2C LCD control

---

## Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/rhthm/gesture-controlled-interface.git
cd gesture-controlled-interface
```

### 2. Install Python dependencies
```bash
pip install pyserial pyautogui
```

### 3. Flash the Arduino
- Open `gesture_controller/gesture_controller.ino` in the Arduino IDE
- Select **Arduino Uno** and the correct COM port
- Upload the sketch

### 4. Configure the COM port
In `main.py`, update line 13:
```python
PORT = 'COM12'  # change to your Arduino's serial port
```
To find your port: Device Manager → Ports (COM & LPT)

### 5. Run the Python script
```bash
python main.py
```

---

## Signal Stability — What Actually Went Into This

Getting gestures to work was straightforward. Getting them to feel stable took most of the time.

- **Median filter on raw sensor data** — spikes get ignored, not averaged in
- **3cm deadzone around the midpoint** — prevents the hand from constantly fighting the threshold between directions
- **Buffer clears on hand exit** — stale readings don't bleed into the next gesture
- **LCD state tracking** — display only writes when the message actually changes, no redundant serial writes

---

## Use Cases

- Hands-free scrolling while eating, cooking, or reading
- Media control from a distance
- Accessibility — reduced reliance on physical input devices
- Hygiene-critical environments where touchless control matters

---

## Project Structure
```
gesture-control-interface/
├── README.md
├── gesture_controller/
│   └── gesture_controller.ino
├── main.py
└── assets/
    ├── circuit_diagram.png
    ├── demo.mp4
    ├── hardware_closeup.jpg
    └── setup.jpg
```

---

## License

MIT — free to use, modify, and distribute. See [LICENSE](LICENSE) for details.

---

*Built by [rhthm](https://github.com/rhthm)*
