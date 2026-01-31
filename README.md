# Physio-2: Physiotherapy Movement Analysis

This repository contains a Python-based system for analyzing physiotherapy exercises using MediaPipe pose landmarks. It supports real-time validation, feedback, and scoring for safe exercise performance with phase awareness and advanced analytics.

## Features

### Core Features
- **Exercise Definitions** (`physio_exercises.py`): Defines three physiotherapy exercises (Arm Raise, Shoulder Rotation, Elbow Flexion) with safe angle ranges and angle calculation functions.
- **Exercise Router** (`exercise_router.py`): Allows selection of exercises and validates movements against safe ranges.
- **Real-Time Feedback** (`realtime_feedback.py`): Generates corrective text feedback per frame based on angle deviations.

### Advanced Features (NEW)
- **Phase-Aware Feedback** (`realtime_feedback.py`): Detects exercise phases (RAISE, HOLD, LOWER, NEUTRAL) and provides phase-specific guidance.
- **Safety Escalation** (`session_scoring.py`): Runtime safety violation detection with escalating alerts (CAUTION → WARNING → HIGH WARNING → CRITICAL).
- **Live Observability** (`webcam_demo.py`): Real-time angle visualization on video feed with FPS, frame count, and timestamp display.

## Phase-Aware Feedback System

The system now detects the current phase of exercise movement:

| Phase | Description | Feedback Example |
|-------|-------------|------------------|
| RAISE | Moving into position | "Continue raising arm" |
| HOLD | Maintaining position | "Hold position (15 frames)" |
| LOWER | Returning to neutral | "Continue lowering slowly" |
| NEUTRAL | Rest position | - |

## Safety Escalation Levels

| Level | Name | Criteria | Visual Alert |
|-------|------|----------|--------------|
| 0 | SAFE | All angles in safe range | Green status bar |
| 1 | CAUTION | Minor deviation for 10+ frames | Orange status bar |
| 2 | WARNING | Moderate deviation for 5+ frames | Red status bar |
| 3 | HIGH WARNING | Significant deviation for 3+ frames | Dark red status bar |
| 4 | CRITICAL | Immediate severe violation | Black status bar |

## Installation

Ensure Python 3.x is installed. Install required dependencies:

```bash
pip install mediapipe opencv-python numpy
```

## Usage

### Console Demo (Simulated)

```bash
python demo.py
```

The console demo now includes:
- Phase progression simulation
- Safety violation detection
- Phase-aware feedback logging
- Session summary with safety statistics

### Real-Time Webcam Demo

```bash
python webcam_demo.py
```

The webcam demo now provides:
- **Live Angle Visualization**: Real-time angle values displayed on video
- **Phase Indicator**: Current exercise phase with hold counter
- **Safety Warning Bar**: Color-coded warning at top of screen
- **Live Observability**: FPS, frame count, and timestamp
- **Key Controls**: 'q' to quit, 's' for session summary

### Controls (Webcam Mode)
- `q` - Quit the demo
- `s` - Show session summary

## Files

| File | Description | New Features |
|------|-------------|--------------|
| `physio_exercises.py` | Core exercise and angle calculation logic | - |
| `exercise_router.py` | Exercise selection and validation | - |
| `realtime_feedback.py` | Feedback generation | **Phase detection, phase-specific feedback** |
| `session_scoring.py` | Session scoring | **Safety escalation, violation tracking** |
| `demo.py` | Console demo with simulation | **Phase simulation, safety logging** |
| `webcam_demo.py` | Real-time webcam demo | **Live visualization, safety alerts, phase indicators** |
| `README.md` | This file | **Updated documentation** |

## API Reference

### PhaseDetector Class

```python
from realtime_feedback import PhaseDetector

detector = PhaseDetector("arm_raise")
phase = detector.detect_phase(angle_value, frame_count)
phase_info = detector.get_phase_info()
# Returns: {"phase": "RAISE", "hold_frames": 5, "phase_duration": 5}
```

### SessionScorer Class (Enhanced)

```python
from session_scoring import SessionScorer

scorer = SessionScorer("arm_raise")
scorer.add_frame(angles, validations, angle_ranges)
safety_status = scorer.get_safety_status()
# Returns: {"warning_level": 0, "warning_text": "SAFE", "is_safe": True, "recent_violations": []}

summary = scorer.get_summary()
# Returns: {"exercise": "arm_raise", "score": 85.5, "safety": {...}}
```

### generate_feedback Function (Enhanced)

```python
from realtime_feedback import generate_feedback

feedbacks = generate_feedback("arm_raise", landmarks, phase_info)
# Returns: ["[RAISE] Continue raising arm", "Good form"]
```

## Testing

### Console Demo
```bash
python demo.py
# Enter: arm_raise
# Enter: 50 (frames)
```

### Webcam Demo
```bash
python webcam_demo.py
# Select: arm_raise
# Perform exercise in front of camera
# Press 's' to see session summary
# Press 'q' to quit
```

## Exercise Angle Ranges

| Exercise | Angle | Safe Range | Description |
|----------|-------|------------|-------------|
| Arm Raise | shoulder_abduction | 0-180° | Arm elevation from body |
| Arm Raise | elbow_flexion | 0-10° | Keep elbow straight |
| Shoulder Rotation | shoulder_internal_rotation | 0-70° | Internal rotation range |
| Shoulder Rotation | shoulder_external_rotation | 0-90° | External rotation range |
| Elbow Flexion | elbow_flexion | 0-150° | Elbow bending range |

## Architecture

```
Physio-2/
├── physio_exercises.py    # Angle calculations & exercise definitions
├── exercise_router.py     # Exercise selection & validation
├── realtime_feedback.py   # Phase detection & feedback generation
├── session_scoring.py     # Scoring & safety escalation
├── demo.py               # Console demo (simulated)
├── webcam_demo.py        # Webcam demo (live)
└── README.md            # Documentation
```

## Version History

- v2.0: Added phase-aware feedback and safety escalation
- v1.0: Initial release with basic angle validation

## License

Submitted via Task Bank as per guidelines.
