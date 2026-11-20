import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split


class AttendanceRiskPredictor:
    def __init__(self):
        self.features = [
            "attendance_pct",
            "last_7_days_attended",
            "consecutive_absences",
            "total_classes",
        ]
        self.model = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)
        self.is_trained = False

    def train(self, df: pd.DataFrame) -> dict:
        X = df[self.features]
        y = df["detention_risk"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True

        preds = self.model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        report = classification_report(y_test, preds, output_dict=True)
        cm = confusion_matrix(y_test, preds)
        importances = dict(zip(self.features, self.model.feature_importances_))

        return {
            "accuracy": round(acc * 100, 2),
            "precision_risk": round(report["1"]["precision"] * 100, 2),
            "recall_risk": round(report["1"]["recall"] * 100, 2),
            "f1_risk": round(report["1"]["f1-score"] * 100, 2),
            "confusion_matrix": cm.tolist(),
            "feature_importances": importances,
        }

    def predict_risk_prob(self, df: pd.DataFrame) -> pd.Series:
        if not self.is_trained:
            raise RuntimeError("Model must be trained before calling predict_risk_prob().")
        probs = self.model.predict_proba(df[self.features])[:, 1]
        return pd.Series(probs, index=df.index)

    @staticmethod
    def assign_risk_tier(attendance_pct: float, consecutive_absences: int) -> str:
        if attendance_pct < 65.0:
            return "CRITICAL"
        if attendance_pct < 75.0:
            return "HIGH_RISK"
        if attendance_pct < 80.0 and consecutive_absences >= 3:
            return "WARNING"
        return "SAFE"

    @staticmethod
    def generate_mentor_alert(row: pd.Series) -> str:
        tier = AttendanceRiskPredictor.assign_risk_tier(
            row["attendance_pct"], row["consecutive_absences"]
        )
        if tier == "CRITICAL":
            return (
                f"[CRITICAL] {row['student_name']} ({row['student_id']}) is at "
                f"{row['attendance_pct']}% in {row['subject_name']} with a "
                f"{row['consecutive_absences']}-class absence streak. Immediate parent & HOD notice required."
            )
        if tier == "HIGH_RISK":
            return (
                f"[HIGH RISK] {row['student_name']} ({row['student_id']}) dropped below 75% "
                f"({row['attendance_pct']}%) in {row['subject_name']}. Schedule mandatory mentor counseling."
            )
        if tier == "WARNING":
            return (
                f"[WARNING] {row['student_name']} ({row['student_id']}) is borderline at "
                f"{row['attendance_pct']}% with {row['consecutive_absences']} recent absences. Issue early warning."
            )
        return f"[SAFE] {row['student_name']} maintains satisfactory attendance ({row['attendance_pct']}%)."