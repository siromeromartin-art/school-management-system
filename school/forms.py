from django import forms
from .models import School, AttendanceDayConfiguration

class SchoolSettingsForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ["name", "address", "phone", "email", "logo_url", "active"]

class AttendanceSettingsForm(forms.ModelForm):
    class Meta:
        model = AttendanceDayConfiguration
        fields = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
