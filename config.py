import os
from dotenv import load_dotenv

load_dotenv()

# NEON Database
NEON_DATABASE_URL = os.getenv('NEON_DATABASE_URL', 'postgresql://user:password@ep-xxx.neon.tech/cctv_db')

# Twilio WhatsApp
TWILIO_ACCOUNT_SID   = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN    = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
WHATSAPP_TO          = os.getenv('WHATSAPP_TO', 'whatsapp:+92XXXXXXXXXX')

# Camera
# Camera
CAMERA_INDEX = os.getenv('CAMERA_INDEX', 'http://192.168.100.31:8080/video')
RTSP_URL     = os.getenv('RTSP_URL', '')
FRAME_WIDTH  = 1280
FRAME_HEIGHT = 720

# Detection
CONFIDENCE_THRESHOLD       = float(os.getenv('CONFIDENCE_THRESHOLD', 0.5))
FACE_RECOGNITION_TOLERANCE = 0.5
GENDER_CLASSIFY_INTERVAL   = 10
FACE_DETECT_INTERVAL       = 5

# Alerts
ALARM_COOLDOWN   = int(os.getenv('ALARM_COOLDOWN', 30))
ALARM_SOUND_PATH = os.path.join('assets', 'alarm.wav')

# Paths
CAPTURE_PATH    = 'captures/'
KNOWN_FACES_DIR = 'known_faces/'
LOGS_DIR        = 'logs/'

# YOLO
YOLO_MODEL = 'yolov8n.pt'
