from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import *

admin.site.site_header = "School Management System"
admin.site.site_title = "School Management System"
admin.site.index_title = "Administration"

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display=("name","phone","email","active")
    search_fields=("name","phone","email")

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display=("name","school","start_date","end_date","is_current")
    list_filter=("school","is_current")

@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display=("name","academic_year","period_type","number","start_date","end_date")
    list_filter=("academic_year","period_type")

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display=("name","school","level","active")
    list_filter=("school","active")

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display=("name","code","school","active")
    list_filter=("school","active")

@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display=("school_class","subject","active")
    list_filter=("school_class","subject","active")

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display=("user","school","phone","active")
    list_filter=("school","active")
    filter_horizontal=("assigned_classes",)

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display=("user","school","phone","active")
    list_filter=("school","active")
    search_fields=("user__username","user__first_name","user__last_name","phone")

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display=("admission_number","full_name","school","parent_one","parent_two","active")
    list_filter=("school","gender","active")
    search_fields=("admission_number","first_name","middle_name","last_name")
    autocomplete_fields=("parent_one","parent_two")

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display=("student","academic_year","school_class","admission_date","promoted","active")
    list_filter=("academic_year","school_class","promoted","active")
    autocomplete_fields=("student",)

@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display=("enrollment","subject","academic_period","cat","exam","total_display")
    list_filter=("academic_period","subject")
    def total_display(self,obj): return obj.total
    total_display.short_description="Total"

@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    list_display=("school","grade","minimum","maximum","remark")
    list_filter=("school",)

@admin.register(AttendanceDayConfiguration)
class AttendanceDayConfigurationAdmin(admin.ModelAdmin):
    list_display=("school","monday","tuesday","wednesday","thursday","friday","saturday","sunday")

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display=("enrollment","date","status","remarks")
    list_filter=("date","status")

@admin.register(ReportRemark)
class ReportRemarkAdmin(admin.ModelAdmin):
    list_display=("enrollment","academic_period","role","text")
    list_filter=("academic_period","role")

@admin.register(FeeAccount)
class FeeAccountAdmin(admin.ModelAdmin):
    list_display=("enrollment","total_fees","paid_display","balance_display")
    def paid_display(self,obj): return obj.paid
    def balance_display(self,obj): return obj.balance
    paid_display.short_description="Paid"
    balance_display.short_description="Balance"

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display=("fee_account","amount","payment_date","method","reference")
    list_filter=("method","payment_date")

# Users and Groups remain available under Authentication and Authorization.
