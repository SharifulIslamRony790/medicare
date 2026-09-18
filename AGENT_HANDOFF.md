# MediCare Agent Handoff Report

> **Target Audience:** Any AI Agent, AI Coding Assistant, or Developer taking over this project.
> **Purpose:** To provide instant technical context, structural breakdown, and workflow history for the MediCare Django project.

## 1. Technical Context & Stack

- **Framework:** Django 5.2.x, Python 3.10+
- **Database:** PostgreSQL
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Bootstrap 5.
- **Admin Panel:** `django-unfold` (highly customized SaaS-like admin interface).
- **Authentication:** `django-allauth` (includes Google OAuth integration).
- **Core Libraries:** 
  - `djangorestframework` (API support)
  - `reportlab` (PDF Generation for Invoices/Prescriptions)
  - `xlsxwriter` (Excel Report Generation)

## 2. Structural Breakdown (Django Apps)

The project follows a modular, clean-code architecture. 
The core configuration app is `medicare_core`. The functional apps are:

1. **`users`**: Handles custom user model (`User`), roles, authentication, and OAuth.
2. **`dashboard`**: Handles the primary views for logged-in users and analytical KPI data.
3. **`patients`**: Manages patient profiles, medical history, and related metrics.
4. **`doctors`**: Manages doctor profiles, specializations, and schedules.
5. **`appointments`**: Handles booking logic, smart 10-minute slot generation, preventing double-bookings.
6. **`prescriptions`**: Doctor's interface for writing digital prescriptions with PDF export.
7. **`billing`**: Invoice generation, payment tracking, partial payment handling.
8. **`staff`**: Manages hospital staff (receptionists, nurses, cashiers) via the `sub_role` field.

## 3. Role-Based Access Control (RBAC) Architecture

**CRITICAL:** Do not use Django's default `is_staff` for general role checks. The system uses a highly customized role structure in `users/models.py`.

- **Primary Role Field:** `user.role` (Choices: `admin`, `doctor`, `staff`, `patient`).
- **Staff Sub-roles:** If `user.role == 'staff'`, check `user.staff_profile.sub_role` (Choices: `nurse`, `receptionist`, `cashier`).
- **Authorization Flow:** Access control is managed through mixins (e.g., `DoctorRequiredMixin`) and helper methods on the User model (e.g., `user.can_manage_billing()`). **Always use these helper methods instead of hardcoding role checks in templates.**

## 4. UI/UX & Design Guidelines

- **Bootstrap 5:** The UI relies heavily on standard Bootstrap 5 utility classes (e.g., `d-flex`, `align-items-center`, `rounded-4`, `shadow-sm`).
- **Do not use inline CSS or custom classes for standard layout requirements.** (Past Failure: Inline width styling in `invoice_detail.html` broke the print layout and responsive grids. Always use Bootstrap classes like `col-12`, `col-md-6`, etc.).
- **Print Styles:** Files like `invoice_detail.html` and `prescription_print.html` contain complex `@media print` blocks. Modify DOM structures very carefully in these files, as grid changes (e.g., changing `col-md-6` to `col-12`) can completely break the PDF/Print layout.

## 5. Workflow History & Current State

- **Completed Tasks:**
  - Standardized UI across patient, doctor, and billing dashboards.
  - Fixed table overflow issues on mobile/sidebar-toggle using `table-responsive` and `text-nowrap`.
  - Refined Invoice detail page design (Professional, minimalist UI with Bootstrap flex layouts).
  - Cleaned up `README.md` to GitHub standards.
- **Pending/Next Steps:**
  - **Render Deployment Setup:** The project is preparing for a Render deployment.
  - An `implementation_plan.md` has been proposed to add `dj-database-url`, `psycopg2-binary`, `gunicorn`, `whitenoise` static roots, and a `build.sh` file. 
  - The current state is fully tested locally (`runserver` works perfectly, `.env` and `db.sqlite3` are properly `.gitignore`d).

## 6. Agent Rules of Engagement

1. **Zero-Trust Input:** Always validate user input on the server side (Forms/Serializers).
2. **Impact Analysis:** Before updating a template's grid (e.g., changing a row/col layout), analyze how it impacts the mobile view and `@media print` views.
3. **No Hardcoding:** Never hardcode URLs in templates (use `{% url 'name' %}`) and never hardcode API keys/secrets (use `os.getenv()`).
4. **Professional Output:** Keep HTML/CSS clean, use modern aesthetic patterns (glassmorphism, subtle shadows, rounded borders), and avoid generic "AI-like" boilerplate.
