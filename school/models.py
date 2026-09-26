from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class School(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    logo_url = models.URLField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class AcademicYear(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="academic_years")
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(fields=["school", "name"], name="unique_school_year")
        ]

    def __str__(self):
        return f"{self.school.name} - {self.name}"

class AcademicPeriod(models.Model):
    SEMESTER = "semester"
    TERM = "term"
    PERIOD_TYPES = [(SEMESTER, "Semester"), (TERM, "Term")]
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="periods")
    name = models.CharField(max_length=50)
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPES)
    number = models.PositiveIntegerField(default=1)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(fields=["academic_year", "number"], name="unique_period_number")
        ]

    def __str__(self):
        return f"{self.academic_year.name} - {self.name}"

class SchoolClass(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="classes")
    name = models.CharField(max_length=100)
    level = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["level", "name"]
        constraints = [
            models.UniqueConstraint(fields=["school", "name"], name="unique_school_class")
        ]

    def __str__(self):
        return self.name

class Subject(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["school", "name"], name="unique_school_subject")
        ]

    def __str__(self):
        return self.name

class ClassSubject(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="class_subjects")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["school_class", "subject"], name="unique_class_subject")
        ]

    def __str__(self):
        return f"{self.school_class} - {self.subject}"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="teachers")
    phone = models.CharField(max_length=50, blank=True)
    assigned_classes = models.ManyToManyField(SchoolClass, blank=True, related_name="teachers")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="parent_profile")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="parents")
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="students")
    admission_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    GENDER = [("M", "Male"), ("F", "Female"), ("O", "Other")]
    gender = models.CharField(max_length=1, choices=GENDER, blank=True)
    parent_one = models.ForeignKey(ParentProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name="children_as_parent_one")
    parent_two = models.ForeignKey(ParentProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name="children_as_parent_two")
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["first_name", "last_name"]
        constraints = [
            models.UniqueConstraint(fields=["school", "admission_number"], name="unique_school_admission")
        ]

    @property
    def full_name(self):
        return " ".join(x for x in [self.first_name, self.middle_name, self.last_name] if x).strip()

    def __str__(self):
        return f"{self.full_name} ({self.admission_number})"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="enrollments")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="enrollments")
    admission_date = models.DateField()
    promoted = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "academic_year"], name="unique_student_year")
        ]

    def __str__(self):
        return f"{self.student} - {self.school_class} - {self.academic_year.name}"

class Mark(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="marks")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    academic_period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE, related_name="marks")
    cat = models.DecimalField(max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    exam = models.DecimalField(max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["enrollment", "subject", "academic_period"], name="unique_mark")
        ]

    @property
    def total(self):
        return self.cat + self.exam

    def __str__(self):
        return f"{self.enrollment.student.full_name} - {self.subject} - {self.academic_period}"

class GradeScale(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="grade_scales")
    grade = models.CharField(max_length=10)
    minimum = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    maximum = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    remark = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-minimum"]
        constraints = [
            models.UniqueConstraint(fields=["school", "grade"], name="unique_school_grade")
        ]

    def __str__(self):
        return f"{self.grade}: {self.minimum}-{self.maximum}"

class AttendanceDayConfiguration(models.Model):
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name="attendance_config")
    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True)
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)

    def enabled_weekdays(self):
        return {
            0: self.monday, 1: self.tuesday, 2: self.wednesday,
            3: self.thursday, 4: self.friday, 5: self.saturday, 6: self.sunday
        }

    def __str__(self):
        return f"Attendance days - {self.school.name}"

class Attendance(models.Model):
    STATUS = [("Present", "Present"), ("Absent", "Absent"), ("Late", "Late"), ("Excused", "Excused")]
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="attendance")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["enrollment", "date"], name="unique_attendance_date")
        ]
        ordering = ["-date"]

class ReportRemark(models.Model):
    ROLE = [("teacher", "Class Teacher"), ("director", "Director"), ("parent", "Parent")]
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="report_remarks")
    academic_period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE)
    text = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["enrollment", "academic_period", "role"], name="unique_report_remark")
        ]

class FeeAccount(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name="fee_account")
    total_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    @property
    def paid(self):
        return self.payments.aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

    @property
    def balance(self):
        return self.total_fees - self.paid

    def __str__(self):
        return f"Fees - {self.enrollment.student.full_name}"

class FeePayment(models.Model):
    METHOD = [("Cash", "Cash"), ("Bank", "Bank"), ("Mobile Money", "Mobile Money"), ("Other", "Other")]
    fee_account = models.ForeignKey(FeeAccount, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    payment_date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    method = models.CharField(max_length=30, choices=METHOD, default="Cash")
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-payment_date", "-id"]
