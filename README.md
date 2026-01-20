# Physio-2: Physiotherapy Movement Analysis

This repository contains a Python-based system for analyzing physiotherapy exercises using MediaPipe pose landmarks. It supports real-time validation, feedback, and scoring for safe exercise performance.

## Features

- **Exercise Definitions** (`physio_exercises.py`): Defines three physiotherapy exercises (Arm Raise, Shoulder Rotation, Elbow Flexion) with safe angle ranges and angle calculation functions.
- **Exercise Router** (`exercise_router.py`): Allows selection of exercises and validates movements against safe ranges.
- **Real-Time Feedback** (`realtime_feedback.py`): Generates corrective text feedback per frame based on angle deviations.
- **Session Scoring** (`session_scoring.py`): Tracks session scores based on consistency and completion quality.
- **Demo** (`demo.py`): Console-based demo that simulates exercise sessions with logging.

## Installation

Ensure Python 3.x is installed. Install required dependencies:

```bash
pip install mediapipe opencv-python
```

Note: MediaPipe is required for real pose detection, but the demo uses simulated data.

## Usage

Run the demo:

```bash
python demo.py
```

Select an exercise and observe the simulated session with logging.

## Files

- `physio_exercises.py`: Core exercise and angle calculation logic.
- `exercise_router.py`: Exercise selection and validation.
- `realtime_feedback.py`: Feedback generation.
- `session_scoring.py`: Session scoring.
- `demo.py`: Console demo.
- `.gitignore`: Ignores cache files.
- `README.md`: This file.

## Testing

The system has been tested with simulated data. For real-world testing, integrate with webcam using MediaPipe.

## Submission

Submitted via Task Bank as per guidelines.