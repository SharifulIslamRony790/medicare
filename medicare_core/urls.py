"""
URL configuration for medicare_core project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet
from patients.views import PatientViewSet
from doctors.views import DoctorViewSet
from appointments.views import AppointmentViewSet
from prescriptions.views import PrescriptionViewSet
from billing.views import InvoiceViewSet
from medicare_core.views import home, contact, support, privacy, user_guide, faqs, live_chat
from patients.views import patient_list, patient_add, patient_detail, patient_dashboard_view
from doctors.views import doctor_list, doctor_add, doctor_leave_list, doctor_leave_add, doctor_leave_delete, doctor_dashboard_view, doctor_detail
from appointments.views import appointment_list, appointment_add, appointment_complete, appointment_cancel, get_available_slots
from prescriptions.views import prescription_list, prescription_add, prescription_pdf, prescription_print_view
from billing.views import invoice_list, invoice_add, invoice_detail, invoice_approve, payment_select, payment_process, payment_success, payment_receipt_pdf
from users.views import login_view, signup_view, logout_view, settings_view, doctor_signup_view, patient_signup_view, complete_profile_view, complete_doctor_profile_view
from dashboard.views import download_monthly_revenue_excel, contact_message_list, resolve_contact_message

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'doctors', DoctorViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'prescriptions', PrescriptionViewSet)
router.register(r'billing', InvoiceViewSet)

urlpatterns = [
    path('dashboard/monthly-revenue/export/', download_monthly_revenue_excel, name='export_monthly_revenue'),
    path('dashboard/', admin.site.urls),
    path('staff/', include('staff.urls')),
    path('staff/messages/', contact_message_list, name='contact_message_list'),
    path('staff/messages/<int:msg_id>/resolve/', resolve_contact_message, name='resolve_contact_message'),
    path('accounts/', include('allauth.urls')),
    path('api/', include(router.urls)),
    path('', home, name='home'),
    path('patients/', patient_list, name='patient_list'),
    path('patients/add/', patient_add, name='patient_add'),
    path('patients/<int:pk>/', patient_detail, name='patient_detail'),
    path('profile/patient/', patient_dashboard_view, name='patient_dashboard'),
    path('profile/doctor/', doctor_dashboard_view, name='doctor_dashboard'),
    path('doctors/', doctor_list, name='doctor_list'),
    path('doctors/<int:pk>/', doctor_detail, name='doctor_detail'),
    path('doctors/add/', doctor_add, name='doctor_add'),
    path('doctors/leaves/', doctor_leave_list, name='doctor_leave_list'),
    path('doctors/leaves/add/', doctor_leave_add, name='doctor_leave_add'),
    path('doctors/leaves/<int:pk>/delete/', doctor_leave_delete, name='doctor_leave_delete'),
    path('appointments/', appointment_list, name='appointment_list'),
    path('appointments/add/', appointment_add, name='appointment_add'),
    path('appointments/<int:pk>/complete/', appointment_complete, name='appointment_complete'),
    path('appointments/<int:pk>/cancel/', appointment_cancel, name='appointment_cancel'),
    path('api/available-slots/', get_available_slots, name='get_available_slots'),
    path('prescriptions/', prescription_list, name='prescription_list'),
    path('prescriptions/add/', prescription_add, name='prescription_add'),
    path('prescriptions/<int:pk>/pdf/', prescription_pdf, name='prescription_pdf'),
    path('prescriptions/<int:pk>/print/', prescription_print_view, name='prescription_print'),
    path('billing/', invoice_list, name='invoice_list'),
    path('billing/add/', invoice_add, name='invoice_add'),
    path('billing/<int:pk>/', invoice_detail, name='invoice_detail'),
    path('billing/<int:invoice_id>/approve/', invoice_approve, name='invoice_approve'),
    path('billing/<int:invoice_id>/pay/', payment_select, name='payment_select'),
    path('billing/<int:invoice_id>/pay/<str:method>/', payment_process, name='payment_process'),
    path('billing/<int:invoice_id>/success/', payment_success, name='payment_success'),
    path('billing/payment/<int:payment_id>/receipt/', payment_receipt_pdf, name='payment_receipt_pdf'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('signup/patient/', patient_signup_view, name='patient_signup'),
    path('signup/doctor/', doctor_signup_view, name='doctor_signup'),
    path('logout/', logout_view, name='logout'),
    path('settings/', settings_view, name='settings'),
    path('complete-profile/', complete_profile_view, name='complete_profile'),
    path('complete-doctor-profile/', complete_doctor_profile_view, name='complete_doctor_profile'),
    path('contact/', contact, name='contact'),
    path('support/', support, name='support'),
    path('support/user-guide/', user_guide, name='user_guide'),
    path('support/faqs/', faqs, name='faqs'),
    path('support/live-chat/', live_chat, name='live_chat'),
    path('privacy/', privacy, name='privacy'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
