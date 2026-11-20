import os
import numpy as np
import pandas as pd


def generate_attendance_data(num_students: int = 300, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    departments = ["CSE", "CSE-AI", "IT", "ECE"]
    subjects = [
        ("CS301", "Data Structures"),
        ("CS302", "Database Management Systems"),
        ("CS303", "Operating Systems"),
        ("CS304", "Computer Networks"),
        ("CS305", "Cloud Computing"),
    ]

    records = []
    for i in range(1, num_students + 1):
        student_id = f"24BCS{10000 + i}"
        name = f"Student_{i:03d}"
        dept = np.random.choice(departments, p=[0.45, 0.25, 0.15, 0.15])
        base_propensity = np.clip(np.random.normal(0.81, 0.11), 0.45, 0.99)

        for subj_code, subj_name in subjects:
            total_classes = int(np.random.randint(36, 45))
            prob = float(np.clip(base_propensity + np.random.normal(0, 0.05), 0.40, 1.0))
            attended = int(round(total_classes * prob))
            last_7_days_attended = int(np.random.binomial(5, prob))
            consecutive_absences = 0 if last_7_days_attended >= 4 else int(np.random.randint(1, 6))
            attendance_pct = round((attended / total_classes) * 100, 2)

            detention_risk = int(
                attendance_pct < 75.0 or (attendance_pct < 78.0 and consecutive_absences >= 3)
            )

            records.append({
                "student_id": student_id,
                "student_name": name,
                "department": dept,
                "subject_code": subj_code,
                "subject_name": subj_name,
                "total_classes": total_classes,
                "attended_classes": attended,
                "attendance_pct": attendance_pct,
                "last_7_days_attended": last_7_days_attended,
                "consecutive_absences": consecutive_absences,
                "detention_risk": detention_risk,
            })

    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "attendance_records.csv")
    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} records at {output_path}")
    return df


if __name__ == "__main__":
    generate_attendance_data()