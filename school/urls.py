from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("dashboard/", views.dashboard, name="dashboard2"),
    path("students/", views.students, name="students"),
    path("students/<int:pk>/", views.student_detail, name="student_detail"),
    path("marks/", views.marks, name="marks"),
    path("attendance/", views.attendance, name="attendance"),
    path("fees/", views.fees, name="fees"),
    path("report/<int:enrollment_id>/", views.report_card, name="report_card"),
    path("setup/", views.setup, name="setup"),
]
