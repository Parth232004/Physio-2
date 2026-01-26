# webcam_demo.py
# Real-time demo using webcam for physiotherapy exercise validation

import cv2
import mediapipe as mp
from physio_exercises import EXERCISES, get_shoulder_abduction_angle, get_elbow_flexion_angle, get_shoulder_rotation_angle
from exercise_router import validate_movement
from realtime_feedback import generate_feedback
from session_scoring import SessionScorer
import time

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def main():
    exercise_name = input("Select exercise (arm_raise, shoulder_rotation, elbow_flexion): ").strip()
    exercise = EXERCISES.get(exercise_name.lower())
    if not exercise:
        print("Invalid exercise")
        return

    scorer = SessionScorer(exercise_name)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam")
        return

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        print("Starting webcam demo. Press 'q' to quit.")
        start_time = time.time()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Flip and convert
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process pose
            results = pose.process(rgb_frame)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                # Calculate angles
                angles = {}
                validations = {}

                if "shoulder_abduction" in exercise.angle_ranges:
                    angle = get_shoulder_abduction_angle(landmarks)
                    angles["shoulder_abduction"] = angle
                    validations["shoulder_abduction"] = exercise.is_angle_safe("shoulder_abduction", angle)

                if "elbow_flexion" in exercise.angle_ranges:
                    angle = get_elbow_flexion_angle(landmarks)
                    angles["elbow_flexion"] = angle
                    validations["elbow_flexion"] = exercise.is_angle_safe("elbow_flexion", angle)

                if "shoulder_internal_rotation" in angle_ranges or "shoulder_external_rotation" in angle_ranges:
                    rot_angles = get_shoulder_rotation_angle(landmarks)
                    angles.update(rot_angles)
                    validations["shoulder_internal_rotation"] = exercise.is_angle_safe("shoulder_internal_rotation", rot_angles["internal"])
                    validations["shoulder_external_rotation"] = exercise.is_angle_safe("shoulder_external_rotation", rot_angles["external"])

                # Generate feedback
                feedbacks = generate_feedback(exercise_name, landmarks)

                # Add to scorer
                scorer.add_frame(angles, validations)

                # Display feedback on frame
                y_offset = 30
                for feedback in feedbacks:
                    cv2.putText(frame, feedback, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    y_offset += 30

                # Log to console (for demo)
                print(f"Angles: {angles}, Feedback: {feedbacks}")

            # Draw landmarks
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow('Physio Demo', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

    # Final score
    summary = scorer.get_summary()
    print(f"Session Summary: {summary}")

if __name__ == "__main__":
    main()