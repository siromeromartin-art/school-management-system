from datetime import date
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from .forms import SchoolSettingsForm, AttendanceSettingsForm
from .services import class_rankings, grade_for

def user_school(user):
    if hasattr(user, "teacher_profile"):
        return user.teacher_profile.school
    if hasattr(user, "parent_profile"):
        return user.parent_profile.school
    return School.objects.filter(active=True).first()

@login_required
def dashboard(request):
    school = user_school(request.user)
    if not school:
        school = School.objects.create(name="My School")
        AttendanceDayConfiguration.objects.create(school=school)
    context = {
        "school": school,
        "students": Student.objects.filter(school=school, active=True).count(),
        "classes": SchoolClass.objects.filter(school=school, active=True).count(),
        "teachers": TeacherProfile.objects.filter(school=school, active=True).count(),
        "parents": ParentProfile.objects.filter(school=school, active=True).count(),
        "subjects": Subject.objects.filter(school=school, active=True).count(),
        "years": AcademicYear.objects.filter(school=school).count(),
    }
    if hasattr(request.user, "parent_profile"):
        children = Student.objects.filter(
            Q(parent_one=request.user.parent_profile) | Q(parent_two=request.user.parent_profile),
            school=school, active=True
        ).distinct()
        context["children"] = children
    return render(request, "school/dashboard.html", context)

@login_required
def students(request):
    school = user_school(request.user)
    qs = Student.objects.filter(school=school, active=True).select_related("parent_one__user","parent_two__user")
    if hasattr(request.user, "teacher_profile"):
        assigned = request.user.teacher_profile.assigned_classes.all()
        qs = qs.filter(enrollments__school_class__in=assigned, enrollments__academic_year__is_current=True).distinct()
    if hasattr(request.user, "parent_profile"):
        p = request.user.parent_profile
        qs = qs.filter(Q(parent_one=p) | Q(parent_two=p)).distinct()
    return render(request, "school/students.html", {"school": school, "students": qs})

@login_required
def student_detail(request, pk):
    school = user_school(request.user)
    student = get_object_or_404(Student, pk=pk, school=school)
    if hasattr(request.user, "parent_profile"):
        p = request.user.parent_profile
        if student.parent_one_id != p.id and student.parent_two_id != p.id:
            return redirect("students")
    enrollments = student.enrollments.select_related("academic_year","school_class").order_by("-academic_year__start_date")
    return render(request, "school/student_detail.html", {"school": school, "student": student, "enrollments": enrollments})

@login_required
def setup(request):
    school = user_school(request.user)
    if hasattr(request.user, "parent_profile"):
        return redirect("dashboard")
    config, _ = AttendanceDayConfiguration.objects.get_or_create(school=school)
    if request.method == "POST":
        sf = SchoolSettingsForm(request.POST, instance=school)
        af = AttendanceSettingsForm(request.POST, instance=config)
        if sf.is_valid() and af.is_valid():
            sf.save(); af.save()
            messages.success(request, "School settings saved.")
            return redirect("setup")
    else:
        sf = SchoolSettingsForm(instance=school)
        af = AttendanceSettingsForm(instance=config)
    return render(request, "school/setup.html", {"school": school, "school_form": sf, "attendance_form": af})

@login_required
def attendance(request):
    school = user_school(request.user)
    enrollments = Enrollment.objects.filter(
        academic_year__is_current=True, student__school=school, active=True
    ).select_related("student","school_class")
    if hasattr(request.user, "teacher_profile"):
        enrollments = enrollments.filter(school_class__in=request.user.teacher_profile.assigned_classes.all())
    if hasattr(request.user, "parent_profile"):
        p = request.user.parent_profile
        enrollments = enrollments.filter(Q(student__parent_one=p)|Q(student__parent_two=p))
    selected = request.GET.get("enrollment")
    chosen = enrollments.filter(pk=selected).first() if selected else enrollments.first()
    selected_date = request.GET.get("date") or date.today().isoformat()
    if request.method == "POST" and chosen:
        status = request.POST.get("status", "Present")
        remarks = request.POST.get("remarks","")
        Attendance.objects.update_or_create(
            enrollment=chosen, date=request.POST.get("date") or date.today(),
            defaults={"status":status,"remarks":remarks}
        )
        messages.success(request, "Attendance saved.")
        return redirect(f"/attendance/?enrollment={chosen.id}&date={request.POST.get('date')}")
    record = Attendance.objects.filter(enrollment=chosen, date=selected_date).first() if chosen else None
    return render(request, "school/attendance.html", {
        "school":school,"enrollments":enrollments,"chosen":chosen,
        "selected_date":selected_date,"record":record,
        "attendance_days": school.attendance_config.enabled_weekdays() if hasattr(school,"attendance_config") else {},
    })

@login_required
def fees(request):
    school = user_school(request.user)
    accounts = FeeAccount.objects.filter(enrollment__student__school=school).select_related(
        "enrollment__student","enrollment__school_class","enrollment__academic_year"
    )
    if hasattr(request.user, "parent_profile"):
        p=request.user.parent_profile
        accounts=accounts.filter(Q(enrollment__student__parent_one=p)|Q(enrollment__student__parent_two=p)).distinct()
    return render(request, "school/fees.html", {"school":school,"accounts":accounts})

@login_required
def marks(request):
    school = user_school(request.user)
    periods = AcademicPeriod.objects.filter(academic_year__school=school).select_related("academic_year")
    enrollments = Enrollment.objects.filter(student__school=school, active=True).select_related("student","school_class")
    if hasattr(request.user,"teacher_profile"):
        enrollments=enrollments.filter(school_class__in=request.user.teacher_profile.assigned_classes.all())
    if hasattr(request.user,"parent_profile"):
        p=request.user.parent_profile
        enrollments=enrollments.filter(Q(student__parent_one=p)|Q(student__parent_two=p)).distinct()
    chosen_period = periods.filter(pk=request.GET.get("period")).first() or periods.first()
    chosen_enrollment = enrollments.filter(pk=request.GET.get("enrollment")).first() or enrollments.first()
    rows=[]
    if chosen_period and chosen_enrollment:
        subjects=Subject.objects.filter(class_subjects__school_class=chosen_enrollment.school_class, class_subjects__active=True, active=True).distinct()
        for s in subjects:
            m=Mark.objects.filter(enrollment=chosen_enrollment, subject=s, academic_period=chosen_period).first()
            total=(m.total if m else Decimal("0"))
            rows.append({"subject":s,"mark":m,"total":total,"grade":grade_for(school,total)})
    return render(request,"school/marks.html",{"school":school,"periods":periods,"enrollments":enrollments,"chosen_period":chosen_period,"chosen_enrollment":chosen_enrollment,"rows":rows})

@login_required
def report_card(request, enrollment_id):
    school=user_school(request.user)
    enrollment=get_object_or_404(Enrollment,pk=enrollment_id,student__school=school)
    if hasattr(request.user,"parent_profile"):
        p=request.user.parent_profile
        if enrollment.student.parent_one_id != p.id and enrollment.student.parent_two_id != p.id:
            return redirect("students")
    periods=list(enrollment.academic_year.periods.all())
    data=[]
    for period in periods:
        rankings=class_rankings(enrollment,period)
        marks=list(Mark.objects.filter(enrollment=enrollment,academic_period=period).select_related("subject"))
        total=sum((m.total for m in marks),Decimal("0"))
        avg=total/len(marks) if marks else Decimal("0")
        data.append({"period":period,"marks":marks,"total":total,"average":avg,"rank":rankings.get(enrollment.id,{}).get("rank","-")})
    attendance_records=list(enrollment.attendance.all())
    return render(request,"school/report_card.html",{"school":school,"enrollment":enrollment,"period_data":data,"attendance":attendance_records})
