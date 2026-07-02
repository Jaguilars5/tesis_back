"""
Analiza los datos históricos disponibles para entrenar un modelo predictivo.
"""
import django, os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
django.setup()

from django.db.models import Count, Avg, Min, Max
from apps.academic.academic_period.infrastructure.models import AcademicPeriod
from apps.analytics.student_risk.infrastructure.models import StudentFeatureSnapshot, StudentRiskScore
from apps.students.models import Enrollment
from apps.grading.student_note.infrastructure.models import PeriodGradeSummary

print("=" * 70)
print("ANÁLISIS DE DATOS HISTÓRICOS PARA ENTRENAMIENTO ML")
print("=" * 70)

# 1. PERIODOS ACADÉMICOS
print("\n## 1. PERIODOS ACADÉMICOS")
periods = AcademicPeriod.objects.all().order_by('start_date')
print(f"Total períodos: {periods.count()}")
for p in periods:
    enroll_count = Enrollment.objects.filter(section__school_year=p.school_year).count()
    act_count = Enrollment.objects.filter(section__school_year=p.school_year, enrollment_status='ACT').count()
    ret_count = Enrollment.objects.filter(section__school_year=p.school_year, enrollment_status='RET').count()
    snap_count = StudentFeatureSnapshot.objects.filter(academic_period=p).count()
    risk_count = StudentRiskScore.objects.filter(academic_period=p).count()
    pgs_count = PeriodGradeSummary.objects.filter(academic_period=p).count()
    fail_count = PeriodGradeSummary.objects.filter(academic_period=p, is_failing=True).count()
    print(f"  [{p.id}] {p.name:30s} start={str(p.start_date):12s} end={str(p.end_date):12s} "
          f"enrolls={enroll_count:4d} act={act_count:3d} ret={ret_count:3d} "
          f"snaps={snap_count:4d} risks={risk_count:4d} "
          f"PGS={pgs_count:5d} failing_subjects={fail_count:4d}")

# 2. DISTRIBUCIÓN DE ESTADOS DE MATRÍCULA
print("\n## 2. ESTADOS DE MATRÍCULA GLOBAL")
status_dist = Enrollment.objects.values('enrollment_status').annotate(count=Count('id'))
for s in status_dist:
    print(f"  {s['enrollment_status']:5s}: {s['count']}")

# 3. ESTUDIANTES CON MÚLTIPLES PERÍODOS
print("\n## 3. ESTUDIANTES CON DATOS EN MÚLTIPLES PERÍODOS")
from django.db.models import Count as Cnt
students_with_periods = (
    StudentFeatureSnapshot.objects
    .values('enrollment__student_id')
    .annotate(num_periods=Cnt('academic_period', distinct=True))
    .order_by('-num_periods')
)
total_students = students_with_periods.count()
multi_period = students_with_periods.filter(num_periods__gte=2).count()
print(f"  Total estudiantes con snapshots: {total_students}")
print(f"  Estudiantes con >= 2 períodos: {multi_period} ({multi_period/total_students*100:.1f}%)")

period_dist = students_with_periods.values('num_periods').annotate(count=Cnt('id')).order_by('num_periods')
for d in period_dist:
    print(f"  {d['num_periods']} períodos: {d['count']} estudiantes")

# 4. DIFERENCIA ENTRE SNAPSHOT Y PGS (cuántos tienen ambos)
print("\n## 4. COBERTURA SNAPSHOT vs PERIODGRADESUMMARY")
for p in periods:
    snap_std = set(StudentFeatureSnapshot.objects.filter(academic_period=p).values_list('enrollment_id', flat=True))
    pgs_std = set(PeriodGradeSummary.objects.filter(academic_period=p).values_list('enrollment_id', flat=True))
    both = len(snap_std & pgs_std)
    only_snap = len(snap_std - pgs_std)
    only_pgs = len(pgs_std - snap_std)
    print(f"  Periodo {p.id} ({p.name:20s}): ambos={both:4d} solo_snapshot={only_snap:4d} solo_pgs={only_pgs:4d}")

# 5. DISTRIBUCIÓN DE is_failing POR PERÍODO
print("\n## 5. TASA DE REPROBACIÓN (is_failing) POR PERÍODO")
for p in periods:
    total = PeriodGradeSummary.objects.filter(academic_period=p).count()
    fail = PeriodGradeSummary.objects.filter(academic_period=p, is_failing=True).count()
    pct = fail/total*100 if total else 0
    print(f"  Periodo {p.id} ({p.name:20s}): {fail:4d}/{total:4d} failing ({pct:.1f}%)")

# 6. DISTRIBUCIÓN DE risk_label POR PERÍODO
print("\n## 6. DISTRIBUCIÓN DE risk_label POR PERÍODO")
for p in periods:
    labels = StudentRiskScore.objects.filter(academic_period=p).values('risk_label').annotate(count=Cnt('id'))
    if labels:
        total = sum(l['count'] for l in labels)
        parts = ' '.join(f"{l['risk_label']}={l['count']:3d}({l['count']/total*100:.0f}%)" for l in labels)
        print(f"  Periodo {p.id} ({p.name:20s}): total={total:4d}  {parts}")

# 7. DOWNTIME: cuántos abandonaron vs activos por período
print("\n## 7. DESERCIÓN (RET) POR PERÍODO")
for p in periods:
    act = Enrollment.objects.filter(section__school_year=p.school_year, enrollment_status='ACT').count()
    ret = Enrollment.objects.filter(section__school_year=p.school_year, enrollment_status='RET').count()
    total_sy = act + ret
    ret_pct = ret/total_sy*100 if total_sy else 0
    print(f"  Periodo {p.id} ({p.name:20s}): activos={act:4d} retirados={ret:4d} (%ret={ret_pct:.1f}%)")

# 8. ALUMNOS QUE REPROBARON y LUEGO SE RETIRARON
print("\n## 8. ALUMNOS QUE REPROBARON EN PERÍODO ANTERIOR (para predicción temporal)")
enrollments_with_prev = 0
for student_id in StudentFeatureSnapshot.objects.values_list('enrollment__student_id', flat=True).distinct():
    enrollments = Enrollment.objects.filter(student_id=student_id).order_by('enrollment_date')
    for e in enrollments:
        prev_pgs = PeriodGradeSummary.objects.filter(enrollment=e, is_failing=True).exists()
        if prev_pgs and e.enrollment_status == 'RET':
            enrollments_with_prev += 1
            break

print(f"  Estudiantes con reprobación previa + retiro: {enrollments_with_prev}")

# 9. RESUMEN GENERAL
print("\n" + "=" * 70)
print("## 9. RESUMEN PARA ENTRENAMIENTO")
pgs_total = PeriodGradeSummary.objects.count()
snap_total = StudentFeatureSnapshot.objects.count()
risk_total = StudentRiskScore.objects.count()
print(f"  PeriodGradeSummary.total: {pgs_total}")
print(f"  StudentFeatureSnapshot.total: {snap_total}")
print(f"  StudentRiskScore.total: {risk_total}")
print(f"  Estudiantes únicos con snapshots: {total_students}")
print(f"  Estudiantes con multi-período: {multi_period}")

# ¿Los snapshot se toman a inicio del periodo (features) y el PGS al final (target)?
print("\n## 10. ¿FECHAS SON ADECUADAS PARA PREDICCIÓN TEMPORAL?")
from datetime import date
for p in periods:
    snaps = StudentFeatureSnapshot.objects.filter(academic_period=p)
    if snaps.exists():
        snap_dates = snaps.aggregate(min_date=Min('calculated_at'), max_date=Max('calculated_at'))
        pgs = PeriodGradeSummary.objects.filter(academic_period=p)
        pgs_dates = pgs.aggregate(min_date=Min('calculated_at'), max_date=Max('calculated_at')) if pgs.exists() else {}
        print(f"  Periodo {p.id} ({p.name}):")
        print(f"    Snapshot fechas: {snap_dates['min_date']} a {snap_dates['max_date']}")
        print(f"    PGS fechas: {pgs_dates.get('min_date', 'N/A')} a {pgs_dates.get('max_date', 'N/A')}")
        print(f"    Periodo rango: {p.start_date} a {p.end_date}")
