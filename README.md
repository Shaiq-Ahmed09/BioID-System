# BioID System: Facial Recognition Terminal

BioID System is a high-performance, cyberpunk-themed real-time facial recognition terminal built in Python. It utilizes **OpenCV's LBPH (Local Binary Patterns Histograms)** algorithm for texture-based biometric matching, wrapped inside a hardware-accelerated, high-DPI desktop interface powered by **CustomTkinter**.

Designed for low latency and high aesthetic appeal, the terminal features a live hacker-style log feed, predictive HUD targeting brackets, and automated scanning state lockdowns.

---

### Core Features
* **Texture-Based Biometrics:** Uses LBPH pattern matching to prioritize facial vectors, bypassing lighting and background noise interference.
* **Edge-to-Edge Zoom Engine:** A custom center-crop scaling matrix expands the live webcam preview to fill the canvas completely with zero black bezels.
* **Animated Cyberpunk HUD:** Integrated real-time typewriter log feeds alongside visual status flashers (Green for Access Granted, Red for Threat Alert).
* **Asynchronous Calculations:** Implements frame-skipping optimizations to isolate frame updates from data crunching, maintaining a stable frame rate.
* **Target Lock-On:** Freezes verification parameters immediately upon matching to secure the connection while keeping the tracking overlay pinned to your face.

---

### Setup & Launch

**1. Install Dependencies**
-bash
pip install opencv-contrib-python customtkinter pillow numpy

**2. Provision Database Profiles**
Create a known_faces directory and drop in an image named after the subject (e.g., lucky.png). The system dynamically handles filename string parsing to render names on the active HUD.

3. Boot System
python app.py

---

# Tech Stack
- Core Runtime: Python 3.x

- Computer Vision: OpenCV (cv2)

- UI Engine: CustomTkinter & PIL (Pillow)

- Data Vectors: NumPy

