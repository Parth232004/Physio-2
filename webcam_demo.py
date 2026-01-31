# webcam_demo.py
# Real-time webcam demo for physiotherapy exercise validation
# Includes: live MediaPipe integration, phase-aware feedback, safety escalation, live observability

import cv2
import mediapipe as mp
import time
import numpy as np
from datetime import datetime

from physio_exercises import EXERCISES, get_shoulder_abduction_angle, get_elbow_flexion_angle, get_shoulder_rotation_angle
from realtime_feedback import generate_feedback, PhaseDetector
from session_scoring import SessionScorer

# MediaPipe setup
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


def draw_angle_on_frame(frame, angle_name, angle_value, position, is_safe, color=(0, 255, 0)):
    """
    Draw angle information on the video frame.
    
    :param frame: Video frame to draw on
    :param angle_name: Name of the angle
    :param angle_value: Current angle value
    :param position: (x, y) position for text
    :param is_safe: Whether angle is in safe range
    :param color: BGR color tuple
    """
    # Set color based on safety
    if is_safe:
        color = (0, 255, 0)  # Green
    elif angle_value < 0:  # Below minimum
        color = (0, 165, 255)  # Orange - need to increase
    else:  # Above maximum
        color = (0, 0, 255)  # Red - need to decrease
    
    # Draw angle value
    cv2.putText(
        frame, 
        f"{angle_name}: {angle_value:.1f}°", 
        position, 
        cv2.FONT_HERSHEY_SIMPLEX, 
        0.6, 
        color, 
        2
    )


def draw_safety_warning(frame, warning_text, warning_level):
    """
    Draw safety warning on frame with appropriate styling.
    
    :param frame: Video frame
    :param warning_text: Warning message
    :param warning_level: 0-4 (none to critical)
    """
    # Background color based on warning level
    if warning_level == 0:
        bg_color = (0, 100, 0)  # Dark green
    elif warning_level == 1:
        bg_color = (0, 165, 255)  # Orange
    elif warning_level == 2:
        bg_color = (0, 0, 255)  # Red
    elif warning_level == 3:
        bg_color = (0, 0, 150)  # Dark red
    else:
        bg_color = (0, 0, 0)  # Black for critical
    
    # Draw warning bar at top
    bar_height = 40
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], bar_height), bg_color, -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Draw warning text
    text_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
    text_x = (frame.shape[1] - text_size[0]) // 2
    text_y = (bar_height + text_size[1]) // 2
    
    # White text
    cv2.putText(frame, warning_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)


def draw_phase_indicator(frame, phase, hold_frames):
    """
    Draw current phase indicator on frame.
    
    :param frame: Video frame
    :param phase: Current phase (RAISE, HOLD, LOWER, NEUTRAL)
    :param hold_frames: Frames in hold phase
    """
    # Phase colors
    phase_colors = {
        "RAISE": (255, 165, 0),    # Orange
        "HOLD": (0, 255, 255),     # Cyan
        "LOWER": (147, 20, 255),   # Purple
        "NEUTRAL": (128, 128, 128) # Gray
    }
    
    color = phase_colors.get(phase, (128, 128, 128))
    
    # Draw phase indicator in corner
    cv2.putText(frame, f"Phase: {phase}", (10, frame.shape[0] - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    if phase == "HOLD":
        cv2.putText(frame, f"Hold: {hold_frames} frames", (10, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


def draw_live_observability(frame, angles, fps, frame_count):
    """
    Draw comprehensive live observability data on frame.
    
    :param frame: Video frame
    :param angles: Dict of angle names to values
    :param fps: Current FPS
    :param frame_count: Total frames processed
    """
    # Draw FPS and frame count
    cv2.putText(frame, f"FPS: {fps:.1f}", (frame.shape[1] - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Frame: {frame_count}", (frame.shape[1] - 120, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Draw timestamp
    timestamp = datetime.now().strftime("%H:%M:%S")
    cv2.putText(frame, timestamp, (frame.shape[1] - 120, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


def process_frame(frame, pose, exercise, scorer, phase_detector):
    """
    Process a single frame and return annotated frame with feedback.
    
    :param frame: Input video frame
    :param pose: MediaPipe pose solution
    :param exercise: PhysioExercise object
    :param scorer: SessionScorer object
    :param phase_detector: PhaseDetector object
    :return: Annotated frame, list of feedbacks, safety status
    """
    # Flip and convert
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process pose
    results = pose.process(rgb_frame)
    
    # Initialize feedback variables
    feedbacks = []
    angles = {}
    validations = {}
    safety_status = {"warning_level": 0, "warning_text": "SAFE", "is_safe": True}
    
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        
        # Calculate angles
        if "shoulder_abduction" in exercise.angle_ranges:
            angle = get_shoulder_abduction_angle(landmarks)
            angles["shoulder_abduction"] = angle
            validations["shoulder_abduction"] = exercise.is_angle_safe("shoulder_abduction", angle)

        if "elbow_flexion" in exercise.angle_ranges:
            angle = get_elbow_flexion_angle(landmarks)
            angles["elbow_flexion"] = angle
            validations["elbow_flexion"] = exercise.is_angle_safe("elbow_flexion", angle)

        if "shoulder_internal_rotation" in exercise.angle_ranges or "shoulder_external_rotation" in exercise.angle_ranges:
            rot_angles = get_shoulder_rotation_angle(landmarks)
            angles.update(rot_angles)
            validations["shoulder_internal_rotation"] = exercise.is_angle_safe("shoulder_internal_rotation", rot_angles.get("internal", 0))
            validations["shoulder_external_rotation"] = exercise.is_angle_safe("shoulder_external_rotation", rot_angles.get("external", 0))
        
        # Get phase info
        primary_angle = angles.get("shoulder_abduction") or angles.get("elbow_flexion") or 0
        frame_count = len(scorer.frames) + 1
        phase_info = phase_detector.detect_phase(primary_angle, frame_count)
        
        # Generate feedback (now phase-aware)
        feedbacks = generate_feedback(exercise.name.lower(), landmarks, phase_info)
        
        # Add frame to scorer (now with angle ranges for safety tracking)
        scorer.add_frame(angles, validations, exercise.angle_ranges)
        
        # Get safety status for runtime display
        safety_status = scorer.get_safety_status()
    
    # Draw pose landmarks
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, 
            results.pose_landmarks, 
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        )
        
        # Draw angles on frame
        y_offset = 30
        for angle_name, angle_value in angles.items():
            is_safe = validations.get(angle_name, True)
            draw_angle_on_frame(frame, angle_name, angle_value, (10, y_offset), is_safe)
            y_offset += 25
        
        # Draw safety warning
        draw_safety_warning(frame, safety_status["warning_text"], safety_status["warning_level"])
        
        # Draw phase indicator
        phase_info = phase_detector.get_phase_info()
        draw_phase_indicator(frame, phase_info["phase"], phase_info["hold_frames"])
    
    return frame, feedbacks, angles, safety_status


def main():
    """Main function to run the live physio demo."""
    print("=" * 60)
    print("LIVE PHYSIO INTELLIGENCE DEMO")
    print("Features: Real-time pose detection, phase-aware feedback, safety escalation")
    print("=" * 60)
    
    # Exercise selection
    print("\nAvailable exercises:")
    for key, exercise in EXERCISES.items():
        print(f"  - {key}: {exercise.description}")
    
    exercise_name = input("\nSelect exercise: ").strip().lower()
    exercise = EXERCISES.get(exercise_name)
    if not exercise:
        print("Invalid exercise")
        return
    
    print(f"\nSelected: {exercise.name}")
    print(f"Description: {exercise.description}")
    print("\nStarting webcam...")
    
    # Initialize scorer with safety escalation
    scorer = SessionScorer(exercise_name)
    
    # Initialize phase detector
    phase_detector = PhaseDetector(exercise_name)
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam")
        return
    
    # Get webcam properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30.0
    
    # Initialize MediaPipe Pose
    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=1
    ) as pose:
        
        print("\n" + "=" * 60)
        print("LIVE DEMO STARTED")
        print("Controls: 'q' to quit, 's' to show session summary")
        print("=" * 60)
        
        frame_count = 0
        prev_time = time.time()
        running = True
        
        while running:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            frame_count += 1
            
            # Process frame
            annotated_frame, feedbacks, angles, safety_status = process_frame(
                frame, pose, exercise, scorer, phase_detector
            )
            
            # Calculate FPS
            current_time = time.time()
            frame_fps = 1.0 / (current_time - prev_time)
            prev_time = current_time
            
            # Draw live observability
            draw_live_observability(annotated_frame, angles, frame_fps, frame_count)
            
            # Display frame
            cv2.imshow('Physio Intelligence - Live Demo', annotated_frame)
            
            # Console logging (optional - can be disabled for cleaner output)
            if frame_count % 30 == 0:  # Log every 30 frames
                safety = "SAFE" if safety_status["is_safe"] else "WARNING"
                print(f"[Frame {frame_count}] FPS: {frame_fps:.1f} | {safety} | Angles: {angles}")
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                running = False
            elif key == ord('s'):
                # Show session summary
                summary = scorer.get_summary()
                print("\n" + "=" * 60)
                print("SESSION SUMMARY")
                print("=" * 60)
                print(f"Exercise: {summary['exercise']}")
                print(f"Total Frames: {summary['total_frames']}")
                print(f"Safe Frames: {summary['safe_frames']}")
                print(f"Final Score: {summary['score']}/100")
                print(f"Safety Violations: {summary['safety']['total_violations']}")
                print(f"Highest Warning: Level {summary['safety']['highest_warning_level']}")
                print("=" * 60)
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Final summary
        print("\n" + "=" * 60)
        print("FINAL SESSION SUMMARY")
        print("=" * 60)
        summary = scorer.get_summary()
        print(f"Exercise: {summary['exercise']}")
        print(f"Duration: {frame_count / fps:.1f} seconds")
        print(f"Total Frames: {summary['total_frames']}")
        print(f"Safe Frames: {summary['safe_frames']}")
        print(f"Safety Compliance: {(summary['safe_frames']/summary['total_frames']*100):.1f}%")
        print(f"Final Score: {summary['score']}/100")
        print(f"\nSafety Violations:")
        safety = summary['safety']
        print(f"  - Total: {safety['total_violations']}")
        print(f"  - Low: {safety['by_severity']['low']}")
        print(f"  - Medium: {safety['by_severity']['medium']}")
        print(f"  - High: {safety['by_severity']['high']}")
        print(f"  - Critical: {safety['by_severity']['critical']}")
        print(f"Escalation Events: {safety['escalation_events']}")
        print("=" * 60)


if __name__ == "__main__":
    main()
