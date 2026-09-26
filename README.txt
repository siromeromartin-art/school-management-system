NEW SCHOOL MANAGEMENT SYSTEM - V2

This is a fresh Django project. It is not the old Brightway project.

Included:
- Multi-school data model
- School settings
- Users and Groups through Django Administration
- Teacher profiles with multiple class assignments
- Parent profiles
- Two parent accounts/links per student
- Academic years and configurable semesters/terms
- Classes and subjects per class
- CAT + Exam marks
- Automatic totals, averages, grades and class-only ranking
- Ties share the same rank
- Configurable attendance days (Mon-Sun)
- Attendance
- Fees, payments and live balance
- Report cards
- Parent view of children and fee balances
- Mobile-friendly basic interface
- Django admin for complete data administration

INSTALLATION
1. Stop the currently running Django server with CTRL+C.
2. Back up your existing school_system_new folder if you want to keep it.
3. Replace the contents of school_system_new with the contents of this ZIP.
4. Open Command Prompt in school_system_new.
5. Run:
   python -m pip install -r requirements.txt
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver 8001
6. Open http://127.0.0.1:8001/

IMPORTANT
The new system starts with a clean database. Your old Brightway project is not changed.
