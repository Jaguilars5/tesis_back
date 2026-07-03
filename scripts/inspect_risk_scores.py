"""Inspección rápida de puntajes ML y features del período activo."""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import django

django.setup()

from django.db.models import Avg, Min, Max, Count
from apps.academic.academic_period import AcademicPeriod
from apps.analytics.student_risk.infrastructure.models import (
    StudentFeatureSnapshot,
    StudentRiskScore,
    RiskScoringConfig,
)
from apps.analytics.student_risk.domain.risk_engine import score_to_risk_label
from apps.analytics.services.risk_scoring_config_service import RiskScoringConfigService

period = AcademicPeriod.objects.filter(is_active=True).first()
cfg = RiskScoringConfigService.get_effective()
print("=" * 70)
print("CONFIG MOTOR:", cfg.engine, "| preset:", getattr(cfg, "version_tag", ""))
if RiskScoringConfig.objects.exists():
    db = RiskScoringConfig.objects.first()
    print("  BD engine:", db.engine, "| preset:", db.preset)

if not period:
    print("No hay período activo")
    sys.exit(0)

print("PERIODO:", period.id, period.name)
print("=" * 70)

qs = StudentRiskScore.objects.filter(academic_period_id=period.id).select_related(
    "enrollment__student__user__person"
)
print(f"StudentRiskScore en período: {qs.count()}")

labels = {"rojo": 0, "amarillo": 0, "verde": 0}
buckets = {"0-39": 0, "40-69": 0, "70-100": 0}
unique_scores = set()

for s in qs:
    sc = float(s.risk_score)
    unique_scores.add(round(sc, 2))
    lab = score_to_risk_label(sc)
    labels[lab] += 1
    if sc < 40:
        buckets["0-39"] += 1
    elif sc < 70:
        buckets["40-69"] += 1
    else:
        buckets["70-100"] += 1

print("\nDistribución por etiqueta (derivada del puntaje):")
for k, v in labels.items():
    print(f"  {k}: {v}")

print("\nDistribución por rango de puntaje:")
for k, v in buckets.items():
    print(f"  {k}: {v}")

if qs.exists():
    agg = qs.aggregate(min=Min("risk_score"), max=Max("risk_score"), avg=Avg("risk_score"))
    print(f"\nPuntaje min/avg/max: {agg['min']} / {round(float(agg['avg']), 2)} / {agg['max']}")
    print(f"Puntajes únicos ({len(unique_scores)}): {sorted(unique_scores)}")

print("\n--- Muestra estudiantes con score intermedio (40-69) ---")
mid = [s for s in qs if 40 <= float(s.risk_score) < 70]
if not mid:
    print("  (ninguno)")
else:
    for s in mid[:10]:
        name = str(s.enrollment)
        print(f"  {name}: {s.risk_score}")

print("\n--- Muestra 5 alto riesgo ---")
for s in qs.order_by("-risk_score")[:5]:
    print(f"  {s.enrollment}: score={s.risk_score} label={score_to_risk_label(float(s.risk_score))}")

print("\n--- Muestra 5 bajo riesgo ---")
for s in qs.order_by("risk_score")[:5]:
    print(f"  {s.enrollment}: score={s.risk_score} label={score_to_risk_label(float(s.risk_score))}")

snap_qs = StudentFeatureSnapshot.objects.filter(academic_period_id=period.id)
print(f"\nSnapshots en período: {snap_qs.count()}")
if snap_qs.exists():
    snap_agg = snap_qs.aggregate(
        att=Avg("attendance_rate"),
        form=Avg("formative_avg_normalized"),
        summ=Avg("summative_avg_normalized"),
        fail=Avg("failing_subjects_count"),
    )
    print(
        "Promedios features:",
        f"asistencia={round(float(snap_agg['att'] or 0), 2)}",
        f"formativo={round(float(snap_agg['form'] or 0), 2)}",
        f"reprobadas={round(float(snap_agg['fail'] or 0), 2)}",
    )

print("\n--- Snapshots training total ---")
print("Total snapshots históricos:", StudentFeatureSnapshot.objects.count())
