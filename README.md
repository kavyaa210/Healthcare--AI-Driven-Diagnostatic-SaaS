# 🏥 CuraMind AI — Healthcare Diagnostic SaaS

> **HIPAA-Compliant Telehealth & Diagnostics Platform**  
> A secure platform connecting patients with medical specialists, powered by AI-driven diagnostic image analysis.

---

## 📋 Table of Contents
- [About the Project](#about-the-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [API Documentation](#api-documentation)
- [Team](#team)

---

## 🧠 About the Project

CuraMind AI is a production-grade healthcare SaaS platform built as part of the **Zaalima Development Q4 Python Elite Track**. It allows patients to securely upload medical images (X-rays, MRIs, DICOM files), which are then pre-processed by a Computer Vision model to highlight potential anomalies — before the radiologist conducts their formal review.

---

## ✨ Features

- 🔐 **JWT Authentication** — Secure login for Patients, Doctors, Nurses, and Admins
- 👥 **Role-Based Access Control (RBAC)** — Granular permissions using Django-Guardian
- 📅 **Appointment Scheduling** — Patients can book appointments with available doctors
- 📁 **Secure File Uploads** — Upload X-rays, MRI scans, lab reports (stored in private AWS S3)
- 🤖 **AI Diagnostic Pipeline** — Pre-trained ResNet/PyTorch model generates anomaly heatmaps
- 📝 **Electronic Medical Records (EMR)** — Secure, encrypted patient record storage
- 📋 **Prescription Management** — Doctors can create and manage prescriptions
- 🔍 **Audit Logging** — Every record access is logged for HIPAA compliance
- 🐳 **Dockerized** — Fully containerized with Docker Compose

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django + Django REST Framework |
| Authentication | JWT (djangorestframework-simplejwt) |
| Database | PostgreSQL |
| Object Storage | AWS S3 (django-storages) |
| Task Queue | Celery + Redis |
| RBAC | Django-Guardian |
| AI / CV Model | PyTorch + ResNet50 |
| DICOM Handling | pydicom |
| API Docs | drf-spectacular (Swagger) |
| Containerization | Docker + Docker Compose |
| Web Server | Gunicorn + Nginx |

---

## 📁 Project Structure

```
curamind/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── curamind/
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── apps/
│   ├── accounts/          # Custom user model, patient & doctor profiles
│   ├── appointments/      # Booking, attachments, prescriptions
│   ├── records/           # EMR, DICOM upload, audit logs
│   └── diagnostics/       # CV model, heatmap generation (Celery tasks)
└── templates/
    └── appointments/
        ├── book_appointment.html
        ├── appointment_list.html
        └── appointment_detail.html
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git

### Clone the repository
```bash
git clone https://github.com/kavyaa210/Healthcare--AI-Driven-Diagnostatic-SaaS.git
cd Healthcare--AI-Driven-Diagnostatic-SaaS
```

---

## 🔑 Environment Variables

Create a `.env` file in the root folder:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

# PostgreSQL
DB_NAME=curamind_db
DB_USER=curamind_user
DB_PASSWORD=strongpassword123
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=curamind-medical-images
AWS_S3_REGION_NAME=us-east-1

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your-app-password
```

> ⚠️ Never commit your `.env` file. It is already added to `.gitignore`.

---

## ▶️ Running the Project

### Option 1 — Docker (Recommended)
```bash
docker-compose up --build
```

### Option 2 — Manual

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 2. Install packages
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env            # then fill in your DB, Redis, S3 values

# 4. Run migrations
python manage.py migrate

# 5. Create admin user
python manage.py createsuperuser

# 6. Start Django (Terminal 1)
python manage.py runserver

# 7. Start Celery worker (Terminal 2)
celery -A curamind worker --loglevel=info
```

---

## 🌐 Access the App

| Page | URL |
|---|---|
| App | http://localhost:8000 |
| Django Admin | http://localhost:8000/admin |
| Swagger API Docs | http://localhost:8000/api/schema/swagger-ui/ |

---

## 📖 API Documentation

Once the server is running, visit:
```
http://localhost:8000/api/schema/swagger-ui/
```
All endpoints are fully documented with request/response schemas.

---

## 👩‍💻 Team

| Name | Role |
|---|---|
| Kavya Panchal | Backend Developer |

---

## 🏢 Organization

**Zaalima Development Pvt. Ltd**  
*Q4 Python Elite Track — Internal Project*  
*Building the Future, One Line at a Time.*
