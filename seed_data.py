import os
import django
import requests
from django.core.files.base import ContentFile
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicare_core.settings')
django.setup()

from users.models import User
from patients.models import Patient
from doctors.models import Doctor, DoctorSchedule
from staff.models import Staff
from django.db import transaction

def fetch_random_users(count):
    # Fetch random realistic data from API
    response = requests.get(f'https://randomuser.me/api/?results={count}')
    if response.status_code == 200:
        return response.json()['results']
    else:
        raise Exception("Failed to fetch realistic data from API.")

def clear_old_data():
    print("Deleting all non-superuser data...")
    users_to_delete = User.objects.filter(is_superuser=False)
    count = users_to_delete.count()
    users_to_delete.delete()
    print(f"Deleted {count} users and all associated cascade data (Patients, Doctors, Staff, Invoices).")

def seed_data():
    clear_old_data()
    
    total_needed = 10 + 10 + 18
    print(f"Fetching {total_needed} random realistic profiles from randomuser.me...")
    profiles = fetch_random_users(total_needed)
    
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    specialties = ['Cardiologist', 'Neurologist', 'Pediatrician', 'Orthopedist', 'Dermatologist', 'Psychiatrist', 'General Physician']
    roles = ['receptionist', 'nurse', 'pharmacist', 'cashier', 'manager', 'support_agent']
    
    # Pre-selected professional Unsplash photos for Doctors
    doctor_images = [
        'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400',
        'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=400',
        'https://images.unsplash.com/photo-1594824436998-d70cb0c529d6?w=400',
        'https://images.unsplash.com/photo-1537368910025-702800faa86b?w=400',
        'https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=400',
        'https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=400',
        'https://images.unsplash.com/photo-1527613426441-4da17471b66d?w=400',
        'https://images.unsplash.com/photo-1584982751601-97d8ce673419?w=400',
        'https://images.unsplash.com/photo-1605684954998-685c79d6a018?w=400',
        'https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=400',
    ]
    random.shuffle(doctor_images)
    
    nurse_images = [
        'https://images.unsplash.com/photo-1580281657521-820875e6d628?w=400',
        'https://images.unsplash.com/photo-1584467735815-f778f274e296?w=400',
        'https://images.unsplash.com/photo-1576091160550-2173ff9e5fe8?w=400',
    ]
    
    # pravatar.cc IDs 11-70 have very clean, professional portraits
    img_ids = list(range(11, 71))
    random.shuffle(img_ids)
    
    # 1. Create 10 Patients
    print("Creating 10 Patients...")
    for i in range(10):
        p_data = profiles.pop(0)
        first_name = p_data['name']['first'].capitalize()
        last_name = p_data['name']['last'].capitalize()
        email = p_data['email']
        
        user = User.objects.create_user(
            username=p_data['login']['username'],
            email=email,
            password='password123',
            first_name=first_name,
            last_name=last_name,
            role='patient'
        )
        
        patient = user.patient_profile
        patient.name = f"{first_name} {last_name}"
        patient.age = p_data['dob']['age']
        patient.gender = 'M' if p_data['gender'] == 'male' else 'F'
        patient.phone = p_data['phone'][:15]
        patient.email = email
        patient.address = f"{p_data['location']['street']['number']} {p_data['location']['street']['name']}, {p_data['location']['city']}"
        patient.blood_group = random.choice(blood_groups)
        
        img_id = img_ids.pop(0)
        img_response = requests.get(f'https://i.pravatar.cc/400?img={img_id}')
        if img_response.status_code == 200:
            patient.image.save(f"patient_{i}.jpg", ContentFile(img_response.content), save=False)
        
        patient.save()
        print(f"  - Created Patient: {patient.name}")

    # 2. Create 10 Doctors
    print("\nCreating 10 Doctors...")
    for i in range(10):
        p_data = profiles.pop(0)
        first_name = p_data['name']['first'].capitalize()
        last_name = p_data['name']['last'].capitalize()
        email = p_data['email']
        
        user = User.objects.create_user(
            username=p_data['login']['username'],
            email=email,
            password='password123',
            first_name=first_name,
            last_name=last_name,
            role='doctor'
        )
        
        doctor = user.doctor_profile
        doctor.name = f"Dr. {first_name} {last_name}"
        doctor.phone = p_data['phone'][:20]
        doctor.specialty = random.choice(specialties)
        
        img_response = requests.get(doctor_images.pop(0))
        if img_response.status_code == 200:
            doctor.image.save(f"doctor_{i}_{first_name}.jpg", ContentFile(img_response.content), save=False)
            
        doctor.save()
        print(f"  - Created Doctor: {doctor.name} ({doctor.specialty})")
        
    # 3. Create Staff
    print("\nCreating Staff...")
    for role in roles:
        count = 1 if role == 'manager' else 3
        for _ in range(count):
            p_data = profiles.pop(0)
            first_name = p_data['name']['first'].capitalize()
            last_name = p_data['name']['last'].capitalize()
            email = p_data['email']
            
            user = User.objects.create_user(
                username=p_data['login']['username'],
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name,
                role='staff'
            )
            
            staff, _ = Staff.objects.get_or_create(user=user)
            staff.name = f"{first_name} {last_name}"
            staff.sub_role = role
            staff.phone = p_data['phone'][:15]
            
            if role == 'nurse':
                img_response = requests.get(random.choice(nurse_images))
            else:
                img_id = img_ids.pop(0)
                img_response = requests.get(f'https://i.pravatar.cc/400?img={img_id}')
                
            if img_response.status_code == 200:
                staff.image.save(f"staff_{role}_{_}.jpg", ContentFile(img_response.content), save=False)
                
            staff.save()
            print(f"  - Created Staff: {staff.name} ({role})")

    print("\nSuccessfully seeded all realistic data!")
    print("Default password for all dummy accounts is: password123")

if __name__ == '__main__':
    with transaction.atomic():
        seed_data()
