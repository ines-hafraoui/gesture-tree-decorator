# Count to Decorate: Hand-Controlled Interactive Christmas Tree

Hand gesture / finger counting demo using MediaPipe and OpenCV.

## Quick Start

Clone the repo, create a virtual environment, install dependencies, and run:

```bash
git clone git@github.com:ines-hafraoui/gesture-tree-decorator.git 
cd Count-to-Decorate
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Notes:
- On macOS you may need to allow camera access for Terminal or your Python interpreter.

## Project Overview
Count to Decorate is an interactive application that lets users decorate a digital Christmas tree using hand-gesture commands detected through a webcam. By showing numbers with their fingers (1, 2, 3…), users can select digital ornaments and place them on the tree, creating a fun and seasonal Natural User Interface (NUI).

This project applies principles learned in Digital Image Processing, including:

- brightness/darkness adjustment
- blurring and sharpening
- mosaic effects
- histogram contrast stretching
- histogram equalization
- image composition

It also introduces computer vision techniques such as hand gesture recognition and real-time webcam processing.

## Team Members
|   Name   |    Year     |     Role    |
|   Juyeon Lee (이주연) |   4th year |  Hand Gesture Team • Team Leader |
|   Ines Hafraoui   |	4th year (France)   |	GUI Team    |
|   Minseo Cho (조민서)	|   3rd year	|	GUI Team    |
|   Sowon Kim (김소원)  |   3rd year    |   Hand Gesture Team   |

## Introduction

The goal of this project is to create an intuitive, joyful, and seasonal interaction experience where users can decorate a digital Christmas tree without touching a keyboard or mouse. Instead, they simply use their hands.

By combining image processing techniques with a hand-gesture-based interface, we aim to provide:
- a creative form of visual interaction
- a demonstration of real-time computer vision
- a playful holiday-themed application

### Why Hand Gesture Interaction?

We chose hand gesture recognition for several reasons:

- Natural User Interface (NUI)
Gestures are intuitive and direct — users interact with digital content the same way they interact with the real world.
- Immersive Experience
Decorating a tree with your hands feels more playful and engaging than clicking with a mouse.
- No Special Hardware Needed
The system works with a standard webcam, making it accessible and easy to set up.
- Practical Educational Value
Hand-gesture detection allows us to apply and understand:
    
    - image thresholding
    - region segmentation
    - contour/area measurement
    - time-series gesture stability
    - real-time video processing

## System Overview
1. Hand Gesture Recognition
- Captures webcam frames.
- Segments the hand region (color-based or MediaPipe Hands).
- Computes the number of raised fingers.
- Interprets gestures as commands:


        1 → ornament 1
        2 → ornament 2
        3 → ornament 3
        etc.

2. Tree & Ornament Visualization
Renders a digital Christmas tree in a graphical window.
Displays available ornaments in a side menu.
Allows users to add, toggle, or remove ornaments.

Uses custom image processing (no OpenCV pre-built functions) such as:

- compositing via manual pixel blending
- brightness/contrast adjustments on ornaments
- mosaic or blur effects as visual decoration styles

3. Interaction Flow

    
        User opens the app.
        Clicks Start → webcam activates.
        The system waits for a recognized gesture.
        Recognized gesture selects the ornament.
        The ornament is applied to the tree.
        Additional gestures can remove/change decorations.

## Survey
Types of User Interaction:

- Command-Based Interfaces
CLI, keyboard shortcuts, menu selections.

- Touch-Based Interfaces
Touchscreens, stylus input.

- Natural User Interfaces (NUI)
Voice, hand gesture recognition → our project belongs here.

- Immersive Interfaces
VR, AR, multi-modal interaction.

### Related Works

Gesture-controlled installations such as
Aurora Borealis – Interactive Light Installation
(gesture-based environmental control)

These works show how touchless interaction can improve immersion in artistic or entertainment-oriented systems.

## Tools & Libraries
#### Computer Vision : 
OpenCV – for webcam capture, drawing utilities
MediaPipe Hands – gesture detection model

#### Graphics / UI

Qt (PyQt6 or PySide6 for Python)
or
Tkinter (simpler, but less polished)

#### Multithreading (if needed)
threading / multiprocessing (Python)

#### Hardware
Standard webcam
Laptop or desktop computer (Windows or Linux)
