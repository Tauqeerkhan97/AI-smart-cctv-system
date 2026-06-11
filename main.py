#!/usr/bin/env python3
"""
Smart CCTV Security System
Controls: q=quit  s=stop-alarm  c=capture  a=add-thief  h=toggle-heatmap
"""

import cv2
import time
import threading

from config import (
    CAMERA_INDEX, RTSP_URL,
    FRAME_WIDTH, FRAME_HEIGHT,
    GENDER_CLASSIFY_INTERVAL, FACE_DETECT_INTERVAL,
    CAPTURE_PATH, KNOWN_FACES_DIR, LOGS_DIR,
)
from database.neon_db            import init_database, log_movement, save_alert
from detection.person_detector   import PersonDetector
from detection.face_recognizer   import FaceRecognizer
from detection.gender_classifier import GenderClassifier
from detection.pose_estimator    import PoseEstimator
from tracking.movement_tracker   import MovementTracker
from tracking.eye_region         import highlight_eye_region
from alerts.alarm_system         import AlarmSystem
from alerts.whatsapp_notifier    import WhatsAppNotifier
from dashboard.live_display      import LiveDisplay
from utils.image_capture         import capture_image, ensure_dirs
from utils.logger                import get_logger

logger = get_logger('main')

_obj_lock    = threading.Lock()
_obj_results = {}


def _obj_worker(detector, frame, detections):
    objects = detector.detect_objects(frame)
    new = {}
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        tid  = det['track_id']
        near = []
        for obj in objects:
            ox1, oy1, ox2, oy2 = obj['bbox']
            ocx = (ox1 + ox2) // 2
            ocy = (oy1 + oy2) // 2
            if (x1 - 40 <= ocx <= x2 + 40) and (y1 - 20 <= ocy <= y2 + 80):
                near.append(obj)
        new[tid] = near
    with _obj_lock:
        _obj_results.clear()
        _obj_results.update(new)


def open_camera():
    src = RTSP_URL if RTSP_URL else CAMERA_INDEX
    cap = cv2.VideoCapture(src)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not cap.isOpened():
        raise RuntimeError(f'Cannot open camera: {src}')
    return cap


def main():
    ensure_dirs(CAPTURE_PATH, KNOWN_FACES_DIR, LOGS_DIR, 'assets')
    logger.info('Initialising Smart CCTV Security System...')
    init_database()

    detector   = PersonDetector()
    recognizer = FaceRecognizer()
    gender_clf = GenderClassifier()
    pose_est   = PoseEstimator()
    tracker    = MovementTracker()
    alarm      = AlarmSystem()
    notifier   = WhatsAppNotifier()
    hud        = LiveDisplay(camera_id='CAM_01',
                             frame_w=FRAME_WIDTH, frame_h=FRAME_HEIGHT)

    cap          = open_camera()
    frame_no     = 0
    fps          = 0.0
    fps_timer    = time.time()
    counts       = {'total': 0, 'male': 0, 'female': 0, 'suspicious': 0}
    genders      = {}
    last_faces   = []
    thief_active = False
    show_heatmap = True
    obj_thread   = None

    logger.info('System running. q=quit s=stop-alarm c=capture a=add-thief h=heatmap')
    print('[SYSTEM] Smart CCTV running. q / s / c / a / h')

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.03)
            continue

        frame_no += 1

        if frame_no % 30 == 0:
            fps       = 30.0 / max(time.time() - fps_timer, 1e-6)
            fps_timer = time.time()

        # ==============================================================
        # 1. PERSON DETECTION
        # ==============================================================
        detections           = detector.detect_persons(frame)
        counts['total']      = len(detections)
        counts['male']       = 0
        counts['female']     = 0
        counts['suspicious'] = 0
        thief_active         = False
        centers              = []

        for det in detections:
            tid             = det['track_id']
            bbox            = det['bbox']
            x1, y1, x2, y2 = bbox
            cx, cy          = (x1 + x2) // 2, (y1 + y2) // 2
            centers.append((cx, cy))

            tracker.update(tid, (cx, cy))
            direction = tracker.get_direction(tid)
            speed     = tracker.get_speed(tid)
            susp      = tracker.is_suspicious(tid)
            if susp:
                counts['suspicious'] += 1
            hud.mark_suspicious(tid, susp)

            if frame_no % GENDER_CLASSIFY_INTERVAL == 0:
                g = gender_clf.classify(frame, bbox, tid)
                genders[tid] = g
                hud.update_gender(tid, g)
            gender = genders.get(tid, 'Unknown')
            if gender == 'Male':   counts['male']   += 1
            if gender == 'Female': counts['female'] += 1

            frame, angle = pose_est.estimate(frame, bbox)

            with _obj_lock:
                person_objs = _obj_results.get(tid, [])
            hud.update_inventory(tid, person_objs)

            if susp and not alarm.is_active:
                alarm.trigger(reason='Suspicious Movement')
                notifier.send_suspicious_alert(
                    track_id=tid,
                    reason='Loitering / Running detected',
                    location='CAM_01'
                )
                capture_image(frame, label='SUSPICIOUS', person_id=str(tid))

            if frame_no % 15 == 0:
                log_movement(person_id=tid, track_id=tid,
                             x=float(cx), y=float(cy),
                             angle=angle, direction=direction)

            frame = detector.draw_box(
                frame, bbox, tid,
                gender=gender, direction=direction,
                angle=angle, is_thief=False,
                objects=person_objs, speed=speed
            )

        hud.update_heatmap(centers)

        if frame_no % 10 == 0:
            if obj_thread is None or not obj_thread.is_alive():
                obj_thread = threading.Thread(
                    target=_obj_worker,
                    args=(detector, frame.copy(), list(detections)),
                    daemon=True
                )
                obj_thread.start()

        # ==============================================================
        # 2. FACE RECOGNITION
        # ==============================================================
        if frame_no % FACE_DETECT_INTERVAL == 0:
            last_faces = recognizer.recognize(frame)

        for face in last_faces:
            loc      = face['location']
            name     = face['name']
            is_thief = face['is_thief']

            frame = recognizer.draw_face(frame, loc, name, is_thief)

            if is_thief:
                thief_active = True
                frame = highlight_eye_region(frame, loc)
                alarm.trigger(reason=f'Thief: {name}')

                img_path = capture_image(frame, label='THIEF', person_id=name)

                with _obj_lock:
                    all_objs = [o['label']
                                for objs in _obj_results.values()
                                for o in objs]
                notifier.send_thief_alert(
                    person_name=name, location='CAM_01',
                    image_path=img_path,
                    objects_carried=all_objs if all_objs else None
                )
                save_alert(alert_type='thief', person_name=name,
                           image_path=img_path, camera_id='CAM_01')

        # ==============================================================
        # 3. TRAILS + HUD + DISPLAY
        # ==============================================================
        frame = tracker.draw_trails(frame)

        hud.set_thief_alert(
            thief_active,
            name=last_faces[0]['name'] if last_faces and thief_active else '',
            reason=alarm.reason
        )
        frame = hud.render(frame, fps, counts, show_heatmap=show_heatmap)

        cv2.imshow('Smart CCTV Security System', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            alarm.stop()
        elif key == ord('c'):
            capture_image(frame, label='manual')
        elif key == ord('h'):
            show_heatmap = not show_heatmap
            print(f'[HUD] Heatmap: {"ON" if show_heatmap else "OFF"}')
        elif key == ord('a'):
            for face in last_faces:
                if face['name'] == 'Unknown':
                    from database.neon_db import save_person
                    pid = save_person(
                        name='Suspect', gender='Unknown',
                        face_encoding=face['encoding'],
                        is_thief=True, location='CAM_01'
                    )
                    print(f'[DB] Suspect saved (id={pid})')
                    recognizer._load_thieves_from_db()
                    break

    cap.release()
    cv2.destroyAllWindows()
    alarm.stop()
    print('[SYSTEM] Stopped.')


if __name__ == '__main__':
    main()
