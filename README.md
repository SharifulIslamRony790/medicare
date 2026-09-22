<div align="center">
  <h1>🏥 MediCare - Advanced Health Management System</h1>
  <p>A comprehensive, scalable, and secure hospital and clinic management system built with Django.</p>

  ![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
  ![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
  ![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
  ![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
</div>

<br />

> **🌍 Live Demo:** [https://medicare-5eop.onrender.com](https://medicare-5eop.onrender.com)

<br />

## 📖 Overview

MediCare is an all-in-one solution designed to streamline the operations of hospitals and clinics. It provides dedicated interfaces for managing patients, doctors, appointments, medical billing, and clinical prescriptions, ensuring a seamless experience for both staff and patients.

## 🌟 Key Features

- **🛡️ Role-Based Access Control (RBAC):** Dedicated portals and strict permissions for Admins, Doctors, Staff (Nurses, Cashiers, Receptionists), and Patients.
- **📅 Smart Appointment Scheduling:** Dynamic time-slot generation (10-minute intervals) that automatically accounts for doctor schedules and leaves. Built-in logic prevents double-booking.
- **💊 Clinical Prescriptions:** Doctors can write detailed prescriptions including symptoms, diagnoses, medications (with dosages), and advice. Generates highly styled PDF prescriptions on the fly.
- **💳 Billing & Payments:** Automated invoice generation, partial/full payment tracking, and PDF payment receipts.
- **📧 Asynchronous HTML Notifications:** Uses background threading to send beautiful HTML email notifications for signups, bookings, and payments, including automatically generated PDF invoice attachments without freezing the user interface.
- **🔒 Secure Infrastructure:** Built-in protection against IDOR (Insecure Direct Object References) and XSS. Production-ready security headers enforced.
- **📊 Admin Dashboard:** Excel report generation and KPI tracking using Unfold Admin.

## 🏗️ Tech Stack

- **Backend:** Python 3, Django 5.x
- **Database:** PostgreSQL 17
- **Document Generation:** ReportLab (PDFs), XlsxWriter (Excel)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.10 or higher
- Git

### Installation

**1. Clone the Repository**
```bash
git clone https://github.com/yourusername/MediCare.git
cd MediCare
```

**2. Create & Activate a Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Environment Variables**
Create a `.env` file in the root directory (where `manage.py` is located) and configure your secrets:
```env
DEBUG=True
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

**5. Database Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

**6. Create Superuser (Admin)**
```bash
python manage.py createsuperuser
```

**7. Run the Development Server**
```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000` in your browser.

## ☁️ Deployment (Render)

This project is configured for easy deployment on platforms like Render:
1. Set up a PostgreSQL database (e.g., Neon).
2. Ensure `dj-database-url`, `psycopg2-binary`, `gunicorn`, and `whitenoise` are installed.
3. Configure `DATABASE_URL` and `SECRET_KEY` in your host's environment variables.
4. Use `./build.sh` (or `python manage.py collectstatic --noinput && python manage.py migrate`) as your build command.
5. Use `gunicorn medicare_core.wsgi:application` as your start command.

## 👨‍💻 Developer Guide

The codebase follows a strict clean-code architecture. 
- **Sectional Comments:** All major views and models contain structured English comments (e.g., `=== FEATURE: ... ===`) explaining the purpose of the code.
- **Modifying Permissions:** Role logic is centralized in `users/models.py` within the `User` class. Update helper methods like `can_manage_billing()` to change access rules globally.

---

## 👤 Author

**Md Shariful Islam Rony**
- GitHub: [@SharifulIslamRony790](https://github.com/SharifulIslamRony790)
- LinkedIn: [@SharifulIslamRony](https://www.linkedin.com/in/md-shariful-islam-rony/)

---
*Built with ❤️ for better healthcare management.*
