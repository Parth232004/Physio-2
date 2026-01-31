# demo.py
# Console-based demo for physiotherapy exercises with logging
# Now includes phase-aware feedback and safety escalation

import time
import random
from physio_exercises import EXERCISES, get_shoulder_abduction_angle, get_elbow_flexion_angle, get_shoulder_rotation_angle
from exercise_router import validate_movement
from realtime_feedback import generate_feedback, PhaseDetector
from session_scoring import SessionScorer

def simulate_landmarks(base_angles):
    """
    Simulate landmarks with some variation.

    :param base_angles: Dict of base angles
    :return: Mock landmarks dict
    """
    # Mock landmarks as dict for simplicity, in real use it's MediaPipe objects
    # But for demo, we'll calculate angles directly
    return {
        "shoulder_abduction": base_angles.get("shoulder_abduction", 90) + random.uniform(-10, 10),
        "elbow_flexion": base_angles.get("elbow_flexion", 10) + random.uniform(-5, 5),
        "shoulder_internal": base_angles.get("shoulder_internal", 20) + random.uniform(-5, 5),
        "shoulder_external": base_angles.get("shoulder_external", 30) + random.uniform(-5, 5)
    }


def run_demo(exercise_name, num_frames=50):
    """
    Run a demo session for the exercise with phase-aware feedback.
    
    :param exercise_name: Name of the exercise
    :param num_frames: Number of frames to simulate
    """
    exercise = EXERCISES.get(exercise_name.lower())
    if not exercise:
        print("Invalid exercise")
        return

    scorer = SessionScorer(exercise_name)
    phase_detector = PhaseDetector(exercise_name)
    
    print(f"\n{'='*60}")
    print(f"PHYSIO INTELLIGENCE DEMO - {exercise.name.upper()}")
    print(f"{'='*60}")
    print(f"Description: {exercise.description}")
    print(f"Frames to simulate: {num_frames}")
    print(f"Features: Phase-aware feedback, Safety escalation, Live observability")
    print(f"{'='*60}\n")

    # Simulate movement phases
    phase_sequence = ["RAISE", "HOLD", "LOWER", "NEUTRAL"]
    current_phase_index = 0
    frames_in_phase = 0
    phase_target_frames = {"RAISE": 10, "HOLD": 15, "LOWER": 10, "NEUTRAL": 15}
    
    for frame in range(num_frames):
        timestamp = time.time()
        
        # Simulate phase progression
        phase = phase_sequence[current_phase_index]
        frames_in_phase += 1
        
        if frames_in_phase >= phase_target_frames.get(phase, 10):
            current_phase_index = (current_phase_index + 1) % len(phase_sequence)
            frames_in_phase = 0
        
        # Generate target angles based on phase
        if exercise_name == "arm_raise":
            if phase == "RAISE":
                base = {"shoulder_abduction": 45 + frames_in_phase * 8, "elbow_flexion": 10}
            elif phase == "HOLD":
                base = {"shoulder_abduction": 125, "elbow_flexion": 10}
            elif phase == "LOWER":
                base = {"shoulder_abduction": 125 - frames_in_phase * 10, "elbow_flexion": 10}
            else:  # NEUTRAL
                base = {"shoulder_abduction": 15, "elbow_flexion": 10}
        elif exercise_name == "shoulder_rotation":
            if phase == "RAISE":
                base = {"shoulder_internal": frames_in_phase * 6, "shoulder_external": 10}
            elif phase == "HOLD":
                base = {"shoulder_internal": 60, "shoulder_external": 10}
            elif phase == "LOWER":
                base = {"shoulder_internal": 60 - frames_in_phase * 5, "shoulder_external": 10}
            else:
                base = {"shoulder_internal": 10, "shoulder_external": 10}
        else:  # elbow_flexion
            if phase == "RAISE":
                base = {"elbow_flexion": 30 + frames_in_phase * 10}
            elif phase == "HOLD":
                base = {"elbow_flexion": 130}
            elif phase == "LOWER":
                base = {"elbow_flexion": 130 - frames_in_phase * 10}
            else:
                base = {"elbow_flexion": 20}

        # Add some variation
        simulated_angles = {}
        for angle_name, value in base.items():
            variation = random.uniform(-5, 5)
            simulated_angles[angle_name] = value + variation

        # Mock validations
        validations = {}
        for angle_name, value in simulated_angles.items():
            if angle_name in exercise.angle_ranges:
                min_a, max_a = exercise.angle_ranges[angle_name]
                validations[angle_name] = min_a <= value <= max_a
        
        # Get phase info
        primary_angle = simulated_angles.get("shoulder_abduction") or simulated_angles.get("elbow_flexion") or 0
        phase_info = phase_detector.detect_phase(primary_angle, frame)
        
        # Generate phase-aware feedback (simulated landmarks for demo)
        # In real use, we'd have actual MediaPipe landmarks
        mock_landmarks = type('obj', (object,), {
            '11': type('obj', (object,), {'x': 0.5, 'y': 0.3})(),  # left_shoulder
            '12': type('obj', (object,), {'x': 0.6, 'y': 0.3})(),  # right_shoulder
            '13': type('obj', (object,), {'x': 0.7, 'y': 0.4})(),  # left_elbow
            '14': type('obj', (object,), {'x': 0.7, 'y': 0.5})(),  # right_elbow
            '16': type('obj', (object,), {'x': 0.8, 'y': 0.6})(),  # right_wrist
            '23': type('obj', (object,), {'x': 0.5, 'y': 0.7})(),  # left_hip
            '24': type('obj', (object,), {'x': 0.6, 'y': 0.7})(),  # right_hip
        })()
        
        feedbacks = generate_feedback(exercise_name, mock_landmarks, phase_info)
        
        # Add phase-specific feedback
        phase_feedback = f"[{phase_info['phase']}] Phase: {phase}, Hold: {phase_info['hold_frames']} frames"
        
        # Log entry
        log_entry = {
            "frame": frame + 1,
            "timestamp": timestamp,
            "phase": phase_info["phase"],
            "angles": simulated_angles,
            "feedbacks": feedbacks,
            "safe": all(validations.values())
        }
        
        # Print log
        safety_indicator = "✓" if all(validations.values()) else "⚠"
        print(f"[{frame+1:3d}] {safety_indicator} Phase: {phase_info['phase']:6s} | Angles: {simulated_angles} | Feedback: {feedbacks[0] if feedbacks else 'None'}")
        
        # Add to scorer
        scorer.add_frame(simulated_angles, validations, exercise.angle_ranges)
        
        time.sleep(0.05)  # Simulate frame rate

    # Final score
    print(f"\n{'='*60}")
    print("FINAL SESSION SUMMARY")
    print("="*60)
    summary = scorer.get_summary()
    print(f"Exercise: {summary['exercise']}")
    print(f"Total Frames: {summary['total_frames']}")
    print(f"Safe Frames: {summary['safe_frames']}")
    print(f"Score: {summary['score']}/100")
    print(f"\nSafety Violations:")
    safety = summary['safety']
    print(f"  - Total: {safety['total_violations']}")
    print(f"  - By Severity: {safety['by_severity']}")
    print(f"  - Escalation Events: {safety['escalation_events']}")
    print(f"  - Highest Warning Level: {safety['highest_warning_level']}")
    print(f"{'='*60}")


if __name__ == "__main__":
    print("Physio Intelligence Demo - Console Version")
    print("Features: Phase-aware feedback, Safety escalation, Live observability")
    print()
    
    exercise = input("Enter exercise (arm_raise, shoulder_rotation, elbow_flexion): ").strip()
    frames = input("Number of frames (default 50): ").strip()
    num_frames = int(frames) if frames else 50
    
    run_demo(exercise, num_frames)
