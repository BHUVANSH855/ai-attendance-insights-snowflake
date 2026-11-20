import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.generate_dataset import fetch_real_attendance_data
from src.risk_model import AttendanceRiskPredictor


def run_evaluation():
    csv_path = os.path.join("data", "attendance_records.csv")
    if not os.path.exists(csv_path):
        df = fetch_real_attendance_data()
    else:
        df = pd.read_csv(csv_path)

    predictor = AttendanceRiskPredictor()
    metrics = predictor.train(df)

    os.makedirs("screenshots", exist_ok=True)

    # 1. Feature Importance Chart
    plt.figure(figsize=(8, 4.5))
    features = list(metrics["feature_importances"].keys())
    scores = list(metrics["feature_importances"].values())
    plt.barh(features, scores, color="#2b6cb0")
    plt.xlabel("Relative Importance Score")
    plt.title("Random Forest Feature Importance - Detention Risk Prediction")
    plt.tight_layout()
    plt.savefig("screenshots/eval_feature_importance.png", dpi=300)
    plt.close()

    # 2. Confusion Matrix Plot
    cm = np.array(metrics["confusion_matrix"])
    plt.figure(figsize=(5.5, 4.5))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title(f"Confusion Matrix (Accuracy: {metrics['accuracy']}%)")
    plt.colorbar()
    classes = ["Safe (0)", "At-Risk (1)"]
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes)
    plt.yticks(tick_marks, classes)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, format(cm[i, j], "d"), ha="center", va="center",
                     color="white" if cm[i, j] > cm.max() / 2 else "black")
    plt.ylabel("Actual Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    plt.savefig("screenshots/eval_confusion_matrix.png", dpi=300)
    plt.close()

    # 3. Department-Wise Attendance Distribution
    plt.figure(figsize=(8, 4.5))
    dept_avg = df.groupby("department")["attendance_pct"].mean().sort_values()
    plt.bar(dept_avg.index, dept_avg.values, color=["#e53e3e", "#dd6b20", "#3182ce", "#38a169"])
    plt.axhline(75.0, color="red", linestyle="--", label="75% Minimum Threshold")
    plt.ylim(60, 100)
    plt.ylabel("Average Attendance (%)")
    plt.title("Department-Wise Mean Attendance vs. 75% Eligibility Threshold")
    plt.legend()
    plt.tight_layout()
    plt.savefig("screenshots/eval_dept_attendance.png", dpi=300)
    plt.close()

    print("=== Real Dataset Evaluation Metrics Summary ===")
    print(f"Records  : {len(df)}")
    print(f"Accuracy : {metrics['accuracy']}%")
    print(f"Precision: {metrics['precision_risk']}%")
    print(f"Recall   : {metrics['recall_risk']}%")
    print(f"F1-Score : {metrics['f1_risk']}%")
    print("Saved 3 evaluation plots into screenshots/.")


if __name__ == "__main__":
    run_evaluation()