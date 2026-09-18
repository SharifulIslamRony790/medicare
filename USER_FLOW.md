# MediCare - User Flow Guide

This document outlines the step-by-step journey for each role within the MediCare system.

---

## 🧑‍⚕️ 1. Patient Flow
**Goal:** Book an appointment, receive consultation, and pay bills.

1. **Sign Up & Login:** Patient creates an account or logs in via Google/Email.
2. **Dashboard Overview:** Views upcoming appointments, recent prescriptions, and unpaid invoices.
3. **Book Appointment:** 
   - Browses the list of available doctors.
   - Selects a specific date.
   - Chooses an available 10-minute time slot.
   - Confirms booking (receives email notification).
4. **Consultation:** Visits the hospital/clinic for the checkup.
5. **View Prescription:** After the checkup, logs in to download or print the digital prescription provided by the doctor.
6. **Payment:** 
   - Checks the "Invoices" section.
   - Clicks "Proceed to Payment" for unpaid invoices.
   - Completes payment (partial or full) and downloads the receipt.

---

## 👨‍⚕️ 2. Doctor Flow
**Goal:** Manage schedule and write clinical prescriptions.

1. **Login:** Doctor logs into their dedicated portal.
2. **View Schedule:** Checks the dashboard for today's appointments and overall patient queue.
3. **Manage Appointments:** Reviews patient details and medical history before consultation.
4. **Write Prescription:** 
   - Clicks on a patient's appointment.
   - Fills in Symptoms, Diagnosis, Advice.
   - Adds Medications (Name, Dosage, Duration, Instructions).
   - Saves and generates a PDF prescription.

---

## 👩‍💼 3. Staff Flow (Nurses, Receptionists, Cashiers)
**Goal:** Manage hospital operations, handle walk-in patients, and process offline payments.

1. **Login:** Logs into the staff portal. Role capabilities depend on their `sub_role` (Receptionist vs. Cashier).
2. **Patient Management (Receptionist):** Registers new walk-in patients and books appointments on their behalf.
3. **Queue Management:** Updates appointment statuses (e.g., "Checked In", "Completed").
4. **Billing & Approvals (Cashier):** 
   - Generates invoices for patient visits or extra services.
   - Collects cash at the desk and marks invoices as "Paid".
   - Approves pending online payments.

---

## 👑 4. Admin Flow
**Goal:** Oversee the entire system, manage users, and view analytics.

1. **Login:** Logs into the high-level Django Admin Panel (`/admin`).
2. **Analytics Monitoring:** Views the dashboard for total revenue, daily appointments, and active users.
3. **User Management:** 
   - Adds new Doctors and configures their specialties.
   - Hires and registers new Staff members, assigning them specific sub-roles.
   - Can block or manage Patient accounts if necessary.
4. **System Reporting:** Generates and downloads Excel reports for financial and operational auditing.
