# AI-smart-cctv-system

# 🛡️ Smart CCTV AI Security System

**AI-Powered Real-time Security & Surveillance System** with Face Recognition, Thief Detection, WhatsApp Alerts & Live Dashboard.

Yeh project YOLOv8, Face Recognition aur DeepFace ka use karke smart surveillance system banata hai jo automatically thief detect karta hai, alarm bajata hai aur WhatsApp pe alert bhejta hai.

## ✨ Key Features

- 👤 **Real-time Person Detection** using YOLOv8
- 🔍 **Face Recognition** + Known/Unknown faces
- 🧑‍🤝‍🧑 **Male/Female Classification** (DeepFace)
- 🚨 **Auto Thief Detection & Alarm**
- 📱 **WhatsApp Alerts** via Twilio
- 🦴 **Body Pose Estimation** (MediaPipe)
- 👁️ **Eye Region Highlighting** for thieves
- 📊 **People Counting** + Movement Trail Tracking
- 🗄️ **NEON PostgreSQL Database** integration
- 📸 **Auto Snapshot Capture**

## 🛠 Tech Stack

- **AI/Computer Vision**: YOLOv8, face_recognition, DeepFace, MediaPipe
- **Backend**: Python, OpenCV
- **Database**: PostgreSQL (NEON)
- **Alerts**: Twilio (WhatsApp)
- **Alarm**: Pygame Audio
- **Others**: SQLAlchemy, python-dotenv

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Tauqeerkhan97/smart-cctv-ai-security-system.git
cd smart-cctv-ai-security-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup Environment
cp .env.example .env
# .env file mein apne credentials fill karo (NEON, Twilio, etc.)

Run the System
Bashpython main.py
Controls:

q → Quit
s → Stop Alarm
c → Manual Capture
a → Add current face as Thief

📁 Project Structure
Bash├── detection/          # YOLO, Face Recognition, Gender, Pose
├── tracking/           # Movement trails + Eye highlight
├── alerts/             # Alarm + WhatsApp
├── database/           # NEON DB models & functions
├── dashboard/          # Live HUD display
├── utils/              # Captures & logging
├── known_faces/        # Known persons & thieves
└── main.py
🎯 What I Learned

Real-time AI Computer Vision system
Multi-model integration (YOLO + Face Recognition + Pose)
Database + Notification system
Production-ready security application development


Made with ❤️ by Muhammad Tauqeer
AI Engineer | Computer Vision | Backend Developer
🔗 Portfolio: https://my-portfolio-theta-wine-24.vercel.app
