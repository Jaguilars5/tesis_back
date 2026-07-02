"""
Debug: calcular score para un perfil específico de estudiante.
"""
import django, os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
django.setup()

import joblib
import pandas as pd
import numpy as np
from apps.analytics.ml.features import MODEL_PATH, TRAIN_FEATURES, _to_number

artifact = joblib.load(MODEL_PATH)
model = artifact['model']
scaler = artifact['scaler']
features = artifact.get('features', TRAIN_FEATURES)

print("Modelo cargado:", type(model).__name__)
print("Features esperadas:", features)
print()

# Perfil del estudiante (según datos proporcionados)
perfil = {
    "attendance_rate": 90.62,
    "consecutive_absences_max": 1,
    "tardiness_count": 12,
    "justified_absences": 10,
    "unjustified_absences": 5,
    "formative_avg_normalized": 8.25,
    "summative_avg_normalized": 8.25,
    "grade_trend_slope": -0.03,
    "conduct_score": 10.00,
    "severe_incidents_count": 0,
    "family_notified_ratio": 0.0,
    "prev_period_avg_grade": 0.0,
    "age_grade_gap": 0,
    "is_repeat": 0.0,
    "has_special_needs": 0.0,
}

feature_row = [perfil[col] for col in features]
X = pd.DataFrame([feature_row], columns=features)
X_scaled = scaler.transform(X)

proba = model.predict_proba(X_scaled)[0]
print(f"Probabilidad clase 0 (aprobado): {proba[0]:.4f} ({proba[0]*100:.2f}%)")
print(f"Probabilidad clase 1 (reprobado): {proba[1]:.4f} ({proba[1]*100:.2f}%)")
print(f"Score final: {round(proba[1]*100, 2)}")

print("\n--- Features escaladas ---")
scaled_df = pd.DataFrame(X_scaled, columns=features)
for col in features:
    print(f"  {col:30s}: original={perfil[col]:8.2f}  escalado={scaled_df[col].values[0]:+8.4f}")

print("\n--- Coeficientes del modelo ---")
coefs = {features[i]: model.coef_[0][i] for i in range(len(features))}
sorted_coefs = sorted(coefs.items(), key=lambda x: abs(x[1]), reverse=True)
for name, coef in sorted_coefs:
    direction = "↑riesgo" if coef > 0 else "↓riesgo"
    print(f"  {name:30s}: {coef:+8.4f}  ({direction})")

print(f"\n--- Contribución de cada feature al score bruto ---")
logit = model.intercept_[0]
print(f"  Intercepto: {logit:.4f}")
for col in features:
    contrib = model.coef_[0][features.index(col)] * scaled_df[col].values[0]
    logit += contrib
    print(f"  {col:30s}: {contrib:+8.4f}")
print(f"\n  Logit total: {logit:.4f}")
print(f"  P(reprobado) = 1 / (1 + e^(-{logit:.4f})) = {1/(1+np.exp(-logit)):.4f}")
