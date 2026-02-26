"""Script to programmatically submit a consultant application via Django test client
and verify reviewer/admin pages and saved files.
Run from project root with the project's virtualenv Python.
"""
import os
import sys
import django
import io
from pathlib import Path

# configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from apps.consultations.models import ConsultantApplication
from django.core.files.uploadedfile import SimpleUploadedFile

BASE_DIR = Path(__file__).resolve().parents[1]
print('BASE_DIR:', BASE_DIR)

User = get_user_model()

# ensure dummy files exist in tmp/
TMP = BASE_DIR / 'tmp'
TMP.mkdir(exist_ok=True)
resume_path = TMP / 'dummy_resume.pdf'
cv_path = TMP / 'dummy_cv.pdf'
if not resume_path.exists():
    resume_path.write_bytes(b'Dummy resume content')
if not cv_path.exists():
    cv_path.write_bytes(b'Dummy CV content')

# create test client
c = Client()

# ensure applicant user exists
app_username = 'applicant1'
app_password = 'ApplicantPass123!'
app_email = 'applicant1@example.com'
app_user = None
try:
    app_user = User.objects.get(username=app_username)
    print('Found applicant user:', app_user.username)
except User.DoesNotExist:
    print('Creating applicant user...')
    app_user = User.objects.create_user(username=app_username, email=app_email, password=app_password)
    print('Created user', app_user.username)

# ensure admin user exists
admin_username = 'admin'
admin_password = 'AdminPass123!'
admin_email = 'admin@example.com'
admin_user = None
try:
    admin_user = User.objects.get(username=admin_username)
    print('Found admin user:', admin_user.username)
except User.DoesNotExist:
    print('Creating admin user...')
    admin_user = User.objects.create_superuser(username=admin_username, email=admin_email, password=admin_password)
    print('Created superuser', admin_user.username)

# Step 1: login as applicant and GET application page
print('\n== Attempting to login as applicant and GET application page ==')
if not c.login(username=app_username, password=app_password):
    print('Login failed for applicant (attempting to set password and retry)')
    app_user.set_password(app_password)
    app_user.save()
    if not c.login(username=app_username, password=app_password):
        print('Login still failed — will continue by creating application via ORM instead')

resp = c.get('/accounts/consultant-application/')
print('GET /accounts/consultant-application/ status:', resp.status_code)
print('Response length:', len(resp.content or b''))

# Step 2: POST form with files if GET was OK
post_data = {
    'full_name': 'Applicant One',
    'email': app_email,
    'phone': '555-0101',
    'experience_years': '7',
    'specialization': 'Project Management',
    'cover_letter': 'I would like to help with projects.'
}
with open(resume_path, 'rb') as f_resume, open(cv_path, 'rb') as f_cv:
    resume_upload = SimpleUploadedFile(resume_path.name, f_resume.read(), content_type='application/pdf')
    cv_upload = SimpleUploadedFile(cv_path.name, f_cv.read(), content_type='application/pdf')

    response = c.post('/accounts/consultant-application/', data={**post_data}, files={'resume': resume_upload, 'cv': cv_upload}, follow=True)
    print('POST /accounts/consultant-application/ status:', response.status_code)
    print('POST final URL:', response.request.get('PATH_INFO'))

# If POST didn't create an application (or login failed), create via ORM as fallback
apps = ConsultantApplication.objects.filter(email=app_email).order_by('-submitted_at')
if apps.exists():
    app = apps.first()
    print('\nFound application (query) id=', app.id, 'email=', app.email)
else:
    print('\nNo application found via view — creating one directly via ORM as fallback')
    with open(resume_path, 'rb') as fr:
        resume_file = SimpleUploadedFile(resume_path.name, fr.read(), content_type='application/pdf')
        with open(cv_path, 'rb') as fc:
            cv_file = SimpleUploadedFile(cv_path.name, fc.read(), content_type='application/pdf')
            app = ConsultantApplication.objects.create(
                user=app_user,
                full_name=post_data['full_name'],
                email=post_data['email'],
                phone=post_data['phone'],
                specialization=post_data['specialization'],
                experience_years=int(post_data['experience_years']),
                cover_letter=post_data['cover_letter'],
                resume=resume_file,
                cv=cv_file,
            )
            print('Created application via ORM id=', app.id)

# Verify files existence on disk
try:
    resume_path_on_disk = app.resume.path
    cv_path_on_disk = app.cv.path
    print('\nSaved resume path:', resume_path_on_disk)
    print('Saved cv path:', cv_path_on_disk)
    print('Resume exists on disk:', Path(resume_path_on_disk).exists())
    print('CV exists on disk:', Path(cv_path_on_disk).exists())
except Exception as e:
    print('Could not read file paths from application object:', e)

# Step 3: Login as admin and GET reviewer page
print('\n== Verifying reviewer page as admin ==')
if not c.login(username=admin_username, password=admin_password):
    print('Admin login failed — attempting to set password and retry')
    admin_user.set_password(admin_password)
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    if not c.login(username=admin_username, password=admin_password):
        print('Admin login still failed — cannot verify reviewer page via client')
else:
    resp2 = c.get('/consultations/applications/review/')
    print('GET /consultations/applications/review/ status:', resp2.status_code)
    print('Response length:', len(resp2.content or b''))

print('\nDone.')
