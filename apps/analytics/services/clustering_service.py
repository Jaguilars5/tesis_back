import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from ..models import StudentFeatureSnapshot, DashboardMetric


class StudentClusteringService:

    CLUSTER_LABELS = {
        0: "Bajo riesgo - Buen rendimiento",
        1: "Riesgo moderado - Asistencia irregular",
        2: "Alto riesgo - Múltiples factores",
        3: "Riesgo conductual - Buen rendimiento",
    }

    @classmethod
    def cluster_students(cls, academic_period_id, n_clusters=4):
        snapshots = StudentFeatureSnapshot.objects.filter(
            academic_period_id=academic_period_id
        )

        features = snapshots.values_list(
            "attendance_rate", "formative_avg_normalized", "summative_avg_normalized",
            "failing_subjects_count", "conduct_score", "severe_incidents_count",
        )

        X = np.array(list(features))
        if len(X) < n_clusters:
            return {"total_clusters": 0, "distribution": {}, "error": "Datos insuficientes"}

        X_scaled = StandardScaler().fit_transform(X)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
        clusters = kmeans.fit_predict(X_scaled)

        for i, snapshot in enumerate(snapshots):
            DashboardMetric.objects.update_or_create(
                academic_period_id=academic_period_id,
                section=snapshot.enrollment.section,
                metric_type="student_cluster",
                defaults={
                    "metric_value": {
                        "cluster": int(clusters[i]),
                        "label": cls.CLUSTER_LABELS.get(int(clusters[i]), "Desconocido"),
                        "centroid_distance": float(
                            np.linalg.norm(X_scaled[i] - kmeans.cluster_centers_[clusters[i]])
                        ),
                    }
                },
            )

        unique, counts = np.unique(clusters, return_counts=True)
        return {
            "total_clusters": n_clusters,
            "distribution": {
                cls.CLUSTER_LABELS.get(int(c), f"Cluster {c}"): int(n)
                for c, n in zip(unique, counts)
            },
        }
