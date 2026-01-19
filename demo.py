# demo.py
# Console-based demo for physiotherapy exercises with logging

import time
import random
from physio_exercises import EXERCISES, get_shoulder_abduction_angle, get_elbow_flexion_angle, get_shoulder_rotation_angle
from exercise_router import validate_movement
from realtime_feedback import generate_feedback
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

def run_demo(exercise_name, num_frames=10):
    """
    Run a demo session for the exercise.

    :param exercise_name: Name of the exercise
    :param num_frames: Number of frames to simulate
    """
    exercise = EXERCISES.get(exercise_name.lower())
    if not exercise:
        print("Invalid exercise")
        return

    scorer = SessionScorer(exercise_name)

    print(f"Starting demo for {exercise.name}")
    print("Logging: angles, corrections, timestamps")

    for frame in range(num_frames):
        timestamp = time.time()

        # Simulate angles
        if exercise_name == "arm_raise":
            base = {"shoulder_abduction": 90, "elbow_flexion": 10}
        elif exercise_name == "shoulder_rotation":
            base = {"shoulder_internal": 20, "shoulder_external": 30}
        else:
            base = {"elbow_flexion": 90}

        simulated_angles = simulate_landmarks(base)

        # Mock validations (in real use, calculate properly)
        validations = {}
        for angle_name, value in simulated_angles.items():
            if angle_name in exercise.angle_ranges:
                min_a, max_a = exercise.angle_ranges[angle_name]
                validations[angle_name] = min_a <= value <= max_a

        # Mock corrections for demo
        corrections = ["Good form"] if all(validations.values()) else ["Adjust position"]

        # Log
        log_entry = {
            "timestamp": timestamp,
            "angles": simulated_angles,
            "corrections": corrections
        }
        print(f"Frame {frame+1}: {log_entry}")

        # Add to scorer
        scorer.add_frame(simulated_angles, validations)

        time.sleep(0.1)  # Simulate frame rate

    # Final score
    summary = scorer.get_summary()
    print(f"Session Summary: {summary}")

if __name__ == "__main__":
    exercise = input("Enter exercise (arm_raise, shoulder_rotation, elbow_flexion): ").strip()
    run_demo(exercise)