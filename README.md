# HandGestureKeyboard

A **Virtual Keyboard** controlled by hand gestures using webcam, powered by [MediaPipe](https://google.github.io/mediapipe/) and [OpenCV](https://opencv.org/).

## Features

- Detect hand using MediaPipe’s hand tracking solution.
- Simulate keyboard input via finger gestures and hand position.
- Visual keyboard GUI displayed on webcam feed.
- Support for upper/lower case, space, delete, and clear functions.
- Touchless typing: no need to press any physical key.

## How it works

1. Turn on webcam.
2. Move hand over the virtual keys displayed.
3. Tap fingers or perform specific gestures to “click” keys.

## Installation

```bash
pip install opencv-python mediapipe pynput cvzone
```

## Usage

```bash
python keyboard.py
```


## Project Structure

```plaintext
HandGestureKeyboard/
├── handTrackingModule.py  # Handles hand detection and finger tracking
├── keyboard.py            # Main virtual keyboard functionality
├── README.md              # Project documentation
```



## Reference

- [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html)
- [OpenCV](https://opencv.org/)
- [cvzone](https://www.cvzone.com/)
- [pynput](https://pypi.org/project/pynput/)