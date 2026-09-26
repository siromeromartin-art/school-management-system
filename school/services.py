from collections import defaultdict
from decimal import Decimal
from .models import Mark, GradeScale, Enrollment

def grade_for(school, total):
    for g in GradeScale.objects.filter(school=school).order_by("-minimum"):
        if g.minimum <= total <= g.maximum:
            return g
    return None

def class_rankings(enrollment, period):
    """Rank students within the same class and academic year; ties share a position."""
    enrollments = Enrollment.objects.filter(
        academic_year=enrollment.academic_year,
        school_class=enrollment.school_class,
        active=True,
    ).select_related("student")
    scores = []
    for e in enrollments:
        totals = list(Mark.objects.filter(enrollment=e, academic_period=period).values_list("cat", "exam"))
        total = sum((Decimal(a) + Decimal(b) for a, b in totals), Decimal("0"))
        average = total / len(totals) if totals else Decimal("0")
        scores.append((e, average))
    scores.sort(key=lambda x: (-x[1], x[0].student.full_name.lower()))
    result = {}
    last_score = None
    rank = 0
    for idx, (e, score) in enumerate(scores, 1):
        if last_score is None or score != last_score:
            rank = idx
        result[e.id] = {"rank": rank, "average": score}
        last_score = score
    return result
